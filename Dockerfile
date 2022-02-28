FROM openeuler/openeuler:21.09
LABEL maintainer="tommylike<tommylikehu@gmail.com>"
WORKDIR /imager
COPY . /imager

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py

RUN yum -y update && yum -y install createrepo dnf genisoimage && pip3 install -r requirements.txt && python3 setup.py install
ENTRYPOINT ["omni-imager"]
