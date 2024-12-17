#!/bin/bash

docker run -d -p 9099:9099 -e OPENAI_API_KEY="$OPENAI_API_KEY" --add-host=host.docker.internal:host-gateway -v pipelines:/app/pipelines --name pipelines --restart always ghcr.io/open-webui/pipelines:main
