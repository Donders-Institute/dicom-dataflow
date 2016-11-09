FROM jodogne/orthanc:1.1.0

# installing lua 5.1 and socket module
WORKDIR /tmp
RUN ( apt-get update && apt-get install -y ncurses-dev git curl )
RUN ( curl -R -O https://www.lua.org/ftp/lua-5.1.tar.gz && tar xvzf lua-5.1.tar.gz )
WORKDIR /tmp/lua-5.1
RUN ( make linux test && make install )
RUN ( git clone https://github.com/diegonehab/luasocket.git && cd luasocket && make && make install )

VOLUME [ "/var/lib/orthanc/log", "/var/lib/orthanc/db", "/var/lib/orthanc/idx", "/var/lib/orthanc/scripts", "/var/lib/orthanc/plugins", "/project" ]
EXPOSE 4242
EXPOSE 8042

WORKDIR /var/lib/orthanc
ENTRYPOINT [ "Orthanc", "--logdir=/var/lib/orthanc/log" ]
CMD [ "/etc/orthanc/" ]
