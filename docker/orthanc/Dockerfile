FROM jodogne/orthanc:1.0.0

VOLUME [ "/var/lib/orthanc/db", "/var/lib/orthanc/scripts", "/var/lib/orthanc/plugins" ]
EXPOSE 4242
EXPOSE 8042

ENTRYPOINT [ "Orthanc" ]
CMD [ "/etc/orthanc/" ]
