#! /usr/bin/env bash

JAVA="java"

mkdir -p $JAVA/pasket/java
mkdir -p $JAVA/pasket/javax

cp -rf $JAVA/java $JAVA/pasket/
cp -rf $JAVA/javax $JAVA/pasket/

rm -rf $JAVA/java
rm -rf $JAVA/javax

for i in `find "$JAVA/pasket" -type f -name '*java'`;
do

  sed -i -e 's/package java.util;/package pasket.java.util;/' $i
  sed -i -e 's/java.util.EventObject/pasket.java.util.EventObject/' $i

  sed -i -e 's/java.awt/pasket.java.awt/' $i
  sed -i -e 's/javax.swing/pasket.javax.swing/' $i
  sed -i -e 's/javax.accessibility/pasket.javax.accessibility/' $i

done
