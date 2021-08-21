#!/bin/bash
# Simple oneliner to generate an URL-safe password with high entropy
echo "$(head /dev/urandom | base64 | sed s/[^a-zA-Z0-9]//g | head -c 64)"
