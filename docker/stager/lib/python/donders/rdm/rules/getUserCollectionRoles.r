getUserCollectionRoles {

    *ec = 0;
    *errmsg = '';

    # way to get all collecitons (including snapshots) in which the user has a role
    *instr = "(";
    foreach(*r in COL_ROLES) {
        msi_str_upper(*r, *r_u);
        *instr = *instr ++ "'" ++ *r_u ++ "',";
    }
    *instr = trimr(*instr, ',');
    *instr = *instr ++ ")";

    msi_str_upper(*userName, *userName_u);
    *qry_str = "SELECT COLL_ID,COLL_NAME,META_COLL_ATTR_NAME WHERE META_COLL_ATTR_NAME IN "++*instr++" AND META_COLL_ATTR_VALUE = '"++*userName_u++"'";

    *ec = errormsg( msi_qry_upper(*qry_str, *qry_out), *errmsg);

    *r_json_str = '[';

    if ( *ec == 0 ) {
        foreach( *row in *qry_out ) {
            *_cid   = *row.COLL_ID;
            *_cname = *row.COLL_NAME;
            *_crole = *row.META_COLL_ATTR_NAME;

            # basic collection attributes
            *_kvstr = 'collId='++*_cid++'%collName='++*_cname++'%collRole='++*_crole;

            # retrieve and append with more collection attributes
            *ec = errormsg(coll_attributes(*_cid, false, true, *_cdata, *isClosedDSC), *errmsg);

            if ( *ec == 0 ) {
                *_kvstr = *_kvstr ++ '%collectionIdentifier='++*_cdata."collectionIdentifier";
                *_kvstr = *_kvstr ++ '%type='++*_cdata."type";
                *_kvstr = *_kvstr ++ '%state='++*_cdata."state";
                *_kvstr = *_kvstr ++ '%title='++*_cdata."title";
                #*_kvstr = *_kvstr ++ '%organisation='++*_cdata."organisation";
                #*_kvstr = *_kvstr ++ '%organisationalUnit='++*_cdata."organisationalUnit";
                #*_kvstr = *_kvstr ++ '%projectId='++*_cdata."projectId";
            }

            # convert kv_str to json object
            wrap_value_json(*_kvstr, *_str_tmp);

            # add json object to json list
            *r_json_str = *r_json_str ++ *_str_tmp ++ ',';
        }
        *r_json_str = trimr(*r_json_str, ',');
    }
    *r_json_str = *r_json_str ++ ']';

    #*ec = errormsg(user_roles(*userName, *grpRoles, *collRoles), *errmsg);

    #*r_json_str = '[';
    #if ( *ec == 0 ) {
    #    foreach ( *cr in *collRoles ) {
    #        *ginfo  = split(*cr, "_");
    #        *_cid = elem(*ginfo, 0);
    #        *_crole = elem(*ginfo, size(*ginfo)-1);
    #        irodsGetCollectionName(*_cid, *_cname);
    #        # convert kv_str to json object
    #        wrap_value_json('collId='++*_cid++'%collName='++*_cname++'%collRole='++*_crole, *_str_tmp);
    #        *r_json_str = *r_json_str ++ *_str_tmp ++ ',';
    #    }
    #}
    #*r_json_str = trimr(*r_json_str, ',');
    #*r_json_str = *r_json_str ++ ']';

    # make output
    *out = '{"ec":' ++ str(*ec) ++ ', "errmsg":"' ++ *errmsg ++ '", "roles":' ++ *r_json_str ++ '}';
}
INPUT *userName=$"U505173-ru.nl"
OUTPUT *out
