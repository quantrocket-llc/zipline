#!/bin/bash

if [[ "$OSTYPE" == "darwin"* ]]; then
    find -E zipline -regex '.*\.(c|so)' -exec rm {} +
else
    find zipline -regex '.*\.\(c\|so\)' -exec rm {} +
fi
python setup.py build_ext --inplace
