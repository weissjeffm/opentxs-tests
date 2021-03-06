from pyopentxs import ReturnValueError, is_message_success, otme, server
import opentxs
from datetime import datetime
from multimethods import singledispatch


class Cheque:
    def __init__(self, server_id, cheque_amount, valid_from, valid_to, sender_account,
                 sender_nym, cheque_memo, recipient_nym):
        self.server_id = server_id or server.only_id()
        self.cheque_amount = cheque_amount
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.sender_account = sender_account
        self.sender_nym = sender_nym
        self.cheque_memo = cheque_memo
        self.recipient_nym = recipient_nym
        self._body = None  # prepared cheque returned by server

    def write(self):
        """
        Prepare cheque
        valid_from and valid_to are datetime objects
        """
        otme.make_sure_enough_trans_nums(10, self.server_id, self.sender_nym._id)

        secs_since_1970 = lambda d: int((d - datetime(1970, 1, 1)).total_seconds())
        self._body = opentxs.OTAPI_Wrap_WriteCheque(
            self.server_id,
            self.cheque_amount,
            secs_since_1970(self.valid_from),
            secs_since_1970(self.valid_to),
            self.sender_account._id,
            self.sender_nym._id,
            self.cheque_memo,
            self.recipient_nym._id)
        return self._body

    def deposit(self, depositor_nym, depositor_account):
        '''Deposit the cheque, getting a written copy from the server first if
        we don't have one.  The reason for having both the nym and
        account is that the server asks for both and we can test its
        behavior when they don't match.

        '''
        if not self._body:
            self.write()
        result = otme.deposit_cheque(self.server_id, depositor_nym._id,
                                     depositor_account._id, self._body)
        print("Deposit: %s" % result)
        assert is_message_success(result)
        # otme.accept_inbox_items(depositor_account._id, 0, "")
        return result

    def cancel(self):
        outpayments_count = opentxs.OTAPI_Wrap_GetNym_OutpaymentsCount(self.sender_account.nym._id)
        for i in range(outpayments_count):
            body = opentxs.OTAPI_Wrap_GetNym_OutpaymentsContentsByIndex(
                self.sender_nym._id, i)
            if body == self._body:
                # found it, now cancel it.
                result = otme.cancel_outgoing_payments(
                    self.sender_nym._id, self.sender_account._id, str(i))
                assert result, "Unable to cancel cheque {}".format(self)
                return
        raise IndexError("Cheque {} not found in outpayments, can't cancel".format(self))


class Voucher:
    def __init__(self, server_id, amount, sender_account, sender_nym, memo, recipient_nym):
        self.server_id = server_id or server.only_id()
        self.amount = amount
        self.sender_account = sender_account
        self.sender_nym = sender_nym
        self.memo = memo
        self.recipient_nym = recipient_nym
        self._body = None

    def withdraw(self):
        """
        Withdraw voucher
        """
        message = otme.withdraw_voucher(self.server_id, self.sender_nym._id,
                                        self.sender_account._id,
                                        self.recipient_nym._id, self.memo, self.amount)
        assert is_message_success(message)
        ledger = opentxs.OTAPI_Wrap_Message_GetLedger(message)
        transaction = opentxs.OTAPI_Wrap_Ledger_GetTransactionByIndex(
            self.server_id, self.sender_nym._id, self.sender_account._id, ledger, 0)
        output = opentxs.OTAPI_Wrap_Transaction_GetVoucher(self.server_id, self.sender_nym._id,
                                                           self.sender_account._id, transaction)

        if output == '':
            raise ReturnValueError(output)

        self._body = output

        # save a copy for myself in outpayments box, so i can cancel later
        otme.send_user_payment(self.server_id, self.sender_nym._id, self.sender_nym._id, output)

        return output

    def deposit(self, depositor_nym, depositor_account):
        '''Deposit the cheque, getting a written copy from the server first if we don't have one.'''
        deposit = otme.deposit_cheque(self.server_id, depositor_nym._id, depositor_account._id,
                                      self._body)
        assert is_message_success(deposit)
        return deposit

    def cancel(self):
        outpayments_count = opentxs.OTAPI_Wrap_GetNym_OutpaymentsCount(self.sender_account.nym._id)
        for i in range(outpayments_count):
            body = opentxs.OTAPI_Wrap_GetNym_OutpaymentsContentsByIndex(
                self.sender_nym._id, i)
            if body == self._body:
                # found it, now cancel it.
                result = otme.cancel_outgoing_payments(
                    self.sender_nym._id, self.sender_account._id, str(i))
                assert result, "Unable to cancel voucher {}".format(self)
                return
        raise IndexError("Voucher {} not found in {} outpayments, can't cancel".format(
            self, outpayments_count))


def send_transfer(server_id=None, acct_from=None, acct_to=None, note=None, amount=None):
    server_id = server_id or server.only_id()
    print("transferring {} from {} to {} on {}".format(amount, acct_from, acct_to, server_id))
    message = otme.send_transfer(server_id, acct_from.nym._id, acct_from._id,
                                 acct_to._id, amount, note)
    assert is_message_success(message)
    # accept all inbox items in target account
    assert otme.accept_inbox_items(acct_to._id, 0, "")
    return message


@singledispatch
def write(item):
    item.write()


@write.method(Voucher)
def write_voucher(v):
    v.withdraw()


@singledispatch
def transfer(item, source_acct, target_acct):
    '''generic function to transfer something from source to target. '''
    raise NotImplementedError("Don't know how to transfer {}'".format(item))


@transfer.method(int)
def transfer_int(amount, source_acct, target_acct):
    '''Send amount via direct transfer'''
    return send_transfer(
        source_acct.server_id, source_acct, target_acct, "withdraw", amount)


@transfer.method(Cheque)
def transfer_cheque(cheque, source_acct, target_acct):
    '''Transfer funds by writing and depositing a cheque'''
    cheque.write()
    return cheque.deposit(target_acct.nym, target_acct)


@transfer.method(Voucher)
def transfer_voucher(voucher, source_acct, target_acct):
    '''Transfer funds by creating and depositing a voucher'''
    voucher.withdraw()
    return voucher.deposit(target_acct.nym, target_acct)
