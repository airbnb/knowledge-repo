FROM ubuntu:18.04

MAINTAINER perryism
 
RUN apt-get update && \
    apt-get -y install \
	wget \
	zip \
	python3-pip \
	python3-dev \
	git \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 install --upgrade pip \
    && rm -rf /var/lib/apt/lists/* 

ARG VERSION=0.9.0

RUN wget https://github.com/airbnb/knowledge-repo/archive/v$VERSION.zip && \
    unzip v$VERSION.zip -d /app

WORKDIR /app/knowledge-repo-$VERSION

COPY . /app/knowledge-repo-$VERSION

RUN pip3 install -r docker/requirements.txt

COPY docker/entrypoint.sh /app/knowledge-repo-$VERSION

VOLUME /data

EXPOSE 7000

CMD ["bash", "./entrypoint.sh"]
