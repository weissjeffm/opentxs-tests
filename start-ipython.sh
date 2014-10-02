#!/bin/bash
cd python3
export PYTHONPATH=/usr/local/lib64/python3.3/site-packages/:.
export LD_LIBRARY_PATH=/usr/local/lib64
ipython3 notebook > ipython-notebook.log 2>&1 &
disown %1
