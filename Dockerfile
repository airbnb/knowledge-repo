# Using officially supported Ubuntu version for Travis CI
FROM ubuntu:14.04

ARG TRAVIS_PYTHON_VERSION

# Install required Ubuntu packages
RUN apt-get update
RUN apt-get install -y wget
RUN apt-get install -y git

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

# Copy our code from the current folder to /app inside the container
ADD . /app

# Install python dependencies
RUN pip install -r requirements.txt

# Ready dependencies to use IpynbFormat instances
RUN pip install --ignore-installed --upgrade nbformat nbconvert[execute] traitlets
