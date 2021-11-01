FROM python:3.9-slim-buster

LABEL MAINTAINER="Broad Institute DSDE <dsde-engineering@broadinstitute.org>" 

ENV PATH $PATH:/root/google-cloud-sdk/bin 

WORKDIR /tools

COPY . .

RUN set eux; \
        apt-get update; \
        apt-get install -y \
            bash \
            curl \
            git \
            jq \
            wget \
    ; \
# Upgrade pip
pip3 install --upgrade pip \
    ; \
# Install adapter_tools
pip3 install . --trusted-host github.com \
    ; \
# Install gsutil
curl -sSL https://sdk.cloud.google.com | bash \
    ; \
# Install tini
    wget https://github.com/krallin/tini/releases/download/v0.19.0/tini -O /sbin/tini; \
    chmod +x /sbin/tini \
    ; \
# Clean up cached files
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set tini as default entrypoint
ENTRYPOINT [ "/sbin/tini", "--" ]