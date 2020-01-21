#!/usr/bin/env bash
set -e
docker build -t vapi .
docker run -p 5000:5000 vapi
