FROM centos:7

# install required packages
RUN ( yum -y install wget gcc gcc-c++ \
                     make autoconf git zlib zlib-devel \
                     openssl openssl-devel openssl-libs \
                     sssd-client \
                     environment-modules which \
                     help2man unixODBC fuse-devel bzip2-devel pam-devel perl-JSON \ 
                     python-devel rpm-build curl curl-devel libxml2-devel )

# create temporary directory
RUN ( mkdir -p /tmp )
WORKDIR /tmp

# build iRODS client
ARG irods_version=4.1.8
COPY install-icommands.sh install-icommands.sh
RUN ( chmod +x install-icommands.sh && ./install-icommands.sh $irods_version )

# prepare iRODS client environment
RUN ( mkdir -p  /opt/irods/ssl )
COPY icat-prod.pem /opt/irods/ssl/icat-prod.pem
COPY irods_environment.json /opt/irods/irods_environment.json
ENV IRODS_ENVIRONMENT_FILE /opt/irods/irods_environment.json

# run a trivial command
WORKDIR /opt/irods
CMD ["/bin/echo", "hello"]
