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

  In the file `docker/cal2wl/cron/crontab`, you may adjust how often the lab-booking events in calendar are converted into DICOM worklist.

## build the containers

Copy the [env.example](env.example) to `.env` and modify the environment variables in `.env` accordingly.

For building the containers, you will make use of the following variables:

- `DOCKER_REGISTRY`: the docker registry endpoint used to form the prefix of the image name.
- `DOCKER_IMAGE_TAG`: the docker image tag.
- `ORTHANC_VERSION`: the Orthanc version based on which the `orthac` container image.
- `ORTHANC_BUILD`: the build number of the `orthanc` container image.
- `TG_TOOLSET_TAG`: the [tag of the tg-toolset-golang](https://github.com/Donders-Institute/tg-toolset-golang/tags) from which the [`dicom_worklist`](https://github.com/Donders-Institute/tg-toolset-golang/tree/master/dataflow/cmd/dicom_worklist) program is built and included in the `cal2wl` container.

```bash
$ docker-compose build --force-rm
```

## run the containers

For running the containers, you will make use of the following variables in the `.env` file:

- `DOCKER_REGISTRY` and `DOCKER_IMAGE_TAG`: these two variables together determine the image to be used for the `cal2wl` and `wlbroker` containers.
- `ORTHANC_VERSION` and `ORTHANC_BUILD`: these two variables together determine the image to be used for the `orthanc` container.
- `VOL_ORTHANC_CONFIG`: path or name of the Orthanc configuration volume. It is bind-mounted to `/var/lib/orthanc/etc` in the Orthanc container.
- `VOL_ORTHANC_LOG`: path or name of the Orthanc log volume. It is bind-mounted to `/var/lib/orthanc/log` in the Orthanc container.
- `VOL_ORTHANC_DB`: path or name of the Orthanc data volume.  It is bind-mounted to `/var/lib/orthanc/db` in the Orthanc container.
- `VOL_ORTHANC_IDX`: path or name of the Orthanc data index volume. It is bind-mounted to `/var/lib/orthanc/idx` in the Orthanc container.
- `VOL_WLBROKER`: path or name of the workload list storage volume.  It is bind-mounted to `/data/wlbroker` in the `cal2wl` and `wlbroker` containers.
- `VOL_CAL2WL_CONFIG`: path or name of the `cal2wl` configuration volume. It is bind-mounted to `/opt/config` in the `cal2wl` container.

Start up docker containers using the following command:

```bash
$ docker-compose -f docker-compose up -d
```

If the services are started successfully, the host should export three TCP ports.  They are `8042` for Orthanc web front-end, `4042` for Orthanc's DICOM interface, and `1234` for DICOM worklist service.
