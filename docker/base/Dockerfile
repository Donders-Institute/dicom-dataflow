FROM centos:7

# install required packages
RUN ( yum -y install wget gcc gcc-c++ \
                     make cmake autoconf git zlib zlib-devel mercurial \
                     openssl openssl-devel openssl-libs)

# create temporary directory
RUN ( mkdir -p /tmp )
WORKDIR /tmp

# build python 2.7.11
ARG python_prefix=/opt/python/2.7.11
ENV PYTHON_PREFIX=$python_prefix
RUN ( wget https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tgz )
RUN ( tar xvzf Python-2.7.11.tgz; cd Python-2.7.11 && \
      ./configure --prefix=$python_prefix && \
      make install && make clean )

# build dcmtk
ARG dcmtk_prefix=/opt/dcmtk/latest
ENV DCMTK_PREFIX=$dcmtk_prefix
RUN ( git clone https://git.dcmtk.org/dcmtk.git)
RUN ( mkdir dcmtk_build; cd dcmtk_build && \
      cmake -DCMAKE_INSTALL_PREFIX=$DCMTK_PREFIX ../dcmtk && \
      make -j8 && make install && make clean )

# install python pip
RUN ( wget https://bootstrap.pypa.io/get-pip.py && \
      $python_prefix/bin/python get-pip.py )
 
# install devcron
RUN ( $python_prefix/bin/pip install -e hg+https://bitbucket.org/dbenamy/devcron#egg=devcron )

# install Cheetah template engine
RUN ( wget https://pypi.python.org/packages/cd/b0/c2d700252fc251e91c08639ff41a8a5203b627f4e0a2ae18a6b662ab32ea/Cheetah-2.4.4.tar.gz#md5=853917116e731afbc8c8a43c37e6ddba && tar xvzf Cheetah-2.4.4.tar.gz && \
      cd Cheetah-2.4.4 && $python_prefix/bin/python setup.py install )

# install hpc-utility
WORKDIR /opt
COPY hpc-utility.tar.gz /opt
RUN ( tar xvzf hpc-utility.tar.gz && rm -rf /opt/hpc-utility.tar.gz )
ENV DCCN_PYTHONDIR=/opt/hpc-utility/python
ENV IRDM_RULE_PREFIX=/opt/hpc-utility/python/lib/rdm/rules

# run a trivial command
CMD ["/bin/echo", "hello"]
