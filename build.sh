#!/bin/bash
cp -r $RECIPE_DIR/src src
cd src

$PYTHON setup.py install
