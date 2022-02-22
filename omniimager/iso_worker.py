import os
from shutil import copy


def prepare_iso_linux(iso_base_dir, rootfs_dir):
    # copy isolinux files to the corresponding folder
    isolinux_files = ['isolinux.bin', 'isolinux.cfg', 'ldlinux.c32']
    for file in isolinux_files:
        full_file = '/etc/omni-imager/isolinux/' + file
        copy(full_file, iso_base_dir)

    # copy linux kernel to the corresponding folder
    kernel_dir = rootfs_dir + '/boot/vmlinuz-*'
    cmd = ['cp', kernel_dir, iso_base_dir + '/vmlinuz']
    os.system(' '.join(cmd))


def make_iso(iso_base, rootfs_dir):
    prepare_iso_linux(iso_base, rootfs_dir)
    orig_dir = os.getcwd()
    os.chdir(iso_base)
    cmd = 'mkisofs -R -l -D -o ../openEuler-test.iso -b isolinux.bin -c boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table ./'
    os.system(cmd)
    os.chdir(orig_dir)
