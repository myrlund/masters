#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

s3cmd get --recursive --skip-existing s3://appearin-kissmetrics $DIR/kissmetrics
s3cmd get --force s3://appearin-kissmetrics/* $DIR/kissmetrics

