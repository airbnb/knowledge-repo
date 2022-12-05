#! /usr/bin/env bash

set -e

# Set up arguments
while test $# -gt 0
do
    case "$1" in
        -h|--help)
            echo -e "\033[1;32m* \033[0mKnowledge Repo V2"
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

PYTHON_VERSION=$(python3 -V | awk '{print $2}')


echo -e "\033[1;34m* \033[0mUsing venv as version manager with Python ${PYTHON_VERSION}"

echo
echo -e "\033[1;35m* \033[0mCreating venv virtual environment in ./venv"
python3 -m venv venv

echo
echo -e "\033[1;35m* \033[0mActivating the venv"
source ./venv/bin/activate

echo
echo -e "\033[1;35m* \033[0mInstalling dependencies"
pip3 install --upgrade pip3
pip3 install -r requirements.txt

# echo
# echo -e "\033[1;35m* \033[0mInstalling pre-commit"
# pre-commit install

# echo
# echo -e "\033[1;31m* \033[0mMake sure to activate the venv in your shell: source ./venv/bin/activate"
# echo
# echo -e "\033[1;32m* \033[0mKnowledge Repo V2 Setup - Enjoy 🚀"