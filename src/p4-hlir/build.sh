#!/bin/bash -x

pushd p4-hlir
python setup.py --command-packages=stdeb.command bdist_deb
popd

cp p4-hlir/deb_dist/*.deb ../
