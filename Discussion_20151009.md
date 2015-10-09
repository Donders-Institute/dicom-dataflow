# Dataflow discussion 2015-10-09

- participants: Rene, Hong, Marcel, Robert

- Subject and session will be specified at the time of lab booking.
    - an extra field for specifying subject and session is needed on the lab-booking form, and the input wll be part of the attributes of the booking.
    - Subjects and sessions have been used in the past for lab booking (excluding the ones being cancelled) are forbidden for new booking. 

- Tentative mapping between subject/session to DICOM worklist attributes.  A minimum worklist DICOM dump is

    ```
    (0010,0010) PN  [0001]                 # PatientName
    (0010,0020) LO  [3010000.01_0001]      # PatientID
    (0010,0030) DA  [UNKNOWN]              # PatientBirthDate
    (0010,0040) CS  [UNKNOWN]              # PatientSex
    (0032,1032) PN  [UNKNOWN]              # RequestingPhysician
    (0040,1001) SH  [3010001.01]           # RequestedProcedureID
    (0032,1060) LO  [The pilot project]    # RequestedProcedureDescription 
    (0040,0100) SQ                         # ScheduledProcedureStepSequence
    (fffe,e000) -
    (0008,0060) CS  [MR]                   # Modality
    (0040,0001) AE  [AVANTO]               # ScheduledStationAETitle
    (0040,0002) DA  [20150428]             # ScheduledProcedureStepStartDate
    (0040,0003) TM  [150000]               # ScheduledProcedureStepStartTime
    (0040,0006) PN  [UNKNOWN]              # ScheduledProcedureStepPerformancePhysician
    (0040,0009) SH  [3010000.01_s01]       # ScheduledProcedureStepID
    (0040,0010) SH  [MRI-AVANTO]           # ScheduledStationName
    (0040,0011) SH  [DCCN]                 # ScheduledProcedureStepLocation
    (fffe,e00d) -
    (fffe,e0dd) -
    (0040,1003) SH [ROUTINE]               # RequestedProcedurePriority
    ```

    where

    - `PatientName` is the subject identifier 
    - `PatientID` is a combination of the project identifier and subject identifier 
    - `PatientBirthday`, `PatientSex`, `RequestingPhysician` and `ScheduledProcedureStepPerformancePhysician` are unknown or null values. 
    - `RequestedProcedureID` is the project identifier
    - `RequestedProcedureDescription` is the project title with urlencoding for special characters 
    - `RequestedProcedureStepID` is the session identifier

## Actions

- Rene: looks up the Project database, insert the selection of subject+session on the lab-booking form.

- Hong and Marcel: check if the proposed worklist fields work on three MRI scanners.
