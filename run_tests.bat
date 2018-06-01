IF NOT DEFINED PYTHON (SET PYTHON=python)

REM Setting up test environment

REM - Removing artifacts from previous testing...
if exist "tests\knowledge.db" (
  DEL tests\knowledge.db
)
if exist ".coverage" (
  DEL .coverage
)

REM Run pep8 tests
%PYTHON%\\python.exe -m pycodestyle knowledge_repo scripts tests setup.py --exclude knowledge_repo/app/migrations,tests/test_repo --ignore=E501,E722,W504

REM Create fake repository and add some sample posts.
REM We use a fake repository here to speed things up, and to avoid using git in test environments
REM Once we ship a public version, this should be changed to use the actual init methods
SET test_repo_path=tests\test_repo

REM Creating a test repository in %test_repo_path%...
REM Remove the repository if it already exists
IF EXIST "%test_repo_path%" (
  RMDIR /Q /S %test_repo_path%
)

%PYTHON%\\python.exe scripts/knowledge_repo --repo="${test_repo_path}" init
COPY tests\config_repo.yml %test_repo_path%\.knowledge_repo_config.yml

PUSHD %test_repo_path%
  git config user.email "knowledge_developer@example.com"
  git config user.name "Knowledge Developer"
  git add .knowledge_repo_config.yml
  git commit -m "Update repository config."
POPD

# Add some knowledge_posts
%PYTHON%\\python.exe scripts/knowledge_repo --repo="%test_repo_path%" --dev add knowledge_repo/templates/knowledge_template.ipynb -p projects/test/ipynb_test -m "Test commit" --branch master
%PYTHON%\\python.exe scripts/knowledge_repo --repo="%test_repo_path%" --dev add knowledge_repo/templates/knowledge_template.Rmd -p projects/test/Rmd_test -m "Test commit" --branch master
%PYTHON%\\python.exe scripts/knowledge_repo --repo="%test_repo_path%" --dev add knowledge_repo/templates/knowledge_template.md -p projects/test/md_test -m "Test commit" --branch master

REM "Running regression test suite"
%PYTHON%\\python.exe -m nose --with-coverage --cover-package=knowledge_repo --verbosity=1
