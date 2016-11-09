# Instruction 

This instruction will show you how to build and start a few docker containers for enabling the DCCN DICOM dataflow.

The containers are organised in the following sub-directories:

- `docker/base`: basic container with pre-installed tools/libraries/packages/modules
- `docker/orthanc`: the [Orthanc](http://www.orthanc-server.com) server
- `docker/wlbroker`: the DICOM worklist broker
- `docker/cal2wl`: the cron job converting calendar bookings to DICOM worklist

They are orchestrated by the docker-compose file `docker/docker-compose-dicomdf.yml`.

## requirements of the docker host

- sufficient space on directory `/scratch/data_dicom`, for Orthanc database and DICOM worklist.
- access to the project storage, i.e. the `/project` directory
- accepting inbound connectivity via ports: `8042`, `4042` and `1234`

## configuration

The files to be configured properly are:

- `docker/docker-compose-dicomdf.yml`

  In the `docker/docker-compose-dicomdf.yml` file, adjust the data directory shared between containers and docker host. By default, data directories are organised under `/scratch/data_dicom/orthanc` and `/scratch/data_dicom/wlbroker` on the docker host.

  In the `docker/docker-compose-dicomdf.yml` file, you should also change the github username and password in order to checkout [the `hpc-utility` repository](https://github.com/Donders-Institute/hpc-utility) from GitHub.

- `docker/cal2wl/config.ini`

  In the file `docker/cal2wl/config.ini`, change the database settings accordingly in order to access the lab-booking events in the DCCN calendar system based on MySQL database.

- `docker/cal2wl/cron/crontab`

  In the file `docker/cal2wl/cron/crontab`, you may adjust how often the lab-booking events in calender are converted into DICOM worklist.

## start the containers 

Build docker containers using the following command:

```bash
$ cd docker
$ docker-compose -f docker-compose-dicomdf build --force-rm
```

Start up docker containers using the following command:

```bash
$ docker-compose -f docker-compose-dicomdf up -d
```

If the services are started successfuly, the host should export three TCP ports.  They are `8042` for Orthanc web front-end, `4042` for Orthanc's DICOM interface, and `1234` for DICOM worklist service.
