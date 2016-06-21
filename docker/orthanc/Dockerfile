FROM jodogne/orthanc:1.0.0

VOLUME [ "/var/lib/orthanc/log", "/var/lib/orthanc/db", "/var/lib/orthanc/scripts", "/var/lib/orthanc/plugins", "/project" ]
EXPOSE 4242
EXPOSE 8042

ENTRYPOINT [ "Orthanc", "--logdir=/var/lib/orthanc/log" ]
CMD [ "/etc/orthanc/" ]
