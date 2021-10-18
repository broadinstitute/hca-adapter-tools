FROM python:3.9-alpine

LABEL MAINTAINER="Broad Institute DSDE <dsde-engineering@broadinstitute.org>" 

ENV PATH $PATH:/root/google-cloud-sdk/bin

WORKDIR /tools

COPY . .

RUN set eux;\
        apk add --no-cache \
            bash \
            curl \
            git \
            jq \
            tini \
    ; \
# Install adapter_tools
pip install . --trusted-host github.com \
    ; \
# Install gsutil
curl -sSL https://sdk.cloud.google.com | bash

# Set tini as default entrypoint
ENTRYPOINT [ "/sbin/tini", "--" ]