# DCCN DICOM dataflow

This package includes tools and scripts for running the DICOM worklist broker, built around the [DCMTK toolkits](http://dicom.offis.de/dcmtk.php.en).

## Starting worklist broker

An init script built around the DCMTK `wlmscpfs` program is provided.  Do the following steps to include this script into system init.

```bash
$ cp etc/init.d/wlserver /etc/init.d
$ chkconfig --add wlserver
```

After that, one can manage the service via

```bash
$ service wlserver {start|stop|restart|status}
```

## Example worklists

A workable DICOM worklist example is located within directory `example/WLBROKER`.  The directory `WLBROKER` should match the broker's DICOM modality name.  To make the  worklist example available, you need to copy the whole directory into the `$WLDIR` directory defined in `etc/wlserver` init script.  For example,

```bash
$ cp -R example/WLBROKER /scratch/OrthancData/DicomWorklist
```

__Note__: remember to `touch` a lockfile within the `WLBROKER` directory so that the `wlmscpfs` recognises it's a directory in which the worklists are provided.  For example,

```bash
$ touch /scratch/OrthancData/DicomWorklist/WLBROKER/lockfile
```

Modify the `DA` and `TM` DICOM fields so a future timestamp, and the `AE` and `SH` fields to relevant MRI scanner in the `wklist1.dump` file and convert it into DICOM format:

```bash
$ source /opt/_modules/setup.sh
$ module load dcmtk
$ dump2dcm /scratch/OrthancData/DicomWorklist/WLBROKER/wklist1.dump /scratch/OrthancData/DicomWorklist/WLBROKER/wklist1.wl
```

## Test client query on example worklists

Instead of testing with MRI console, one could also test with DCMTK's `findscu` by querying the examples worklists.  In the `example/client` directory a very generic query is prepared as file `wlistqry1.dump`.  Simply convert it to DICOM format and run the query via the `findscu` command:

```bash
$ dump2dcm example/client/wlistqry1.dump example/client/wlistqry1.dcm
$ findscu --call WLBROKER localhost 1234 example/client/wlistqry1.dcm
```

On the screen, you should see the response with the worklists in return.
