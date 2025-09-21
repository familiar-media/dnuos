#!/usr/bin/env python3
"""Test runner for dnuos - replaces the custom 'test' command from setup.py"""

import os
import sys
import doctest
from glob import glob


def testpkg(path):
    """Runs doctest on an entire package"""
    modules = glob(os.path.join(path, '*.py'))
    modules += glob(os.path.join(path, '**/*.py'))
    total_failures, total_tests = 0, 0
    for module in modules:
        if module.endswith('__init__.py'):
            continue
        module = os.path.splitext(module)[0]
        module = module.replace(os.path.sep, '.')
        justmodule = module.split('.', 1)[1]
        try:
            failures, tests = doctest.testmod(__import__(module, {}, {},
                                                         [justmodule]))
        except Exception as e:
            print('Unable to import %r: %s' % (module, e), file=sys.stderr)
            continue
        if tests > 0:
            print('%s: %s/%s passed' % (module, tests + (0 - failures), tests))
        total_failures += failures
        total_tests += tests

    print('Total: %s/%s passed' % (total_tests + (0 - total_failures),
                                   total_tests))
    print('')
    return total_failures == 0


def main():
    """Main test runner function"""
    # Set DATA_DIR environment variable
    data_dir = os.path.abspath('./testdata')
    if len(sys.argv) > 1:
        data_dir = os.path.abspath(sys.argv[1])

    os.environ['DATA_DIR'] = data_dir
    print(f"Using test data directory: {data_dir}")

    success = True
    success &= testpkg('dnuos')
    success &= testpkg('dnuostests')

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())