#!/bin/bash

cd /home/ftsinfra/ominicontacto
git checkout deploy/ansible/inventory
git checkout develop
git fetch
git branch -D $CI_COMMIT_REF_NAME
git checkout $CI_COMMIT_REF_NAME
git pull origin $CI_COMMIT_REF_NAME
