FROM openjdk:8-alpine
# Note - the dockerfile must be run from the root repository directory!
WORKDIR /var/www/

# SOFTWARE PACKAGES
#   * musl: standard C library
#   * lib6-compat: compatibility libraries for glibc
#   * linux-headers: commonly needed, and an unusual package name from Alpine.
#   * build-base: used so we include the basic development packages (gcc)
#   * bash: so we can access /bin/bash
#   * ca-certificates: for SSL verification during Pip and easy_install
#   * freetype: library used to render text onto bitmaps, and provides support font-related operations
#   * libgfortran: contains a Fortran shared library, needed to run Fortran
#   * libgcc: contains shared code that would be inefficient to duplicate every time as well as auxiliary helper routines and runtime support
#   * libstdc++: The GNU Standard C++ Library. This package contains an additional runtime library for C++ programs built with the GNU compiler
#   * openblas: open source implementation of the BLAS(Basic Linear Algebra Subprograms) API with many hand-crafted optimizations for specific processor types
#   * libssl1.0: SSL shared libraries
ENV PACKAGES="\
    dumb-init \
    musl \
    libc6-compat \
    linux-headers \
    build-base \
    bash \
    ca-certificates \
    freetype \
    libgfortran \
    libgcc \
    libstdc++ \
    openblas \
    libssl1.0 \
"

ENV PYTHON_PACKAGES="\
    numpy \
    scipy \
    pandas \
    pyspark \
" 

RUN apk add --no-cache --virtual build-dependencies python3 \
    && apk add --virtual build-runtime \
    build-base python3-dev openblas-dev freetype-dev pkgconfig gfortran \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && ln -sf pip3 /usr/bin/pip \
    && rm -r /root/.cache \
    && pip install --no-cache-dir --default-timeout=1000 $PYTHON_PACKAGES \
    && apk del build-runtime \
    && apk add --no-cache --virtual build-dependencies $PACKAGES \
    && rm -rf /var/cache/apk/*


WORKDIR /worker 

# Copy the worker directory.
ADD worker/ /worker
ADD guias/entradas/ /worker/datos

EXPOSE 6000/tcp

ENTRYPOINT ["/worker/entry.py"]
