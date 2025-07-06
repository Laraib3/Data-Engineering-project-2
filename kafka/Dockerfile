FROM apache/airflow:2.7.1

USER root

# Install OpenSSL and other required dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libssl-dev \
        openssl \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python packages
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt 