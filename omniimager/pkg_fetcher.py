import os
from shutil import copy


RPM_INSTALLER = 'dnf'


def fetch_and_install_pkg(dest_dir, pkg, verbose=False):
    cmd = [RPM_INSTALLER, 'install', pkg, '--installroot',
           dest_dir, '-y']
    if not verbose:
        cmd.append('-q')
    print('Fetching and Installing:', pkg, '...')
    os.system(' '.join(cmd))


def fetch_and_install_pkgs(dest_dir, pkg_list, repo_file, rootfs_repo_dir, verbose=False):
    print('Fetching and Installing Packages ...')

    # copy repo files again to avoid override by filesystem
    copy(repo_file, rootfs_repo_dir)

    for pkg in pkg_list:
        fetch_and_install_pkg(dest_dir, pkg, verbose)

    print("Done.")
    print("Fetched and Installed %s Packages" % len(pkg_list))


def fetch_pkgs(dest_dir, pkg_list, installroot=None, verbose=False):
    for pkg in pkg_list:
        cmd = [RPM_INSTALLER,
               'download', '--resolv --alldeps',
               '--destdir', dest_dir, pkg]
        if installroot:
            cmd.append('--installroot ' + installroot)
        if not verbose:
            cmd.append('-q')
        os.system(' '.join(cmd))
