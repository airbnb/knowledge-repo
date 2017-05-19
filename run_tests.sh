#!/usr/bin/env bash

echo
echo "Setting up test environment"
echo "---------------------------"
echo

echo "Removing artifacts from previous testing..."
rm tests/knowledge.db &> /dev/null
rm -f .coverage &> /dev/null

# Exit script if any command returns a non-zero status hereonin
set -e

# Run pep8 tests
pep8 --exclude knowledge_repo/app/migrations,tests/test_repo,build,deploy,kube,docs --ignore=E501 .

# Create fake repository and add some sample posts.
# We use a fake repository here to speed things up, and to avoid using git in test environments
# Once we ship a public version, this should be changed to use the actual init methods
test_repo_path="`dirname $0`/tests/test_repo"

echo "Creating a test repository in ${test_repo_path}..."
# Remove the repository if it exists
rm -rf ${test_repo_path} &> /dev/null

# `dirname $0`/scripts/knowledge_repo --repo="${test_repo_path}" init # TODO: USE THIS AGAIN
mkdir -p ${test_repo_path} &> /dev/null
cp `dirname $0`/tests/config_repo.py ${test_repo_path}/.knowledge_repo_config.py &> /dev/null

pushd ${test_repo_path} &> /dev/null
git init &> /dev/null
git config user.email "knowledge_developer@example.com" &> /dev/null
git config user.name "Knowledge Developer" &> /dev/null
git add .knowledge_repo_config.py &> /dev/null
git commit -m "Initial commit." &> /dev/null
popd &> /dev/null

# Add some knowledge_posts
`dirname $0`/scripts/knowledge_repo --repo="${test_repo_path}" --dev add `dirname $0`/knowledge_repo/templates/knowledge_template.ipynb -p projects/test/ipynb_test -m "Test commit" --branch master
`dirname $0`/scripts/knowledge_repo --repo="${test_repo_path}" --dev add `dirname $0`/knowledge_repo/templates/knowledge_template.Rmd -p projects/test/Rmd_test -m "Test commit" --branch master
`dirname $0`/scripts/knowledge_repo --repo="${test_repo_path}" --dev add `dirname $0`/knowledge_repo/templates/knowledge_template.md -p projects/test/md_test -m "Test commit" --branch master

for post in $(ls `dirname $0`/tests/test_posts); do
    if [[ "${post}" == *.ipynb ]] || [[ "${post}" == *.org ]] ; then
        `dirname $0`/scripts/knowledge_repo --repo="${test_repo_path}" --dev add `dirname $0`/tests/test_posts/${post} -p projects/${post} -m "Test commit" --branch master;
    fi;
done

echo
echo "Running regression test suite"
echo "-----------------------------"
echo
nosetests --with-coverage --cover-package=knowledge_repo --verbosity=1 -a '!notest'
