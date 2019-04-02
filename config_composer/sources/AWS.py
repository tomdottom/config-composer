from typing import Optional
import os

import boto3
import botocore

from ..abc import AbstractSourceDescriptor
from ..consts import NOTHING


class Parameter(AbstractSourceDescriptor):
    def __init__(self, path: str):
        self._path = path

    def _init_value(self):
        client = boto3.client('ssm')
        try:
            response = client.get_parameter(
                Name=self._path,
                WithDecryption=True,
            )
            value = response["Parameter"]["Value"]
        except botocore.exceptions.ClientError as err:
            value = NOTHING
        return value
