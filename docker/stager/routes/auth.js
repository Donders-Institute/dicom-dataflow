var config = require('config');
var auth = require('basic-auth');
var ActiveDirectory = require('activedirectory');

var _basicAuthAD = function(req, res, next) {

    // simple authentication aganist ActiveDirectory 
    var ad = new ActiveDirectory(config.get('ActiveDirectory'));
    var user = auth(req);

    try {
        if ( typeof user !== 'undefined' ) {
            ad.authenticate(user.name, user.pass, function(err, authenticated) {
                if (err) {
                    console.error(err);
                }

                if (authenticated) {
                    next();
                } else {
                    res.statusCode = 401;
                    res.setHeader('WWW-Authenticate', 'Basic realm="DIRDM Stager"');
                    res.end('Unauthorized');
                }
            });
        } else {
            res.statusCode = 401;
            res.setHeader('WWW-Authenticate', 'Basic realm="DIRDM Stager"');
            res.end('Unauthorized');
        }
    } catch(e) {
        console.error(e);
        res.statusCode = 500;
        res.end('Internal Server Error');
    }
}

module.exports.basicAuthAD = _basicAuthAD;
