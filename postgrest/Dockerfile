FROM debian:stretch-slim

ENV POSTGREST_VERSION "v6.0.2"

# Install libpq5
RUN apt-get -qq update && \
    apt-get -qq install -y --no-install-recommends libpq5 && \
    apt-get -qq clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install postgrest
RUN BUILD_DEPS="curl ca-certificates xz-utils" && \
    apt-get -qq update && \
    apt-get -qq install -y --no-install-recommends $BUILD_DEPS && \
    cd /tmp && \
    curl -SLO https://github.com/PostgREST/postgrest/releases/download/${POSTGREST_VERSION}/postgrest-${POSTGREST_VERSION}-ubuntu.tar.xz && \
    tar -xJvf postgrest-${POSTGREST_VERSION}-ubuntu.tar.xz && \
    mv postgrest /usr/local/bin/postgrest && \
    cd / && \
    apt-get -qq purge --auto-remove -y $BUILD_DEPS && \
    apt-get -qq clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY postgrest.conf /etc/postgrest.conf

ENV PGRST_DB_URI=postgres://univerdustry:univerdustry@localhost:5432/univerdustry
ENV PGRST_DB_SCHEMA=public
ENV PGRST_DB_ANON_ROLE=univerdustry
ENV PGRST_DB_POOL=100
ENV PGRST_DB_EXTRA_SEARCH_PATH=public

RUN groupadd -g 1000 postgrest && \
    useradd -r -u 1000 -g postgrest postgrest && \
    chown postgrest:postgrest /etc/postgrest.conf

USER 1000

# PostgREST reads /etc/postgrest.conf so map the configuration
# file in when you run this container
CMD exec postgrest /etc/postgrest.conf

EXPOSE 3000
