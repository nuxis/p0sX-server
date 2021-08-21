#!/bin/bash
# Management commands for running stuff in Docker

set -o errexit
set -o pipefail
set -o nounset

function run_and_commit {
    # Run commands in a container and commit that container locally
    CNAME=p0sx-server$("${BASH_SOURCE%/*}"/pwgen.sh | head -c 12)
    docker-compose run --name "$CNAME" server "$@"
    docker commit "$CNAME" p0sx-server:latest
    docker rm "$CNAME"
}

function pip-sync {
  # Sync pip requirements in local image
  run_and_commit pip-sync requirements/dev.txt
}

function pip-compile {
  # Resolve and compile pip requirements
  docker-compose run --rm server compile-pip
}

function pip-update-req {
  pip-compile
  pip-sync
}

"$@"
