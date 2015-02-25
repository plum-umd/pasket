#! /usr/bin/env bash

if [ "$#" -ne 1 ]; then
  echo "a path to sketch files is required"
  exit -1
fi

sketch --fe-inc $1 $1/sample.sk -V 10 --fe-keep-tmp --fe-tempdir tmp
sketch --fe-inc $1 $1/sample.sk -V 10 --fe-keep-tmp --fe-tempdir tmp --debug-fake-solver --fe-output-test
sed -i '' 's/\(g\+\+\)/\1 -g -I \"$SKETCH_HOME\/src\/runtime\/include\"/g' script
chmod +x script
mv script tmp/
mv *.h tmp/
mv *.cpp tmp/
