import argparse
import json
import os
import subprocess
import sys
import time
import yaml
import shutil
import signal

from omniimager import rootfs_worker
from omniimager import installer_maker
from omniimager import iso_worker
from omniimager import pkg_fetcher


ROOTFS_DIR = 'rootfs'
DNF_COMMAND = 'dnf'

TYPE_VHD = 'vhd'
TYPE_INSTALLER = 'installer-iso'
TYPE_LIVECD = 'livecd-iso'
SUPPORTED_BUILDTYPE = [TYPE_LIVECD, TYPE_INSTALLER, TYPE_VHD]

INITRD_PKG_LIST = [
    "filesystem", "audit", "bash", "ncurses", "ncurses-libs",
    "cronie", "coreutils", "basesystem", "file", "bc", "bash",
    "bzip2", "sed", "procps-ng", "findutils", "gzip", "grep",
    "libtool", "openssl", "pkgconf", "readline", "sed", "sudo",
    "systemd", "util-linux", "bridge-utils", "e2fsprogs",
    "elfutils-libelf", "expat", "setup", "gdbm", "tar",
    "xz", "zlib", "iproute", "dbus", "cpio", "file",
    "procps-ng", "net-tools", "nspr", "lvm2", "firewalld",
    "glibc", "grubby", "hostname", "initscripts", "iprutils",
    "irqbalance", "kbd", "kexec-tools", "less", "openssh",
    "openssh-server", "openssh-clients", "parted", "passwd",
    "policycoreutils", "rng-tools", "rootfiles",
    "selinux-policy-targeted", "sssd", "tuned", "vim-minimal",
    "xfsprogs", "NetworkManager", "NetworkManager-config-server",
    "authselect", "dracut-config-rescue", "kernel-tools", "sysfsutils",
    "linux-firmware", "lshw", "lsscsi", "rsyslog", "security-tool",
    "sg3_utils", "dracut-config-generic", "dracut-network", "rdma-core",
    "selinux-policy-mls", "kernel"
  ]
REQUIRED_BINARIES = ["createrepo", "dnf", "mkisofs"]

parser = argparse.ArgumentParser(description='clone and manipulate git repositories')
parser.add_argument('--package-list', metavar='<package_list>',
                    dest='package_list', required=True,
                    help='Input file including information like package lists and target version.')
parser.add_argument('--config-file', metavar='<config_file>',
                    dest='config_file', required=True,
                    help='Configuration file for the software, including working dir, number of workers etc.')
parser.add_argument('--build-type', metavar='<config_file>',
                    dest='build_type', required=True,
                    help='Specify the build type, should be one of: vhd, livecd-iso, installer-iso')
parser.add_argument('--output-file', metavar='image-name', dest='output_file', const='openEuler-image.iso',
                    nargs='?', type=str, default="openEuler-image.iso",
                    help="Specify the name of the build image")


def parse_package_list(list_file):
    if not list_file:
        raise Exception

    with open(list_file, 'r') as inputs:
        input_dict = json.load(inputs)

    package_list = input_dict["packages"]
    return package_list


def clean_up_dir(target_dir):
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)


def binary_exists(name):
    return False if shutil.which(name) is None else True


def prepare_workspace(config_options):
    work_dir = config_options['working_dir']
    clean_up_dir(work_dir)
    os.makedirs(work_dir)

    verbose = False
    if config_options.get('debug'):
        verbose = True

    # prepare an empty rootfs folder with repo file in place
    rootfs_dir = config_options['working_dir'] + '/' + ROOTFS_DIR
    rootfs_repo_dir = rootfs_dir + '/etc/yum.repos.d'

    # TODO: make this configurable
    repo_file = '/etc/omni-imager/openEuler.repo'

    clean_up_dir(rootfs_dir)
    os.makedirs(rootfs_dir)
    os.makedirs(rootfs_repo_dir)
    shutil.copy(repo_file, rootfs_repo_dir)

    print('Create a clean dir to hold all files required to make iso ...')
    iso_base_dir = work_dir + '/iso'
    os.makedirs(iso_base_dir)

    return rootfs_dir, config_options['working_dir'], iso_base_dir, repo_file, rootfs_repo_dir, verbose


def omni_interrupt_handler(signum, frame):
    print('\nKeyboard Interrupted! Cleaning Up and Exit!')
    sys.exit(1)


def main():
    signal.signal(signal.SIGINT, omni_interrupt_handler)
    start_time = time.time()
    # parse config options and args
    parsed_args = parser.parse_args()

    build_type = parsed_args.build_type
    if build_type not in SUPPORTED_BUILDTYPE:
        print('Unsupported build-type, Stopped ...')
        sys.exit(1)
    else:
        print('Building:', build_type)

    for command in REQUIRED_BINARIES:
        if not binary_exists(command):
            print('binary not found: %s' % command)
            sys.exit(1)

    with open(parsed_args.config_file, 'r') as config_file:
        config_options = yaml.load(config_file, Loader=yaml.SafeLoader)

    packages = parse_package_list(parsed_args.package_list)
    user_specified_packages = []
    config_options['auto_login'] = False
    # Installer ISO have different rootfs with other image type
    if build_type == TYPE_INSTALLER:
        user_specified_packages = packages
        packages = INITRD_PKG_LIST
        config_options['auto_login'] = True

    rootfs_dir, work_dir, iso_base, repo_file, rootfs_repo_dir, verbose = prepare_workspace(config_options)
    rootfs_worker.make_rootfs(
        rootfs_dir, packages, config_options, repo_file, rootfs_repo_dir, build_type, verbose)

    if build_type == TYPE_INSTALLER:
        installer_maker.install_and_configure_installer(
            config_options, rootfs_dir, repo_file, rootfs_repo_dir, user_specified_packages)

    print('Compressing rootfs ...')
    rootfs_worker.compress_to_gz(rootfs_dir, work_dir)

    if build_type == TYPE_INSTALLER:
        print('Downloading RPMs for installer ISO ...')
        rpms_dir = iso_base + '/RPMS'
        os.makedirs(rpms_dir)
        pkg_fetcher.fetch_pkgs(rpms_dir, user_specified_packages, rootfs_dir, verbose=True)
        subprocess.run('createrepo ' + rpms_dir, shell=True)

    iso_worker.make_iso(iso_base, rootfs_dir, parsed_args.output_file)

    print('ISO: openEuler-test.iso generated in:', work_dir)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Elapsed time: %s s' % elapsed_time)
