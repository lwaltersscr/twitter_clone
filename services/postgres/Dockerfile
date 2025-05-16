FROM postgres:15

# Install build dependencies and RUM extension
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        git \
        postgresql-server-dev-15 \
        systemtap-sdt-dev \
    && cd /tmp \
    && git clone https://github.com/postgrespro/rum \
    && cd rum \
    && make USE_PGXS=1 \
    && make USE_PGXS=1 install \
    && apt-get remove -y \
        build-essential \
        git \
        postgresql-server-dev-15 \
        systemtap-sdt-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# Copy schema file
COPY schema.sql /docker-entrypoint-initdb.d/ 