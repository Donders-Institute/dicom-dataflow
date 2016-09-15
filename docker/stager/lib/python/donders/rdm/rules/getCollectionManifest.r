getCollectionManifest {

  *out = '{}';

  # get manifest (size, iCAT checksum, path) of files right in the collection
  *qry = SELECT DATA_SIZE, DATA_CHECKSUM, COLL_NAME, DATA_NAME WHERE COLL_NAME = '*collName';

  foreach (*r in *qry) {
      msiString2KeyValPair("", *mkvp);
      msiAddKeyVal(*mkvp, "size", *r.DATA_SIZE);
      msiAddKeyVal(*mkvp, "checksum", *r.DATA_CHECKSUM);

      *m = '';
      *iec = errormsg( msi_json_objops(*m, *mkvp, "set"), *ierrmsg);

      msiString2KeyValPair("", *mkvp);
      msiAddKeyVal(*mkvp, *r.COLL_NAME ++ '/' ++ *r.DATA_NAME, *m);
      *iec = errormsg( msi_json_objops(*out, *mkvp, "set"), *ierrmsg);
  }

  if ( bool(*recursive) ) {
      # get manifest (size, iCAT checksum, path) recursively within the collection
      *qry = SELECT DATA_SIZE, DATA_CHECKSUM, COLL_NAME, DATA_NAME WHERE COLL_NAME LIKE '*collName/%';

      foreach (*r in *qry) {
          msiString2KeyValPair("", *mkvp);
          msiAddKeyVal(*mkvp, "size", *r.DATA_SIZE);
          msiAddKeyVal(*mkvp, "checksum", *r.DATA_CHECKSUM);

          *m = '';
          *iec = errormsg( msi_json_objops(*m, *mkvp, "set"), *ierrmsg);

          msiString2KeyValPair("", *mkvp);
          msiAddKeyVal(*mkvp, *r.COLL_NAME ++ '/' ++ *r.DATA_NAME, *m);
          *iec = errormsg( msi_json_objops(*out, *mkvp, "set"), *ierrmsg);
      }
  }
}
INPUT *collName=$"/rdm/di/dccn/DAC_3010000.01_173", *recursive=$'1'
OUTPUT *out
