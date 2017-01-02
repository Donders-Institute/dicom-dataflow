# DCCN DICOM dataflow

_NOTE: this package has strong dependency on the DCCN research facility, such as the project-based storage and properly configured MRI scanners._

A schematic illustration of the dataflow is shown in the figure below:

![](dicom_dataflow_docker_containers.png)

This package consists of the services indiciated by the blue blocks:

- __CAL2WL__: a (cron-like) service running periodically to convert the lab-booking events into DICOM worklist.
- __WLBROKER__: a light-weight DICOM worklist broker using the `wlmscpfs` program of the [DCMTK toolkits](http://dicom.offis.de) to serve worklist to the MR scanners.
- __ORTHANC__: a [Orthanc](http://www.orthanc-server.com/) DICOM PACS server.

Those services are provided as [docker](http://docker.com) containers.

Note: The service for streaming data from the PACS server to project storage and data archive is provided as a separate package called `streamer`.  It can be found in [this repository](https://github.com/Donders-Institute/streamer).

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
