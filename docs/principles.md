# Principles

1. Separation of config from code
    - all settings live in one config object
2. Applications should know and set:
    - what settings it needs
    - how to validate those settings
    - ~~best guess at where settings should be sourced from~~
3. Deployer should know and set:
    - where the settings should be sourced from
4. Values vs. Secrets
    -
5. Static vs. Dynamic
    - setting should know if they change
    - _if they can_, then they should communicate to the application _when they do_


## Start-up

- Hard Fail if _Value_ un-fetchable;
- Unless this is explicitly overriden


## Mutable Values

Some _Sources_ can provide values with change.

- Warn if a new _Value_ is un-fetchable;
- Unless this is explicitly overriden


## Remote Sources

- Implicity retry on:
    - transport failures
    - connections failures


## Typing


## Validation
