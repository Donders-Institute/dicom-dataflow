/**
 * *   authenticate user's username/password to a SFTP server 	
 * */
var config = require('config');
var auth = require('basic-auth');
var Client = require('ssh2').Client;

var _authenticateUser = function(request, response) {

    var cfg = { host: config.get('StagerLocal.sftp.host'),
                port: config.get('StagerLocal.sftp.port'),
                username: auth(request).name,
                password: auth(request).pass };

    var c = new Client();

    var handle_error = function(err) {
        c.end();
        console.error(err);
        response.status(404);
        response.end("User not found or not authenticated: " + cfg.username);
    };

    try {
        c.on( 'ready', function() {
            c.end();
            response.status(200);
            response.json({});
        }).on( 'error', function(err) {
            handle_error(err);
        }).connect(cfg);
    } catch(err) {
        handle_error(err);
    }
}

module.exports.authenticateUser = _authenticateUser;
