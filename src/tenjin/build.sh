#!/bin/bash -x

wget -nc http://pypi.python.org/packages/source/T/Tenjin/Tenjin-1.1.1.tar.gz
tar xzf Tenjin-1.1.1.tar.gz
pushd Tenjin-1.1.1
python setup.py --command-packages=stdeb.command bdist_deb
popd
cp Tenjin-1.1.1/deb_dist/*.deb ../
