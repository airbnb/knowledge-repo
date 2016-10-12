FROM ubuntu:16.04

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python-pip python-dev build-essential 
RUN apt-get -y install git
RUN apt-get -y install ssh

RUN pip install --upgrade pip
RUN pip install knowledge-repo

WORKDIR /knowledge

EXPOSE 7000

CMD ["/bin/bash"]
