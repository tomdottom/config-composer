from textwrap import dedent
from typing import Optional
import os

try:
    import boto3
    import botocore

    _boto = True
except ImportError:
    _boto = False

from ..abc import AbstractSourceDescriptor
from ..consts import NOTHING


class Parameter(AbstractSourceDescriptor):
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

    def _init_value(self):
        client = boto3.client("ssm")
        try:
            response = client.get_parameter(Name=self._path, WithDecryption=True)
            value = response["Parameter"]["Value"]
        except botocore.exceptions.ClientError as err:
            value = NOTHING
        return value
