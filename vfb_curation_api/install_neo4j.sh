#!/usr/bin/env bash

mkdir -p tmp
cd tmp
rm -rf VFB_neo4j
git clone --quiet https://github.com/VirtualFlyBrain/VFB_neo4j.git
cd ..
rm -rf vfb/*
cp -r tmp/VFB_neo4j/src/uk vfb