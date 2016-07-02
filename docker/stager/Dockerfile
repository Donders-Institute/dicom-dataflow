FROM dccn-dirdm-irodsclient

# create temporary directory
RUN ( mkdir -p /tmp )
WORKDIR /tmp

# install nodejs
ARG nodejs_prefix=/opt/nodejs
RUN ( wget https://nodejs.org/dist/v4.4.7/node-v4.4.7-linux-x64.tar.xz && tar xf node-v4.4.7-linux-x64.tar.xz && mv node-v4.4.7-linux-x64 $nodejs_prefix )

# install stager scripts
RUN ( mkdir -p /opt/stager/bin )
WORKDIR /opt/stager
COPY package.json package.json
COPY *.js ./
COPY bin/* ./bin/
RUN ( $nodejs_prefix/bin/npm install redis )
RUN ( $nodejs_prefix/bin/npm install kue )
RUN ( $nodejs_prefix/bin/npm install tree-kill )
COPY start_stager.sh start_stager.sh
RUN ( chmod +x start_stager.sh )

# run a stager
ENV NODEJS_PREFIX $nodejs_prefix
VOLUME [ "/project", "/opt/stager/irods_otp" ]
EXPOSE 3000
CMD [ "/opt/stager/start_stager.sh" ]
