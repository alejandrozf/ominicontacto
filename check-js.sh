#!/bin/bash

# Basado en https://gist.github.com/linhmtran168/2286aeafe747e78f53bf

TARGET_BRANCH_SHA=`git rev-parse origin/${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}`

STAGED_FILES=`git diff $TARGET_BRANCH_SHA...HEAD --name-only --diff-filter=ACM | grep ".*\.js$"`

if [[ "$STAGED_FILES" = "" ]]; then
  exit 0
fi

PASS=true

echo "\nValidating Javascript code:\n"

# Check for eslint
which eslint &> /dev/null
if [[ "$?" == 1 ]]; then
  echo "Please install ESlintm"
  exit 1
fi

for FILE in $STAGED_FILES
do
  eslint "$FILE"

  if [[ "$?" == 0 ]]; then
    echo "ESLint Passed: $FILE"
  else
    echo "ESLint Failed: $FILE"
    PASS=false
  fi
done

echo "\nJavascript validation completed!\n"

if ! $PASS; then
  echo "COMMIT FAILED:\033[0m Your commit contains files that should pass ESLint but do not. Please fix the ESLint errors and try again.\n"
  exit 1
else
  echo "COMMIT SUCCEEDED"
fi

exit $?
