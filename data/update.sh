#!/bin/bash
s3cmd get --recursive --skip-existing s3://appearin-kissmetrics kissmetrics
s3cmd get --force s3://appearin-kissmetrics/* kissmetrics
