# Design

Order of discovery for each Config:

1. Field Sources
2. Config Sources
3. Parent Config


Imagined Usage:

**runtime**

    export MY_APP_CONFIG=test
    python run app.py


**app.py**

    from config import conf

    foo = conf["foo"]
    bar = conf.bar


**config.py**

    from typing import List
    from config_composer import Config, Sources, Composer
    from config_composer.sourcese.env import Env, Default
    from config_composer.sources import aws

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


    # class Conf(Composer):
    #     __prefix__ = "MY_APP_"
    #     dev = (Dev, Base)
    #     test = (Test, Dev, Base)
    #     prod = (Base, Prod)
    #
    # conf = Conf()

    from marshmallow import Schema, fields
    class ConfSchema(Schema):
        foo = fields.Str(required=True)
        bar = fields.Int(required=True)
        xor = fields.Bool(required=True)
        woop = fields.Str(required=True)


    conf = Composer(
        prefix="MY_APP_",  # MY_APP_CONFIG
        schema=ConfSchema(),
        configs={
            "dev": (Dev, Base),
            "test": (Test, Dev, Base),
            "prod": (Prod, Base),
        }
    )
