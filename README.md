# DCCN DICOM dataflow

This package contains:

- [docker](http://docker.com) scripts to start the [Orthanc](http://www.orthanc-server.com/) PACS server and a simple DICOM worklist broker using the `wlmscpfs` program of the [DCMTK toolkits](http://dicom.offis.de). 
- A cron job script to periodically converting the lab-booking events into DICOM worklist. 

## Requirements 

1. [docker-engine](https://www.docker.com/products/docker-engine) and [docker-compose](https://docs.docker.com/compose/)
2. The DCCN's [hpc-utility package](https://github.com/Donders-Institute/hpc-utility). In the HPC cluster at DCCN, this package is available under the `/opt` directory.
3. crontab

## Configure and run the services 

### 1. checkout this package from GitHub
 
```bash
$ git clone https://github.com/Donders-Institute/dccn-dicom-dataflow.git
$ cd dccn-dicom-dataflow
```

### 2. start docker containers for DICOM PACS and worklist servers

The docker scripts are organised under the directory `docker`.  You may edit the file `docker-compose.yml` to adjust the data directory shared between containers and docker host. By default, data directories are organised under `/scratch/data_dicom/orthanc` and `/scratch/data_dicom/wlbroker` on the docker host.

Build docker containers using the following command:

```bash
$ cd docker
$ docker-compose build 
```

Start docker containers using the following command:

```bash
$ docker-compose up -d
```

If the services are started successfuly, the host should export three TCP ports.  They are `8042` for Orthanc web front-end, `4042` for Orthanc's DICOM interface, and `1234` for DICOM worklist service.

### 3. setup cron job for converting lab-booking events to worklist tasks

The script can be put right in the `crontab` is `cron/cron-dicom-labbooking2worklist.sh`. Inside the script, one should adjust the `WLBROKER_DIR` variable to specify the directory on the docker host in which the worklist files are stored.By default, it is set to `/scratch/data_dicom/wlbroker/WLBROKER`.  

In addition, the script uses `cron/cron-dicom-labbooking2worklist.ini` to setup connection to the project database of DCCN.

After the configuration, create a entry in the `crontab -e` similar to the example below:

```
30 * * * * /bin/bash -l -c '/root/opt/dccn-dicom-dataflow/cron/cron-dicom-labbooking2worklist.sh >> /scratch/data_dicom/cron/dicom-labbooking2worklist.log 2>&1'
```
