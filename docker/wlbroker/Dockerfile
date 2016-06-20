FROM centos:7 

# install required packages
RUN ( yum -y install wget gcc gcc-c++ \
                     make autoconf git gnupg2 )

# create temporary directory
RUN ( mkdir -p /tmp )
WORKDIR /tmp

# build python 2.7.11
ARG python_prefix=/opt/python/2.7.11
ENV PYTHON_PREFIX=$python_prefix
RUN ( wget https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tgz )
RUN ( tar xvzf Python-2.7.11.tgz; cd Python-2.7.11; ./configure --prefix=$python_prefix; make install )

# build dcmtk
ARG dcmtk_prefix=/opt/dcmtk/latest
ENV DCMTK_PREFIX=$dcmtk_prefix
RUN ( git clone https://github.com/commontk/DCMTK.git )
RUN ( cd DCMTK; ./configure --prefix=$dcmtk_prefix; make; make install )

# install hpc-utility (here requires authentication to github)
#WORKDIR /opt
#ARG gpg_key
#ARG gpg_pub
#COPY $gpg_sec gpg_sec.gpg
#COPY $gpg_pub gpg_pub.gpg
#RUN ( gpg --import gpg_pub.gpg )
#RUN ( gpg --allow-secret-key-import --import gpg_sec.gpg )
#RUN ( git clone https://github.com/Donders-Institute/hpc-utility.git )

# install wlbroker starter script
ENV WLBROKER_DATADIR=/data/wlbroker
COPY wlbroker.sh wlbroker.sh
RUN (chmod +x wlbroker.sh)

# worklist data store and service port
VOLUME [ "/data/wlbroker" ]
EXPOSE 1234

CMD [ "./wlbroker.sh" ]
