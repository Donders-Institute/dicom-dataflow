# DCCN DICOM dataflow

_NOTE: this package has strong dependency on the DCCN research facility, such as the project-based storage and properly configured MRI scanners._

This package contains:

- [docker](http://docker.com) scripts to start the [Orthanc](http://www.orthanc-server.com/) PACS server and a simple DICOM worklist broker using the `wlmscpfs` program of the [DCMTK toolkits](http://dicom.offis.de). 
- A cron job script to periodically converting the lab-booking events into DICOM worklist. 
- A service for staging data from the project storage to the [DI-RDM](https://data.donders.ru.nl) system.

## Requirements 

1. [docker-engine](https://www.docker.com/products/docker-engine)
1. [docker-compose](https://docs.docker.com/compose/)

## Getting start

### 1. checkout this package from GitHub
 
```bash
$ git clone https://github.com/Donders-Institute/dccn-dicom-dataflow.git
$ cd dccn-dicom-dataflow
```

### 2. start docker containers

Instruction of startng docker containers is documented [here](docker/README.md).
