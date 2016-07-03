## Requirements

- [Node.js](http://nodejs.org) 
- [Redis](http://redis.io) 

## Installation

```bash
$ npm install config
$ npm install redis
$ npm install kue
$ npm install tree-kill 
```

## Start up service

1. start up Redis server

    ```bash
    $ redis-server
    ```

2. start up the application

    ```bash
    $ node stager.js
    ```

The web interface is accessible via `http://localhost:3000`. For inserting staging jobs, see the example in `test/test_insertjobs.sh`.
