FROM dccn-dirdm-irodsclient

# install cyberduck command-line interface
RUN ( echo -e "[duck-stable]\n\
name=duck-stable\n\
baseurl=https://repo.cyberduck.io/stable/\$basearch/\n\
enabled=1\n\
gpgcheck=0" > /etc/yum.repos.d/duck-stable.repo )

RUN ( yum -y install duck )

# create temporary directory
RUN ( mkdir -p /tmp )
WORKDIR /tmp

# install python 2.7.12 and pycurl (as the system pycurl seems to have problem with data encoding)
ADD https://www.python.org/ftp/python/2.7.12/Python-2.7.12.tgz /tmp 
RUN ( tar xvf Python-2.7.12.tgz \
      && cd Python-2.7.12 \
      && ./configure --prefix=/opt/python \
      && make && make install && rm -rf /tmp/Python-* )

ADD https://dl.bintray.com/pycurl/pycurl/pycurl-7.43.0.tar.gz /tmp 
RUN ( tar xvf pycurl-7.43.0.tar.gz \
      && cd pycurl-7.43.0 \
      && /opt/python/bin/python setup.py --with-nss install && rm -rf pycurl-* )

# install nodejs
ARG nodejs_prefix=/opt/nodejs
ADD https://nodejs.org/dist/v4.4.7/node-v4.4.7-linux-x64.tar.xz /tmp
RUN ( tar xf node-v4.4.7-linux-x64.tar.xz && mv node-v4.4.7-linux-x64 $nodejs_prefix )

# install stager scripts and required nodejs modules
RUN ( mkdir -p /opt/stager/bin )
WORKDIR /opt/stager
RUN ( $nodejs_prefix/bin/npm install express )
RUN ( $nodejs_prefix/bin/npm install redis )
RUN ( $nodejs_prefix/bin/npm install kue )
RUN ( $nodejs_prefix/bin/npm install config )
RUN ( $nodejs_prefix/bin/npm install tree-kill )
RUN ( $nodejs_prefix/bin/npm install basic-auth-connect )
RUN ( $nodejs_prefix/bin/npm install underscore )
RUN ( $nodejs_prefix/bin/npm install async )
RUN ( $nodejs_prefix/bin/npm install ldapjs )
RUN ( $nodejs_prefix/bin/npm install bunyan )
RUN ( $nodejs_prefix/bin/npm install activedirectory )
COPY package.json package.json
COPY *.js ./
COPY bin/* ./bin/
COPY lib ./lib
COPY config/* ./config/
COPY start_stager.sh start_stager.sh
RUN ( chmod +x start_stager.sh )

# run a stager
ENV PYTHON_BINDIR /opt/python/bin
ENV PYTHON_LIBDIR /opt/stager/lib/python
ENV NODEJS_PREFIX $nodejs_prefix
VOLUME [ "/project", "/opt/stager/irods_otp" ]
EXPOSE 3000
CMD [ "/opt/stager/start_stager.sh" ]
