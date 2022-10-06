"""Prints woz experiment url in GitPod"""
import hashlib
import random
import sys
import subprocess
from ipython_genutils.py3compat import cast_bytes, str_to_bytes

if len(sys.argv) > 1:
    # Get the password from the environment
    password_environment_variable = sys.argv[1]

    # Hash the password, this is taken from https://github.com/jupyter/notebook/blob/master/notebook/auth/security.py
    salt_len = 12
    algorithm = 'sha1'
    h = hashlib.new(algorithm)
    salt = ('%0' + str(salt_len) + 'x') % random.getrandbits(4 * salt_len)
    h.update(cast_bytes(password_environment_variable, 'utf-8') + str_to_bytes(salt, 'ascii'))
    password = ':'.join((algorithm, salt, h.hexdigest()))
else:
    password = ''

url = subprocess.check_output(['gp', 'url', '8888']).decode('utf-8').strip()
result = f"jupyter lab --NotebookApp.allow_origin='{url}' --ip='*' --NotebookApp.token='' --NotebookApp.password='{password}' --collaborative --notebook-dir experiments/woz --Anachat.restrict=tool.ipynb"

print(result)
