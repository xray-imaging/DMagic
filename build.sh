#!/bin/bash
cp -r $RECIPE_DIR/data_management data_management
cd data_management

$PYTHON setup.py install
