
```
(0010,0010) PN  [3010000.01_SUBJ0001]
(0010,0020) LO  [3010000.01_SUBJ0001]
(0020,000d) UI  [12348]                      # Study Instance ID, should be a number and unique per day
(0032,1032) PN  [MARCEL ZWIERS]                   # RequestedPhysician (the one who book the lab)
(0032,1060) LO  [The title of project 3010000.01] # RequestedProcedureDescription
(0040,1001) SH  [SESS01]                          # RequestedProcedureID, this is mapped to StudyID in DICOM header, and the Study of DICOM is what DCCN researcher calls "session"
(0040,0100) SQ                       
(fffe,e000) -
(0008,0060) CS  [MR]
(0040,0001) AE  [PRISMA]
(0040,0002) DA  [20151106]
(0040,0003) TM  [170000]
(0040,0009) SH  [3010000.01_S01]     # max. 16 chars.
(0040,0010) SH  [PRISMA]
(0040,0011) SH  [DCCN]
(0040,0007) LO  [The description of SESS01]
(0040,0008) SQ
(fffe,e0dd) -
(fffe,e00d) -
(fffe,e0dd) -
```
