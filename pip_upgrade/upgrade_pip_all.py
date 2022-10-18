# This is a simple script to upgrade all Python packages.
# Please launch this script with the Python executable whose packages are what you want to upgrade.

import functools
import json
import subprocess  # nosec: B404
import sys

import colorlabels as cl

# Load config from config file.
try:
    import upgrade_pip_config
except ImportError:
    config = {}
else:
    config = upgrade_pip_config.config

    if not isinstance(config, dict):
        raise TypeError('configuration should be a dict')

lower_sorted = functools.partial(sorted, key=lambda x: x.lower())

timeout = int(config.get('timeout', 100))
ignore_packages = lower_sorted(set(config.get('ignore_packages', [])))
ignore_packages_lower = set(p.lower() for p in ignore_packages)

py_version = '.'.join(map(str, sys.version_info[:3]))
py_exec = sys.executable
pip_exec = [py_exec, '-m', 'pip']
pip_global_param = ['--timeout', str(timeout)]


def get_outdated_list():
    output = subprocess.check_output(pip_exec + pip_global_param + ['list', '-o', '--format=json']).decode()  # nosec: B603
    result = (item['name'] for item in json.loads(output))
    return lower_sorted(p for p in result if p.lower() not in ignore_packages_lower)


# List all outdated packages.
with cl.progress('Checking update for all packages for Python %s (%s)' % (py_version, py_exec), cl.PROGRESS_SPIN):
    outdated_list = get_outdated_list()

# Print ignored packages.
if ignore_packages:
    cl.warning('These packages are ignored: %s' % ' '.join(ignore_packages))

if not outdated_list:  # No packages to upgrade.
    cl.success('All packages up to date.')
    sys.exit(0)

cl.info('These packages need upgrading: %s' % ' '.join(outdated_list))

# Upgrade outdated packages.
for name in outdated_list:
    cl.item('Upgrading package %s' % name)
    subprocess.call(pip_exec + pip_global_param + ['install', '-U', name])  # nosec: B603

# Check if all packages are upgraded successfully.
with cl.progress('Verifying update...', cl.PROGRESS_SPIN):
    outdated_list = get_outdated_list()

if outdated_list:
    cl.error('Failed to upgrade some packages: %s' % ' '.join(outdated_list))
    sys.exit(1)
else:
    cl.success('Successfully finished upgrading.')
