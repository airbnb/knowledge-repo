FROM ubuntu:16.04

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python3-pip python3-dev build-essential 
RUN apt-get -y install git
RUN apt-get -y install ssh

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade "knowledge-repo[all]==0.6.6"

WORKDIR /knowledge

EXPOSE 7000

CMD ["/bin/bash"]
