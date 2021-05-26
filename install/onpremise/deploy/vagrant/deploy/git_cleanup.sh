#!/bin/bash

cd /home/ftsinfra/ominicontacto
git checkout install/
git checkout develop
git branch -D $CI_COMMIT_REF_NAME
git fetch
git checkout $CI_COMMIT_REF_NAME
git pull origin $CI_COMMIT_REF_NAME
rm -rf modules
git submodule update --remote
