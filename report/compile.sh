#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd $DIR

FILENAME=${1:-main}

echo Compiling $FILENAME.

cmd="pdflatex -interaction=nonstopmode -shell-escape"

./write_log.sh

$cmd   $FILENAME.tex
bibtex $FILENAME.aux
$cmd   $FILENAME.tex

popd

exit 0
