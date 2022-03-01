# Omni-Imager:
The imager worker for the Omni-Build Platform, a group of python scripts aimed to build bootable
openEuler ISO image(w/o Calamares GUI installer) from a list with packages.

## Usage
Dependencies: 
- openEuler distro
- Python runtime: `Python 3.8+`
- rpm packages: `dnf` `mkisofs` `genisoimage`
- pypi packages: check `requirements.txt`

Install：

1. From source:
```shell
git clone https://github.com/omnibuildplatform/omni-imager.git
cd omni-imager && pip install -r requirements.txt
python3 setup.py install
```

2. Using pip(currently you should download the release manually):
```shell
wget https://github.com/omnibuildplatform/omni-imager/releases/download/v0.1/omniimager-0.1.0.tar.gz
pip3 install --prefix / ./omniimager-0.1.0.tar.gz
```

Simply run:
```shell
omni-imager --package-list /etc/omni-imager/openEuler-minimal.json --config-file /etc/omni-imager/conf.yaml \
--build-type installer-iso --output-file openEuler-image.iso
```

## TODO list

- Hierarchical package list support
- User specified package list and logos for Calamares

## Contribute

Welcome to file issues or bugs at:
https://github.com/omnibuildplatform/omni-imager/issues
