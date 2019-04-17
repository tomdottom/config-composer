# Simple Server Example

## Run in test

    export SOURCE_SPEC_PATH='./source_specs/test.ini,./source_specs/defaults.ini'
    python server.py

## Run in prod

    export SIMPLE_SERVER_PORT=8080
    export SOURCE_SPEC_PATH='./source_specs/prod.ini,./source_specs/defaults.ini'
    python server.py
