var kue = require('kue');
var cluster = require('cluster'); 
var queue = kue.createQueue({
    redis: {
        port: 6379,
        //host: 'redis'
        host: '0.0.0.0'
    }
});
var path = require('path');

const stager_bindir = __dirname + path.sep + 'bin';

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
                var cmd = stager_bindir + path.sep + 's-irsync.sh';
                var cmd_args = [ job.data.srcURL, job.data.dstURL ];
                var cmd_opts = {
                };
  
                job.data.__stopped = false;
                var execFile = require('child_process').execFile;
                var child = execFile(cmd, cmd_args, cmd_opts, function(err, stdout, stderr) {
                    if (err) { throw new Error(stderr); }
                    job.data.__stopped = true;
                    done(null, stdout);
                });

                child.on( "exit", function(code, signal) {
                    job.data.__stopped = true;
                    if ( signal != 'null' ) {
                        throw new Error('job terminated by ' + signal);
                    }
                });

                // determine job timeout 
                var timeout;
                if ( job.data.timeout === undefined || job.data.timeout <= 0 ) {
                    // no timeout
                    timeout = Number.MAX_SAFE_INTEGER;  
                } else {
                    timeout = job.data.timeout;
                }

                // initiate a monitor loop (timer) for heartbeat check on job status/progress
                var t_beg = new Date().getTime() / 1000;
                var timer = setInterval( function() {
                    if ( ! job.data.__stopped ) {
                        // job still running, timeout check
                        if ( new Date().getTime()/1000 - t_beg > timeout ) {
                            console.log( 'job ' + job.id + ' timout (> ' + timeout + 's)');
                            child.stdin.pause();
                            child.kill('SIGKILL');
                        } else {
                            // TODO: check irsync progress and report back to the job progress
                        }
                    } else {
                        // stop the timer 
                        clearInterval(timer);
                    }
                }, 1000 );
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
