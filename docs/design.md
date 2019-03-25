# Design

Order of discovery for each Config:

1. Field Sources
2. Config Sources
3. Parent Config


Imagined Usage:

**app.py**

    from config import conf

    foo = conf["foo"]
    bar = conf.bar


**config.py**

    from typing import List
    from config_composer import Config, Sources
    from config_composer.sources import Env, Default

    class Base(Config):
        __sources__ = [
            Env(prefix="NOZZLE_"),  # Check first
            Env(),                  # Checked second
        ]


    # export NOZZLE_FOO="Foo"
    # export NOZZLE_BAR="foo,bar,baz"
    # export BAR="Ignore Me"
    # export XOR="foo,bar,baz"
    class Dev(Config):
        foo: str
        bar: List[str]
        xor: str
        woop: str = "Default"


    # export NOZZLE_FOO="Foo"
    # export NOZZLE_BAR="foo,bar,baz"
    class Test(Config):
        __sources__ = [
            Env(prefix="TEST_NOZZLE_"),  # Check second
            Env(prefix="NOZZLE_"),       # Check third
            Env(),                       # Check fourth
        ]
        foo: str = Sources(
            AWS(),                       # Check first
        )
        bar: List[str] = (
            AWS(),                       # Check first
            "Default",                   # Check next, always succeeds, blocks other sources
        )
        xor: str
        woop: str = Default(
            Source(
                AWS(),                   # Check first
            ),
            "Default",                   # Check last in Test, blocks parent config sources
        )


    class Config(Selector):
        __prefix__ = "NOZZLE_"

        DEV = DEV
        TEST = TEST
        PROD= PROD


    conf = Config()
