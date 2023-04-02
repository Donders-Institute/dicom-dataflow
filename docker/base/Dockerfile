FROM centos:7

# install required packages
RUN (ulimit -n 1024 && yum -y install gcc gcc-c++ make cmake && yum clean all && rm -rf /var/cache/yum/*)

# create temporary directory
RUN ( mkdir -p /tmp )

# build dcmtk
ARG dcmtk_prefix=/opt/dcmtk/latest
ENV DCMTK_PREFIX=$dcmtk_prefix
RUN ( cd /tmp && curl -LO https://github.com/DCMTK/dcmtk/archive/refs/tags/DCMTK-3.6.4.tar.gz && \
      tar xvzf DCMTK-3.6.4.tar.gz && cd dcmtk-DCMTK-3.6.4 && \
      mkdir dcmtk_build; cd dcmtk_build && \
      cmake -DCMAKE_INSTALL_PREFIX=$DCMTK_PREFIX ../ && \
      make -j8 && make install && make clean && cd )

RUN rm -rf /tmp/*DCMTK*

# run a trivial command
ENTRYPOINT ["/bin/echo", "hello"]
