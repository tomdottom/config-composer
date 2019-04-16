# Design

Configuration object is created using two files:

The first containing the config specification file:
- part of the app
- defines the config value types
- validates the config values
- a python file

The second containing the config source files:
- created/selected at deployment
  - deployments to different systems can specify sources as needed
- can be composed of multiple files
- supports many types to files

## Example

An application `config.py` defines the config values, types,
and validation requirements in the `ConfigSpec`.

The `ConfigSource` object creates an instance which lets the
application access config values from a variety of sources.


**app/config.py**

    class ConfigSpec:
        foo: str
        bar = params.String(
            validator=Length(min=10, max=20)
        )
        baz: bool

    config = ConfigSource(
        schema=ConfigSchema
    )

Sources can be defined in a variety of files to make it easier
and flexible for DevOps. For example `.py`, `.yaml`, `*.ini`.

**source_spec.py**

    class AppEnv(sources.Env):
        prefix = "MY_APP_"


    class SourceSpec:
        foo = sources.Env(path="FOO")                 # FOO
        bar = AppEnv(path="BAR")                      # MY_APP_BAR
        baz = sources.Env(path="BAZ", prefix="APP_")  # APP_BAZ

**source_spec.yaml**

    sources:
        AppEnv:
            source: Env
            prefix: MY_APP_

    parameters:
        foo:
            (): Env
            path: FOO
        bar:
            (): AppEnv
            path: FOO
        baz:
            (): Env
            path: FOO
            prefix: APP_

**source_spec.ini**

    [source_AppEnv]
    source=Env
    prefix = "MY_APP_"

    [value_foo]
    source=Env
    args=("FOO",)

    [value_bar]
    source=AppEnv
    args=("BAR",)

    [value_baz]
    source=Env
    args=("BAZ", "APP_")
