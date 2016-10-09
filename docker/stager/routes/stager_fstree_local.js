/**
 *	jQuery File Tree Node.js Connector
 *	Version 1.0
 *	wangpeng_hit@live.cn
 *	21 May 2014
 */
var fs = require('fs');
var basicAuth = require('basic-auth');

var _getDirList = function(request, response) {

    console.log(basicAuth(request));

    var dir = request.body.dir;
    var f_data = [];

    try {
        var files = fs.readdirSync(dir);
        files.forEach(function(f){
            var ff = dir + f;
            var stats = fs.lstatSync(ff)
            if (stats.isDirectory()) { 
                f_data.push( { 'name': f, 'type': 'd', 'size': 0 } );
            } else {
                f_data.push( { 'name': f, 'type': 'f', 'size': stats.size } );
            }
        });
    } catch(e) {
        console.error('Could not load directory: ' + dir);
        console.error(e);
    }

    response.contentType('application/json');
    response.send(f_data);
}

module.exports.getDirList = _getDirList;
