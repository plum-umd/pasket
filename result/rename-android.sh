#! /usr/bin/env bash

JAVA="java"

for i in `find "$JAVA" -type f -name '*java'`;
do
  sed -i '' 's/ android./ symdroid.model.android./' $i
  sed -i '' 's/ com.android./ symdroid.model.com.android./' $i
done
