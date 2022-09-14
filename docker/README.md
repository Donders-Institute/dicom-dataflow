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

Prepare environment variables by copying the [`env.example`](env.example) file to `.env`; and modify the values accordingly. 

The files to be configured properly are:

- `docker/cal2wl/config.yml`

  In the file `docker/cal2wl/config.yml`, change the connections accordingly in order to access the lab-booking events in the DCCN project database.

- `docker/cal2wl/cron/crontab`

  In the file `docker/cal2wl/cron/crontab`, you may adjust how often the lab-booking events in calender are converted into DICOM worklist.

## build the containers

The service `cal2wl` makes use of the [`dicom_worklist`](https://github.com/Donders-Institute/tg-toolset-golang/tree/master/dataflow/cmd/dicom_worklist) program from the [tg-toolset-golang](https://github.com/Donders-Institute/tg-toolset-golang).  Make sure a correct [tag of the tg-toolset-golang](https://github.com/Donders-Institute/tg-toolset-golang/tags) is specified during the build.

```bash
$ docker-compose build --build-arg TG_TOOLSET_TAG={tag} --force-rm
```

## run the containers

Start up docker containers using the following command:

```bash
$ docker-compose -f docker-compose up -d
```

If the services are started successfuly, the host should export three TCP ports.  They are `8042` for Orthanc web front-end, `4042` for Orthanc's DICOM interface, and `1234` for DICOM worklist service.
