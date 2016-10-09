var config = require('config');
var RestClient = require('node-rest-client').Client;

var _getDirList = function(request, response) {

    var cfg = { user: request.body.rdm_user,
                password: request.body.rdm_pass };

    var dir = request.body.dir;

    var c = new RestClient(cfg);
    var args = { parameters: { listType: 'both', listing: 'True' },
                 headers: { "Accept": "application/json" } };

    var f_data = [];
    c.get(config.get('RDM.restEndpoint') + '/collection' + dir, args, function(data, resp) {

        try {
            console.log('irods-rest response status: ' + resp.statusCode);

            data.children.forEach(function(f){

                if ( f.objectType == 'COLLECTION' ) {
                    var rel_name = f.pathOrName.replace(f.parentPath + '/', '');
                    f_data.push( {'name': rel_name, 'type': 'd', 'size': -1} );
                } else {
                    f_data.push( {'name': f.pathOrName, 'type': 'f', 'size': f.dataSize} );
                }
            });
        } catch(e) {
            console.error(e);
        }

        response.contentType('application/json');
        response.json(f_data);
    });
}

module.exports.getDirList = _getDirList;
