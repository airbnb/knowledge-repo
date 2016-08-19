#!/usr/bin/env bash

rm tests/knowledge.db
rm -f .coverage

# Exit script if any command returns a non-zero status
set -e

# Run pep8 tests
pep8 --exclude knowledge_repo/app/migrations,tests/test_repo,build --ignore=E501 .

# See if package will build
#python2 setup.py bdist

# Create fake repository and add some sample posts.
# We use a fake repository here to speed things up, and to avoid using git in test environments
# Once we ship a public version, this should be changed to use the actual init methods
test_repo_path="`dirname $0`/tests/test_repo"

# Remove the repository if it exists
rm -rf ${test_repo_path}

# `dirname $0`/scripts/knowledge_repo --repo="${test_repo_path}" init
mkdir -p ${test_repo_path}
cp `dirname $0`/tests/config_repo.py ${test_repo_path}/.knowledge_repo_config.py

pushd ${test_repo_path}
git init
git config user.email "knowledge_developer@example.com"
git config user.name "Knowledge Developer"
git add .knowledge_repo_config.py
git commit -m "Initial commit."
popd

# Add some knowledge_posts
`dirname $0`/scripts/knowledge_repo --repo="${test_repo_path}" --dev add `dirname $0`/knowledge_repo/templates/knowledge_template.ipynb -p projects/test/ipynb_test -m "Test commit" --branch master
`dirname $0`/scripts/knowledge_repo --repo="${test_repo_path}" --dev add `dirname $0`/knowledge_repo/templates/knowledge_template.Rmd -p projects/test/Rmd_test -m "Test commit" --branch master
`dirname $0`/scripts/knowledge_repo --repo="${test_repo_path}" --dev add `dirname $0`/knowledge_repo/templates/knowledge_template.md -p projects/test/md_test -m "Test commit" --branch master

# Run nosestests in python2
python `which nosetests` --with-coverage --cover-package=knowledge_repo --verbosity=3 --nocapture -a '!notest'
