# -*- coding: utf-8 -*-
import os
import sys
import argparse
import platform
import json
from subprocess import run
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read(filenames=['setup.cfg'])
VERSION = cfg.get('metadata', 'version')

# Name with underscore (wheel filename)
PACKAGE_NAME = cfg.get('metadata', 'name')

# Name with dash (pip name, URL, S3 bucket)
PACKAGE_NAME_DASH = PACKAGE_NAME.replace('_', '-')

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))
PYTHON = "python3"
PIP = "pip3"


def is_linux():
    """
    :return: True if system is Linux, False otherwise
    """
    return platform.system() == 'Linux'


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


if is_macos() or is_linux():
    PYTHON = "python3"
    PIP = "pip3"
elif is_windows():
    PYTHON = "python"
    PIP = "pip"


def sanity_check():
    """
    Check src/{PACKAGE_NAME} exists
    """
    if not os.path.isdir(os.path.join(PROJECT_DIR, 'src', PACKAGE_NAME)):
        raise RuntimeError(f'Cannot find src/{PACKAGE_NAME}')


def wheel_path():
    """
    :return: Path to the wheel file
    """
    return os.path.join(PROJECT_DIR, 'dist', f'{PACKAGE_NAME}-{VERSION}-py3-none-any.whl')


def uninstall_wheel():
    """
    pip.exe uninstall -y {PACKAGE_NAME_DASH}
    """
    run([PIP, 'uninstall', '-y', PACKAGE_NAME_DASH])


def publish_pypi():
    """
    Publish the package to PyPI
    Example:
    twine upload dist/{PACKAGE_NAME}-2.9.34-py3-none-any.whl
    """
    run([PYTHON, '-m', 'pip', 'install', '--upgrade', 'build', 'twine'])
    run(['twine', 'check', 'dist/*'])
    run(['twine', 'upload', 'dist/*'])


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
    pip.exe install ./dist/{PACKAGE_NAME}-{VERSION}-py3-none-any.whl
    """
    run([PIP, 'install', wheel_path()])


def install_wheel_devmode():
    """
    pip.exe install -e ./dist/{PACKAGE_NAME}-{VERSION}-py3-none-any.whl
    """
    run([PIP, 'install', '-e', '.'])


def cleanup_old_wheels():
    """
    Remove all previous {PACKAGE_NAME}-{}-py3-none-any.whl in dist
    """
    if os.path.isdir(os.path.join(PROJECT_DIR, 'dist')):
        for file in os.listdir(os.path.join(PROJECT_DIR, 'dist')):
            if file.startswith(f'{PACKAGE_NAME}-'):
                os.remove(os.path.join(PROJECT_DIR, 'dist', file))


def upload_s3():
    f"""
    Upload the package to S3
    Example:
    aws s3 cp {PACKAGE_NAME}-2.9.31-py3-none-any.whl s3://{PACKAGE_NAME_DASH}/packages/
    aws s3api put-object-acl
        --bucket {PACKAGE_NAME_DASH}
        --key packages/{PACKAGE_NAME}-2.9.31-py3-none-any.whl
        --acl public-read
    """
    run(['aws', 's3', 'cp', wheel_path(), f's3://{PACKAGE_NAME_DASH}/packages/'])
    run(['aws', 's3api', 'put-object-acl',
         '--bucket', f'{PACKAGE_NAME_DASH}',
         '--key', f'packages/{PACKAGE_NAME}-{VERSION}-py3-none-any.whl',
         '--acl', 'public-read'])


def tag_release():
    """
    Tag the release on GitHub
    Example:
    git tag -a release.2.9.34 -m"Release 2.9.34"
    git push origin --tags master
    """
    run(['git', 'tag', '-a', 'release.{}'.format(VERSION), '-m', 'Release {}'.format(VERSION)])
    run(['git', 'push', 'origin', '--tags', 'master'])


def create_release(release_file):
    """
    Create a release on GitHub
    Example:
    gh release create release.2.9.34 dist/{PACKAGE_NAME}-2.9.34-py3-none-any.whl --title 2.9.34 --notes-file RELEASE.md
    """
    run(['gh', 'release', 'create', 'release.{}'.format(VERSION), wheel_path(),
         '--title', '{}'.format(VERSION),
         '--notes-file', release_file])


def release_version_exists(version):
    """
    Check if version with respective release notes exists in RELEASE_NOTES.json
    :param version: Version to check in format 2.9.34
    :return: True if version exists, False otherwise
    """
    with open(os.path.join(PROJECT_DIR, 'RELEASE_NOTES.json'), 'r') as release_json:
        release_notes = json.load(release_json)
    return True if version in release_notes['releases'] else False


def tmp_release_notes():
    """
    Read the last release notes in JSON format from release_notes.json and create a temporary release notes file
    :return: Path to the temporary release notes file
    """
    # read release_notes.json as dict
    release_md = 'RELEASE.md'
    with open('RELEASE_NOTES.json', 'r') as release_json:
        release_notes = json.load(release_json)

    if not release_version_exists(VERSION):
        print(f'No release notes found for version {VERSION}')
        sys.exit(1)

    last_release = release_notes['releases'][VERSION]['release_notes']
    url_template = release_notes['release']['download_link']
    release_url = url_template.format(version=VERSION,
                                      package_name=PACKAGE_NAME,
                                      package_name_dash=PACKAGE_NAME_DASH)
    # create a temporary release notes file
    with open(release_md, 'w') as release_tmp:
        release_tmp.write('## Release notes\n')
        for note in last_release:
            release_tmp.write('* {}\n'.format(note))
        release_tmp.write('## Staging Area Download URL\n')
        release_tmp.write('[Wheel Package {} on AWS S3]({})\n'.format(VERSION, release_url))
    return os.path.abspath(release_md)


def main():
    parser = argparse.ArgumentParser(description='Command-line params')
    parser.add_argument('--mode',
                        help='What to do with the package',
                        choices=["build", "install", "dev-mode", "reinstall", "uninstall"],
                        default="reinstall",
                        required=False)
    parser.add_argument('--upload-s3',
                        help='Upload the package to S3',
                        action='store_true',
                        required=False)
    parser.add_argument('--create-release',
                        help='Create a release on GitHub',
                        action='store_true',
                        required=False)
    parser.add_argument('--publish-pypi',
                        help='Publish the package to PyPI',
                        action='store_true',
                        required=False)
    args = parser.parse_args()

    print(f'Package name: {PACKAGE_NAME}')
    print(f'Package name2: {PACKAGE_NAME_DASH}')
    print(f'Version: {VERSION}')
    sanity_check()

    if args.create_release and not release_version_exists(VERSION):
        print(f'No release notes found for version {VERSION}')
        sys.exit(1)

    if args.mode == "build":
        build_wheel()
    elif args.mode == "install":
        cleanup_old_wheels()
        build_wheel()
        install_wheel()
    elif args.mode == "dev-mode":
        cleanup_old_wheels()
        build_wheel()
        install_wheel_devmode()
    elif args.mode == "reinstall":
        cleanup_old_wheels()
        uninstall_wheel()
        build_wheel()
        install_wheel()
    elif args.mode == "uninstall":
        uninstall_wheel()
    else:
        print("Unknown mode")

    if args.upload_s3 and args.mode != "uninstall":
        upload_s3()

    if args.create_release and args.mode != "uninstall":
        release_file = tmp_release_notes()
        tag_release()
        create_release(release_file=release_file)
        os.remove(release_file)

    if args.publish_pypi and args.mode != "uninstall":
        publish_pypi()

    return 0


if __name__ == '__main__':
    sys.exit(main())
