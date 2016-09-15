getCollectionManifest {

  *out = '{}';

  # get manifest (size, iCAT checksum, path) of files right in the collection
  *qry = SELECT DATA_SIZE, DATA_CHECKSUM, COLL_NAME, DATA_NAME WHERE COLL_NAME = '*collName';

  foreach (*r in *qry) {
      writeLine('stdout', *r.DATA_SIZE ++ ',' ++ *r.DATA_CHECKSUM ++ ',' ++ *r.COLL_NAME ++ '/' ++ *r.DATA_NAME);
  }

  if ( bool(*recursive) ) {
      # get manifest (size, iCAT checksum, path) recursively within the collection
      *qry = SELECT DATA_SIZE, DATA_CHECKSUM, COLL_NAME, DATA_NAME WHERE COLL_NAME LIKE '*collName/%';

      foreach (*r in *qry) {
          writeLine('stdout', *r.DATA_SIZE ++ ',' ++ *r.DATA_CHECKSUM ++ ',' ++ *r.COLL_NAME ++ '/' ++ *r.DATA_NAME);
      }
  }
}
INPUT *collName=$"/rdm/di/dccn/DAC_3010000.01_173", *recursive=$'1'
OUTPUT ruleExecOut
