#!/bin/bash
set -e  # Stop on first failing command

# Get full system path of the script directory
ROOT_DIR=`dirname "$0"`
ROOT_DIR=`( cd "$ROOT_DIR" && pwd )`
cd `dirname $0`

echo "Starting the fake GCS docker container"
docker stop gc-fake-storage
docker rm -v gc-fake-storage
docker run -d --name gc-fake-storage -p 4443:4443 -v $ROOT_DIR/init_buckets:/data matteoscandolo/gc-fake-storage:0.1.0
echo "Started."
echo

# Run the client with tests against it
echo "Running client-test.py..."
./client-test.py
echo "Done."
echo
echo "Logs from the fake GCS docker container:"
docker logs gc-fake-storage
echo

echo "Stopping the fake GCS docker container"
docker stop gc-fake-storage
