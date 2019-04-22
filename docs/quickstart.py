from config_composer.core import Spec, Config
from config_composer.core.utils import preload
from config_composer.sources.env import Env
from config_composer.sources import aws, vault, files
from config_composer.sources.default import Default


class ConfigSpec(Spec):
    foo: str
    bar: int
    baz: str


class SourceSpec:
    foo = Env("FOO")
    bar = aws.Parameter(path="/foo/bar/baz")
    baz = vault.Secret(path="/foo/bar/baz", field="my-secret")
    qux = files.DotEnvFile(path="FOO", dotenv_path="/app/config/.prod-env")
    wat = Default(value="wat")


config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

if __name__ == "__main__":
    preload(config)

    env_foo = config.foo
    bar_foo = config["bar"]
    env_baz = config.get("baz")
