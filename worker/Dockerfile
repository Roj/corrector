FROM python:3.6
# Note - the dockerfile must be run from the root repository directory!
# Install java.
RUN \
  apt-get update && \
  apt-get install -y openjdk-8-jdk && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /worker 
# At first, we only add the necessary files to install the python
# packages. This allows docker to cache the image and not download
# them every time.
ADD worker/requirements.txt /worker
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# Copy the worker directory.
ADD worker/ /worker
ADD guias/entradas/ /worker/datos

EXPOSE 6000/tcp

ENTRYPOINT ["/worker/entry.py"]
