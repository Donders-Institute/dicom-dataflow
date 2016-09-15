getNamespaceType {
    *ec = 0;
    *errmsg = '';
    *type = 'UNKNOWN';

    foreach (*r in SELECT COLL_ID WHERE COLL_NAME = '*namespace' ) {
        *type = 'COLLECTION';
    }

    if ( *type == 'UNKNOWN' ) {
        msiSplitPath(*namespace, *collName, *objName);
        foreach (*r in SELECT DATA_ID WHERE COLL_NAME = '*collName' AND DATA_NAME = '*objName' ) {
            *type = 'FILE';
        }
    }

    *out = '{"ec":'++str(*ec)++', "errmsg":"'++*errmsg++'", "type":"'++ *type ++'"}';
}

INPUT *namespace=$'/rdm/di/dccn/DAC_xyz'
OUTPUT *out
