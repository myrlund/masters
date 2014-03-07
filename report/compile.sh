#!/bin/bash

FILENAME=${1:-main}

echo Compiling $FILENAME.

cmd="pdflatex -interaction=nonstopmode -shell-escape"

$cmd   $FILENAME.tex
bibtex $FILENAME.aux
$cmd   $FILENAME.tex

exit 0
