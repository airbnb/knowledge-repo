#! /usr/bin/env bash

set -e

# Set up arguments
while test $# -gt 0
do
    case "$1" in
        -h|--help)
            echo -e "\033[1;32m* \033[0mKnowledge Repo"
            echo
            echo "USAGE: ./setup.sh [OPTIONS]"
            echo
            echo "OPTIONS"
            echo -e " -h or --help\t\tdisplay this help message"
            exit 0
            ;;
    esac
    shift
done

echo
echo -e "\033[1;34m* \033[0mEnv Preparation"
sudo apt-get update -y1
sudo apt install software-properties-common -y1
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.9 -y1
sudo apt-get install python3.9-venv -y1

PYTHON_VERSION=$(python3 -V | awk '{print $2}')

echo
echo -e "\033[1;34m* \033[0mUsing venv as version manager with Python ${PYTHON_VERSION}"

echo
echo -e "\033[1;34m* \033[0mDownload knowledge-repo"
git clone https://github.com/airbnb/knowledge-repo.git

echo
echo -e "\033[1;34m* \033[0mDownload default config"
wget -O config.py https://raw.githubusercontent.com/airbnb/knowledge-repo/master/knowledge_repo/app/config_defaults.py


echo
echo -e "\033[1;34m* \033[0mSetup Default Postgresql"
sudo apt install postgresql -y1
sudo su postgres
psql -U postgres -c "CREATE ROLE knowledge_repo;"
psql -U postgres -c "ALTER ROLE  knowledge_repo  WITH LOGIN;"
psql -U postgres -c "ALTER USER  knowledge_repo  CREATEDB;"
psql -U postgres -c "ALTER USER  knowledge_repo  WITH PASSWORD 'password';"
psql -U postgres -c "CREATE DATABASE knowledge_repo;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE knowledge_repo TO knowledge_repo;"
exit

echo
echo -e "\033[1;35m* \033[0mCreating venv virtual environment in ./venv"
python3 -m venv venv

echo
echo -e "\033[1;35m* \033[0mActivating the venv"
source ./venv/bin/activate

echo
echo -e "\033[1;35m* \033[0mInstalling dependencies"
pip install --upgrade pip
pip install -r requirements.txt