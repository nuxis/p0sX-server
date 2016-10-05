#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "Give me a version!"
    exit 1
fi

echo "VERSION = $1" > version.py
git add version.py
git commit -m "Releases version $1"
git tag $1
git push origin $1
