#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
git log --pretty=format:'\item[%ad] %s%d \\' --date=short --no-merges -- "$DIR/*.tex" > $DIR/log.txt
echo >> $DIR/log.txt