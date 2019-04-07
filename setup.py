import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="config-composer",
    version="0.0.1",
    packages=find_packages(),
    long_description=README,
    long_description_content_type="text/markdown",
    setup_requires=[],
    install_requires=[],
    tests_require=[],
    extras_require={"AWS": ["boto3"], "Vault": ["hvac"]},
)
