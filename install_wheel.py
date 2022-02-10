# -*- coding: utf-8 -*-
import os
import sys
import argparse
import platform
from subprocess import run

def is_macos():
    """
    :return: True if system is MacOS, False otherwise
    """
    return platform.system() == 'Darwin'


def is_windows():
    """
    :return: True if system is Windows, False otherwise
    """
    return platform.system() == 'Windows'

def is_linux():
    """
    :return: True if system is Windows, False otherwise
    """
    return platform.system() == 'Linux'


PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.abspath(os.path.join(PROJECT_DIR, "src", "code_generator")))
from version import VERSION

PYTHON = "python3"
PIP = "pip3"

if is_macos() or is_linux():
    PYTHON = "python3"
    PIP = "pip3"
elif is_windows():
    PYTHON = "python"
    PIP = "pip"


def uninstall_wheel():
    """
    pip.exe uninstall -y auditor-srv
    """
    run([PIP, 'uninstall', '-y', 'code-generator'])


def build_wheel():
    """
    python.exe -m pip install --upgrade pip
    python.exe -m pip install --upgrade build
    python.exe -m build
    """
    run([PYTHON, '-m', 'pip', 'install', '--upgrade', 'pip'])
    run([PYTHON, '-m', 'pip', 'install', '--upgrade', 'build'])
    run([PYTHON, '-m', 'build'])


def install_wheel():
    """
    pip.exe install ./dist/auditor_srv-{VERSION}-py3-none-any.whl
    """
    wheel_path = os.path.join(PROJECT_DIR, 'dist', 'code_generator-{}-py3-none-any.whl'.format(VERSION))
    run([PIP, 'install', wheel_path])


def main():
    parser = argparse.ArgumentParser(description='Command-line params')
    parser.add_argument('--mode',
                        help='What to di with the package',
                        choices=["build", "install", "reinstall", "uninstall"],
                        default="reinstall",
                        required=False)
    args = parser.parse_args()
    if args.mode == "build":
        build_wheel()
    elif args.mode == "install":
        build_wheel()
        install_wheel()
    elif args.mode == "reinstall":
        uninstall_wheel()
        build_wheel()
        install_wheel()
    elif args.mode == "uninstall":
        uninstall_wheel()
    else:
        print("Unknown mode")

    return 0


if __name__ == '__main__':
    sys.exit(main())
