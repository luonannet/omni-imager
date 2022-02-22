# Omni-Imager:
The imager worker for the Omni-Build Platform, a group of python scripts aimed to build bootable
openEuler ISO image(w/o Calamares GUI installer) from a list with packages.

## Note
### Currently the worker can only run on openEuler hosts 

## Usage
Dependencies: 
- Python runtime: `Python 3.8+`
- rpm packages: `dnf` `mkisofs`
- pypi packages: `pychroot`


Install：

```
git clone https://github.com/omnibuildplatform/omni-imager.git
cd omni-imager && pip install -r requirements.txt
python3 setup.py install
```

Simply run:
```shell
omni-imager --package-list /etc/omni-imager/openEuler-minimal.json --config-file /etc/omni-imager/conf.yaml \
--build-type installer-iso
```

## TODO list

- Hierarchical package list support
- User specified package list and logos for Calamares

## Contribute

Welcome to file issues or bugs at:
https://github.com/omnibuildplatform/omni-imager/issues
