var config = require('config');
var auth = require('basic-auth');
var Client = require('ssh2').Client;

var _getDirList = function(request, response) {

    var cfg = { host: config.get('StagerLocal.sftp.host'),
                port: config.get('StagerLocal.sftp.port'),
                username: auth(request).name,
                password: auth(request).pass };

    var dir = request.body.dir;

    var f_data = [];

    var c = new Client();
    var handle_error = function(err, code) {
        c.end();
        console.log(typeof err);
        console.error(err);
        response.contentType('application/json');
        response.status(code);
        response.end('something wrong');
    };

    if ( typeof dir === 'undefined' || dir == '' ) {
        handle_error("directory not specified", 404); 
    } else {
        try {
            c.on( 'ready', function() {
                c.sftp( function(err, sftp) {
                    if (err) throw err;
 
                    sftp.readdir(dir, function(err, list) {
                        if (err) {
                            handle_error(err, 500);
                        } else {
                            list.forEach(function(f) {
                                if ( f.longname.substr(0,1) == 'd' ) {
                                    f_data.push( { 'name': f.filename, 'type': 'd', 'size': -1 } );
                                } else if (f.longname.substr(0,1) != 'l') { // ignore symbolic links
                                    f_data.push( { 'name': f.filename, 'type': 'f', 'size': f.attrs.size } );
                                }
                            });
                            c.end();
                            response.contentType('application/json');
                            response.send(f_data);
                        }
                    });
                });
            }).on( 'error', function(err) {
                handle_error(err, 500);
            }).connect(cfg);
        } catch(err) {
            handle_error(err, 500);
        }
    }
}

module.exports.getDirList = _getDirList;
