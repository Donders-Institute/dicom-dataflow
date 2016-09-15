sysDumpOUCollections {

    *ec = 0;
    *errmsg = '';
    *coll_list = list();

    if ( $userNameClient != ACC_RODS_ADMIN ) {
        *ec = EC_FORBIDDEN_ACTION;
        *errmsg = 'iRODS admin user required';
    } else {

        *parent_col = '/' ++ ZONE_NAME ++ '/' ++ *o ++ '/' ++ *ou;
 
        *qry = SELECT COLL_ID,COLL_NAME WHERE COLL_PARENT_NAME = '*parent_col';
 
        foreach (*r in *qry) {
            *collId   = *r.COLL_ID;
            *collName = *r.COLL_NAME;
           
            *jsonStr = '{}'; 
            *ec = errormsg( rdmGetCollectionAttributesJSON(*collId, *collName, false, false, *jsonStr, *isClosedDSC), *errmsg );
            *coll_list = cons(*jsonStr, *coll_list);
        }
    }

    # construct output
    *out = '{"ec":'++str(*ec)++',"errmsg":"'++*errmsg++'","n_collections":'++str(size(*coll_list))++',"collections":[';

    *col_out = "";
    foreach(*s in *coll_list) {
        *col_out = *col_out ++ *s ++ ',';
    }

    *out = *out ++ trimr(*col_out, ',') ++ ']}';
}
INPUT *o=$'di', *ou=$"dccn"
OUTPUT *out
