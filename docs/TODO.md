# TODO

# General

- better logging

# AWS Parameter

- handle connection failures


# Vault Secret

- handle connection failures


# Remote Sources
*running*

    export SOURCE_SPEC_PATH="https://example.com/source_spec.ini"

*config.py*
    class ConfigSpec(Spec):
        foo: str

    config = Config(config_spec=ConfigSpec, env_var="SOURCE_SPEC_PATH")
