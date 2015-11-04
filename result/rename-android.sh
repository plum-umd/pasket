#! /usr/bin/env bash

JAVA="java"

for i in `find "$JAVA" -type f -name '*java'`;
do
  sed -i -e 's/ android./ symdroid.model.android./' $i
  sed -i -e 's/ com.android./ symdroid.model.com.android./' $i

  rm -f "$i-e"
done
