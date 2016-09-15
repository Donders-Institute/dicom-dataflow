updateUserProfile {
    msi_str_replace(*kv_str,'&#37;','%',*kv_str_ext);
    uiUpdateUserProfile(*kv_str_ext, *out);
}
INPUT *kv_str=$"irodsUserName=U505173-ru.nl%organisationalUnit=DCCN"
OUTPUT *out
