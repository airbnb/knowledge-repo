


sudo apt install python3.10-venv

PYTHON_VERSION=$(python3 -V | awk '{print $2}')


echo -e "\033[1;34m* \033[0mUsing venv as version manager with Python ${PYTHON_VERSION}"

echo
echo -e "\033[1;35m* \033[0mCreating venv virtual environment in ./venv"
python -m venv venv

echo
echo -e "\033[1;35m* \033[0mActivating the venv"
source ./venv/bin/activate

echo
echo -e "\033[1;35m* \033[0mInstalling dependencies"
pip install --upgrade pip
pip install --upgrade "knowledge-repo[all]"

sudo apt install nginx

sudo apt install postgresql-client-common


knowledge_repo --repo /home/ubuntu/knowledge-repo.com  runserver --config config.py