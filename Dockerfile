FROM ubuntu:16.04

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python-pip python-dev build-essential 
RUN apt-get -y install git
RUN apt-get -y install ssh

RUN pip install --upgrade pip
RUN pip install git+https://github.com/airbnb/knowledge-repo.git

WORKDIR /knowledge

CMD ["/bin/bash"]
