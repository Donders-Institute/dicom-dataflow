# Instruction 

This instruction will show you how to build and start a few docker containers for enabling the DCCN DICOM dataflow.

A high-level picture of the dataflow is illustrated as the picture below:

The containers are distinguished into two service sets, naming the __dicomdf__ and __stager__ service sets, as it is logical to run the two sets of containers on different docker hosts for distributing the load, for example.

## The "dicomdf" service set

This service set makes use of the containers organised in the following sub-directories:

- `docker/base`
- `docker/orthanc`
- `docker/wlbroker`
- `docker/cal2wl`

These containers are orchestrated by the docker-compose file `docker/docker-compose-dicomdf.yml`.

### 1. docker host requirements

- sufficient space on directory `/scratch/data_dicom`
- access to the project storage, i.e. the `/project` directory
- firewall opened for in-bound connectivity via ports: `8042`, `4042` and `1234`

### 2. configure access to private GitHub repositories and the databases

The files to be configured properly are:

- `docker/docker-compose-dicomdf.yml`

  In the `docker/docker-compose-dicomdf.yml` file, adjust the data directory shared between containers and docker host. By default, data directories are organised under `/scratch/data_dicom/orthanc` and `/scratch/data_dicom/wlbroker` on the docker host.

  In the `docker/docker-compose-dicomdf.yml` file, you should also change the github username and password in order to checkout [the `hpc-utility` repository](https://github.com/Donders-Institute/hpc-utility) from GitHub.

- `docker/cal2wl/config.ini`

  In the file `docker/cal2wl/config.ini`, change the database settings accordingly in order to access the lab-booking events in the DCCN calendar system based on MySQL database.

- `docker/cal2wl/cron/crontab`

  In the file `docker/cal2wl/cron/crontab`, you may adjust how often the lab-booking events in calender are converted into DICOM worklist.

### 3. start docker containers for the service set "dicomdf" 

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

## The "stager" service set

This service set makes use of the containers organised in the following sub-directories:

- `docker/irodsclient`
- `docker/stager`

These containers are orchestrated by the docker-compose file `docker/docker-compose-stager.yml`.

### 1. docker host requirements

- directory `/scratch/data_stager`
- access to the project storage, i.e. the `/project` directory
- firewall opened for in-bound connectivity via ports: `3000`

### 2. configure the one-time password of the iRODS admin account

The 6-digit one-time password for iRODS admin account `irods` should be provided in the file `docker/irods_otp` before you start up the containers.

### 3. configure the username/password for accessing stager's RESTful interface

For the moment, the RESTful interface is protected by a simple username/password with default `admin:admin`.  You may change it in the file `docker/stager/config/default.json` before you build the containers.

### 4. start docker containers for the service set "stager" 

Build docker containers using the following command:

```bash
$ cd docker
$ docker-compose -f docker-compose-stager build --force-rm
```

Start up docker containers using the following command:

```bash
$ docker-compose -f docker-compose-stager up -d
```

If the services are started successfuly, the RESTful interface of the stager should be listening on port `3000`.  You may check it by connecting the browser to `http://<dockerhost>:3000`. 
