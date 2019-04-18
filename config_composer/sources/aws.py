from textwrap import dedent
from typing import Optional
import os

try:
    import boto3
    import botocore

    _boto = True
except ImportError:
    _boto = False

from ..consts import NOTHING
from .abc import AbstractSourceDescriptor, ValueSource


class Parameter(ValueSource, AbstractSourceDescriptor):
    def __init__(self, path: str):
        if not _boto:
            raise ImportError(
                dedent(
                    """
                The aws.Parameter source requires the boto3 library.
                Please reinstall using:
                    pip install config-composer[AWS]
            """
                )
            )
        self._path = path

    @property
    def _name(self):
        return self._path

    @property
    def _key(self):
        name = type(self).__name__
        return (name,)

    @property
    def _value(self):
        client = boto3.client("ssm")
        try:
            response = client.get_parameter(Name=self._path, WithDecryption=True)
            value = response["Parameter"]["Value"]
        except botocore.exceptions.ClientError as err:
            value = NOTHING
        return value
