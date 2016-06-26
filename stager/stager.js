var kue = require('kue');
var cluster = require('cluster'); 
var queue = kue.createQueue({
    redis: {
        port: 6379,
        host: '0.0.0.0'
    }
});

queue.on( 'error', function(err) {
    if ( cluster.isMaster) { console.log('Oops... ', err); }
}).on( 'job enqueue', function(id, type) {
    if ( cluster.isMaster) { console.log('job %d got queued of type %s', id, type); }
}).on( 'job complete', function(id, result) {
    if ( cluster.isMaster) { console.log('job %d complete', id); }
}).on( 'job failed attempt', function(id, err, nattempts) {
    if ( cluster.isMaster) { console.log('job %d failed, attempt %d', id, nattempts); }
}).on( 'job failed' , function(id, err) {
    if ( cluster.isMaster) { console.log('job %d failed', id); }
});

if (cluster.isMaster) {
    // restful UI interface
    kue.app.listen(3000);

    // fork workers
    var nworkers = require('os').cpus().length - 1;
    for (var i = 0; i < nworkers; i++) {
        cluster.fork();
    }

} else {

    queue.process("rdm", function(job, done) {

        var domain = require('domain').create();
 
        domain.on('error', function(err) {
            done(err);
        });
 
        domain.run( function() {
            if ( job.data.srcURL === undefined || job.data.dstURL === undefined ) {
                console.log("ignore job: " + job.id);
                done();
            } else {
                console.log("staging data: " + job.data.srcURL + " -> " + job.data.dstURL);
             
                // TODO: make the logic implementation as a plug-in
                var cmd = 'irsync'
                var cmd_args = [job.data.srcURL, job.data.dstURL];
                var cmd_opts = {
                };
                var execFile = require('child_process').execFile;
                var child = execFile(cmd, cmd_args, cmd_opts, function(err, stdout, stderr) {
                    if (err) { throw new Error('irsync failure: ' + stderr); }
                    //done(null, stdout);
                    done();
                });
            }
        });
    });
}

// graceful queue shutdown
function shutdown() {
    if ( cluster.isMaster ) {
        queue.shutdown( 60000, function(err) {
            console.log( 'Kue shutdown: ', err||'' );
            process.exit( 0 );
        });
    }
}

process.once( 'SIGTERM', function(sig) { shutdown(sig); } );
process.once( 'SIGINT', function(sig) { shutdown(sig); } );
