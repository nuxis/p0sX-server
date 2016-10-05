#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "Give me a version!"
    exit 1
fi

echo "VERSION = $1" > version.py
git tag $1
git push origin $1
