FROM ubuntu:18.04

LABEL description="knowledge-repo service"

# Define some build time variables
ARG PIP=pip3
ARG VERSION=0.9.1

# Install required tools and libraries
RUN apt-get update && \
    apt-get -y install \
    wget \
    zip \
    python3-pip \
    python3-dev \
    git \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && ${PIP} install --upgrade pip \
    && rm -rf /var/lib/apt/lists/* 

# Install the latest version of knowledge-repo
RUN wget https://github.com/airbnb/knowledge-repo/archive/v$VERSION.zip && \
    unzip v$VERSION.zip -d /app

COPY . /app/knowledge-repo-$VERSION

COPY docker/entrypoint.sh /app/knowledge-repo-$VERSION

RUN ${PIP} install -r /app/knowledge-repo-$VERSION/docker/requirements.txt

WORKDIR /app/knowledge-repo-$VERSION

VOLUME /data

EXPOSE 7000

CMD ["bash", "./entrypoint.sh"]
