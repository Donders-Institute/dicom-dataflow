updateCollectionMetadata {
    msi_str_replace(*kv_str,'&#37;','%',*kv_str_ext);
    uiUpdateCollectionMetadata(*kv_str_ext, *out);
}
INPUT *kv_str=$"collName=/rdmtst/di/dccn/DAC_3010000.01%keyword_freetext=DICOM%keyword_freetext=raw data"
OUTPUT *out
