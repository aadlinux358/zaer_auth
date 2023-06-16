#! /usr/bin/env bash

poetry export -o requirements.txt --without-hashes
docker build -t aadlinux358/zaer-hr-backend:latest .
