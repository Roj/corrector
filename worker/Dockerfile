FROM python:3.6
# Install java.
RUN \
  apt-get update && \
  apt-get install -y openjdk-8-jdk && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /worker 
# At first, we only add the necessary files to install the python
# packages. This allows docker to cache the image and not download
# them every time.
ADD requirements.txt /worker
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# Copy our current directory.
ADD . /worker

RUN python3 --version
RUN ls /worker
ENTRYPOINT ["/worker/entry.py"]
#CMD ["bash"]
