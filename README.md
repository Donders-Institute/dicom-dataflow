# DCCN DICOM dataflow

This package contains:

- [docker](http://docker.com) scripts to start the [Orthanc](http://www.orthanc-server.com/) PACS server and a simple DICOM worklist broker using the `wlmscpfs` program of the [DCMTK toolkits](http://dicom.offis.de). 
- A cron job script to periodically converting the lab-booking events into DICOM worklist. 

## Requirements 

1. [docker-engine](https://www.docker.com/products/docker-engine)
1. [docker-compose](https://docs.docker.com/compose/)

## Configure and run the services 

### 1. checkout this package from GitHub
 
```bash
$ git clone https://github.com/Donders-Institute/dccn-dicom-dataflow.git
$ cd dccn-dicom-dataflow
```

### 2. configure access to private GitHub repositories and the databases

The files to be configured properly are:

- `docker/docker-compose.yml`

  In the `docker/docker-compose.yml` file, adjust the data directory shared between containers and docker host. By default, data directories are organised under `/scratch/data_dicom/orthanc` and `/scratch/data_dicom/wlbroker` on the docker host.

  In the `docker/docker-compose.yml` file, you should also change the github username and password in order to checkout the `hpc-utility` repository from GitHub.

- `docker/cal2wl/config.ini`

  In the file `docker/cal2wl/config.ini`, change the database settings accordingly in order to access the lab-booking events in the DCCN calendar system based on MySQL database.

- `docker/cal2wl/cron/crontab`

  In the file `docker/cal2wl/cron/crontab`, you may adjust how often the lab-booking events in calender are converted into DICOM worklist.

### 3. start docker containers for DICOM PACS and worklist servers

Build docker containers using the following command:

```bash
$ cd docker
$ docker-compose build
```

Start up docker containers using the following command:

```bash
$ docker-compose up -d
```

If the services are started successfuly, the host should export three TCP ports.  They are `8042` for Orthanc web front-end, `4042` for Orthanc's DICOM interface, and `1234` for DICOM worklist service.
