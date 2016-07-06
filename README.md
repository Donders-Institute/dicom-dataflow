# DCCN DICOM dataflow

_NOTE: this package has strong dependency on the DCCN research facility, such as the project-based storage and properly configured MRI scanners._

A schematic illustration of the dataflow is shown in the figure below:

![](dicom_dataflow_docker_containers.png)

This package consists of a few services involved in realising the dataflow.  From the lab-booking event to raw data archive in the [DI-RDM](http://data.donders.ru.nl) system, they are:

- A (cron-like) service running periodically to convert the lab-booking events into DICOM worklist.
- A light-weight DICOM worklist broker using the `wlmscpfs` program of the [DCMTK toolkits](http://dicom.offis.de) to serve scanning tasks to the MR scanners.
- A DICOM PACS server powered by [Orthanc](http://www.orthanc-server.com/)
- A data stager uploading raw data from the project storage to the [DI-RDM](https://data.donders.ru.nl) system.

Those services are provided as [docker](http://docker.com) containers. 

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
