/**
*   authenticate user's username/password to RDM 	
*/
var config = require('config');
var RestClient = require('node-rest-client').Client;

var _authenticateUser = function(request, response) {

    var cfg = {user: request.body.username,
               password: request.body.password};

    var c = new RestClient(cfg);
    var args = { headers: { "Accept": "application/json" } };

    var req = c.get(config.get('RDM.restEndpoint') + '/user/' + request.body.username, args, function(data, resp) {
        try {
            console.log('irods-rest response status: ' + resp.statusCode);
            if ( resp.statusCode == 200 ) {
                response.status(200);
                response.json(data);
            } else {
                response.status(404);
                response.end("User not found or not authenticated: " + request.body.username);
            } 
        } catch(e) {
            console.error(e);
            response.status(404);
            response.end("User not found or not authenticated: " + request.body.username);
        }
    });
}

module.exports.authenticateUser = _authenticateUser;
