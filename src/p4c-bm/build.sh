#!/bin/bash -x

pushd p4c-bm
python setup.py --command-packages=stdeb.command bdist_deb
popd

cp p4c-bm/deb_dist/*.deb ../
