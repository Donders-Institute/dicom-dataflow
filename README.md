# DCCN DICOM dataflow

_NOTE: this package has strong dependency on the DCCN research facility, such as the project-based storage, properly configured MRI scanners and the [DI-RDM](http://data.donders.ru.nl) system._

A schematic illustration of the dataflow is shown in the figure below:

![](dicom_dataflow_docker_containers.png)

This package consists of a few services involved in realising the dataflow.  From the lab-booking event to raw data archive in the [DI-RDM](http://data.donders.ru.nl) system, they are:

- __CAL2WL__: a (cron-like) service running periodically to convert the lab-booking events into DICOM worklist.
- __WLBROKER__: a light-weight DICOM worklist broker using the `wlmscpfs` program of the [DCMTK toolkits](http://dicom.offis.de) to serve worklist to the MR scanners.
- __PACS__: a [Orthanc](http://www.orthanc-server.com/)-powered DICOM PACS server.
- ~~__STAGER__: a data stager uploading raw data from the project storage to the [DI-RDM](https://data.donders.ru.nl) system ~~

Those services are provided as [docker](http://docker.com) containers.

Note: The Stager service is now provided as a separate package.  It can be found in [https://github.com/donders-research-data-management/rdm-stager](this repository).

## Requirements 

1. [docker-engine](https://www.docker.com/products/docker-engine)
1. [docker-compose](https://docs.docker.com/compose/)

## Getting start

### 1. checkout this package from GitHub
 
```bash
$ git clone https://github.com/Donders-Institute/dicom-dataflow.git
$ cd dicom-dataflow
```

### 2. start docker containers

Instruction of startng docker containers is documented [here](docker/README.md).
