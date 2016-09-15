countFileInCollection {

    *ec = 0;
    *errmsg = '';

    *nf1 = 0;
    foreach (*r in SELECT count(DATA_NAME),RESC_NAME WHERE COLL_NAME = '*collName' ) {
        if ( int(*r.DATA_NAME) > *nf1 ) {
            *nf1 = int(*r.DATA_NAME);
        }
    }

    *collPattern = *collName ++ '/%';
    *nf2 = 0;
    foreach (*r in SELECT count(DATA_NAME),RESC_NAME WHERE COLL_NAME like '*collPattern') {
        if ( int(*r.DATA_NAME) > *nf2 ) {
            *nf2 = int(*r.DATA_NAME);
        }
    }

    *out = '{"ec":'++str(*ec)++', "errmsg":"'++*errmsg++'", "nfiles":'++str(*nf1 + *nf2)++'}';
}

INPUT *collName=$'/rdm/di/dccn/DAC_xyz'
OUTPUT *out
