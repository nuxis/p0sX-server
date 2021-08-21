#!/bin/bash
# Load and set environment variables from an env file

source $1
export $(cut -d= -f1 $1 | grep -v '^#')