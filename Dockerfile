FROM ubuntu:16.04

ARG TRAVIS_PYTHON_VERSION
ARG PORT

# Install required Ubuntu packages
RUN apt-get update
RUN apt-get install -y wget
RUN apt-get install -y bzip2
RUN apt-get install -y git

# Set the locale
RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Download appropriate version of Miniconda
RUN if [[ "$TRAVIS_PYTHON_VERSION" == "2.7" ]]; then wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh; \
else wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh; fi

# Install Miniconda
RUN bash miniconda.sh -b -p /miniconda
ENV PATH=/miniconda/bin:${PATH}
RUN hash -r

# Set up conda package installer
RUN conda config --set always_yes yes --set changeps1 no
RUN conda update -q conda

# Useful for debugging any issues with conda
RUN conda info -a

# Install R
RUN conda install -c r r
RUN conda install -c r r-knitr

# Set the application directory
WORKDIR /app

# Install python dependencies - do this before adding rest of code to allow docker to cache this step
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy our code from the current folder to /app inside the container
ADD . /app

# Run project installation scripts
RUN python setup.py develop

# Ready dependencies to use IpynbFormat instances
RUN pip install --ignore-installed --upgrade nbformat nbconvert[execute] traitlets

# Set up to use a new empty repo until configured otherwise
RUN ./scripts/knowledge_repo --repo ./default_repo init
ENV KNOWLEDGE_REPO=./default_repo

EXPOSE ${PORT}
ENV PORT=${PORT}

# Deploy via gunicorn as standard startup command
CMD ["bash", "-c", "./scripts/knowledge_repo deploy --port ${PORT}"]
