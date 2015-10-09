## start server

$ wlmscpfs -v -dfp /scratch/dcmwlm_data -dfr 1234

## query with client

$ findscu --call AVANTO localhost 1234 wlistqry1.dcm
