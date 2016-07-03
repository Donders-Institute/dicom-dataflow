var kue = require('kue');
var cluster = require('cluster'); 
var kill = require('tree-kill');
var queue = kue.createQueue({
    redis: {
        port: 6379,
        //host: 'redis'
        host: '0.0.0.0'
    }
});
var path = require('path');

var active_pids = {};

const stager_bindir = __dirname + path.sep + 'bin';

queue.on( 'error', function(err) {
    if ( cluster.isMaster) { 
        console.error('Oops... ', err);
    }
}).on( 'job enqueue', function(id, type) {
    if ( cluster.isMaster) { 
        console.log('[' + new Date().toISOString() + '] job %d enqueued for %s', id, type);
    }
}).on( 'job complete', function(id, result) {
    if ( cluster.isMaster) {
        console.log('[' + new Date().toISOString() + '] job %d complete', id);
    }
}).on( 'job failed attempt', function(id, err, nattempts) {
    if ( cluster.isMaster) {
        console.log('[' + new Date().toISOString() + '] job %d failed, attempt %d', id, nattempts); 
    }
}).on( 'job failed' , function(id, err) {
    if ( cluster.isMaster) {
        console.log('[' + new Date().toISOString() + '] job %d failed', id);
    }
}).on( 'job remove', function(id, err) {
    if ( cluster.isMaster) {
        var pinfo = active_pids[id];
        if ( ! (pinfo === undefined) ) {
            // inform worker to kill the process
            pinfo['worker'].send({'type': 'KILL', 'pid': pinfo['pid'], 'jid': id});
        }
        delete active_pids[id];
        console.log('[' + new Date().toISOString() + '] job %d removed', id);
    }
});

if (cluster.isMaster) {

    // restful UI interface
    kue.app.listen(3000);

    // fork workers
    var nworkers = require('os').cpus().length - 1;
    for (var i = 0; i < nworkers; i++) {
        var w = cluster.fork();
        w.on('message', function(msg) {
            if ( msg['type'] == 'START' ) {
                active_pids[msg['jid']] = {'worker': this, 'pid': msg['pid']};
                console.log('[' + new Date().toISOString() + '] job %s run by worker %s:%s', msg['jid'], active_pids[msg['jid']]['worker'].id, active_pids[msg['jid']]['pid']);
            } else {
                delete active_pids[msg['jid']];
            }
        });
    }

} else {

    process.on('message', function(msg) {
        if ( msg['type'] == 'KILL' ) {
            kill(msg['pid'], 'SIGKILL', function(err) {
                console.log( '[' + new Date().toISOString() + '] job ' + msg['jid'] + ' killed upon user removal');
            });
        }
    });

    queue.process("rdm", function(job, done) {

        var domain = require('domain').create();
 
        domain.on('error', function(err) {
            done(err);
        });
 
        domain.run( function() {
            if ( job.data.srcURL === undefined || job.data.dstURL === undefined ) {
                console.log('[' + new Date().toISOString() + '] job %d ignored: invalid arguments', job.id);
                done();
            } else {
             
                // TODO: make the logic implementation as a plug-in
                var cmd = stager_bindir + path.sep + 's-irsync.sh';
                var cmd_args = [ job.data.srcURL, job.data.dstURL ];
                var cmd_opts = {
                };
  
                var job_stopped = false;
                var execFile = require('child_process').execFile;
                var child = execFile(cmd, cmd_args, cmd_opts, function(err, stdout, stderr) {
                    // inform master the job has been stopped
                    process.send({'type':'stop', 'jid': job.id});
                    if (err) { throw new Error(stderr); }
                    job_stopped = true;
                    done(null, stdout);
                });

                // inform master the job has been started
                process.send({'type':'START', 'jid': job.id, 'pid': child.pid});

                child.on( "exit", function(code, signal) {
                    job_stopped = true;
                    // inform master the job has been stopped
                    process.send({'type':'STOP', 'jid': job.id});
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
                    if ( ! job_stopped ) {
                        // job still running, timeout check
                        if ( new Date().getTime()/1000 - t_beg > timeout ) {
                            child.stdin.pause();
                            kill(child.pid, 'SIGKILL', function(err) {
                                console.log( '[' + new Date().toISOString() + '] job ' + job.id + ' killed due to timout (> ' + timeout + 's)');
                            });
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
