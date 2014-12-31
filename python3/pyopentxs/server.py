import opentxs

# the ids of the notaries we know we should be able to contact
active = []


def add(nym_id, contract):
    '''Create a server contract with the given nym_id and the contract
    contents.'''
    contract_id = opentxs.OTAPI_Wrap_CreateServerContract(nym_id, contract)
    assert(len(contract_id) > 0)
    return contract_id


def get_all():
    '''Return a list of pairs of [id, name] of all the locally registered servers.'''
    server_count = opentxs.OTAPI_Wrap_GetServerCount()
    servers = []
    for i in range(server_count):
        server_id = opentxs.OTAPI_Wrap_GetServer_ID(i)
        server_name = opentxs.OTAPI_Wrap_GetServer_Name(server_id)
        servers.append([server_id, server_name])

    return servers


def first_id():
    return get_all()[0][0]


def only_id():
    '''Returns the server id if there is only one server, otherwise raises an error'''
    servers = get_all()
    if len(servers) == 0:
        return None
    assert len(servers) == 1, "There are multiple servers, you must explicitly pick one"
    return servers[0][0]


def check_id(server_id, user_id):
    """
    Returns true if the server is available and the user (same as nym) exists.
    """

    # The user_id parameters here is the same as nym_id in other api calls

    # The method is described as a "ping" in the API documentation, which should
    # be called after wallet initialized. However a remote account on the server
    # is required.

    if hasattr(opentxs, 'OTAPI_Wrap_pingNotary'): # new api name
        retval = opentxs.OTAPI_Wrap_pingNotary(server_id, user_id)
    else: # todo: old api name, remove in due time
        retval = opentxs.OTAPI_Wrap_checkServerID(server_id, user_id)

    # print("(debug) check_server_id retval=", retval)

    # The return value `1` for success is defined by
    #     case (OTClient::checkServerId)
    # in OTClient::ProcessUserCommand()

    return retval == 1


def first_active_id():
    '''Return the first known active notary, or if there are none, just
    the first one.  We should have at least one we're talking to.

    '''
    if active:
        return active[0]
    else:
        return first_id()


def first_inactive_id():
    for s in get_all():
        if s[0] not in active:
            return s[0]
    return None
