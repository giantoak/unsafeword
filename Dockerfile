# Dockerfile for setting up Docker container with MiniConda and an
# example app.
# Copied from http://pythonwise.blogspot.com/2015/04/docker-miniconda-perfect-match.html

FROM ubuntu:latest
MAINTAINER Pete[r] M. Landwehr <peter.landwehr@giantoak.com>

# System packages
RUN apt-get update && apt-get install -y curl

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
RUN bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

# Python packages from conda
RUN conda config --add channels memex
RUN conda create -n unsafeword --file requirements.txt
RUN source activate unsafeword

# Setup application
COPY app.py /
ENTRYPOINT ["/miniconda/bin/python", "/app.py"]
EXPOSE 8080
