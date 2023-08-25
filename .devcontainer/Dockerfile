FROM ubuntu:focal
ARG PYTHON_PACKAGES="\
python3.8 python3.8-distutils python3.8-venv \
python3.9 python3.9-distutils python3.9-venv \
python3.10 python3.10-distutils python3.10-venv \
python3.11 python3.11-distutils python3.11-venv \
python3.12 python3.12-distutils python3.11-venv \
"

# Base utils
RUN apt-get update && apt-get install --no-install-recommends -yq software-properties-common
RUN apt-get -yq install git

# Python versions
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update
RUN apt-get install -yq --no-install-recommends ${PYTHON_PACKAGES}

# Fish shell
RUN apt-add-repository ppa:fish-shell/release-3 && apt update
RUN apt-get -yq install fish

SHELL ["fish", "--command"]
RUN chsh -s /usr/bin/fish
ENV SHELL /usr/bin/fish
ENTRYPOINT ["fish"]
