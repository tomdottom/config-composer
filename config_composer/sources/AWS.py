from typing import Optional
import os

import boto3

from ..abc import AbstractSourceDescriptor


class Parameter(AbstractSourceDescriptor):
    def __init__(self, path: str):
        self._path = path

    def _init_value(self):
        client = boto3.client('ssm')
        response = client.get_parameter(
            Name=self._path,
            WithDecryption=True,
        )
        return response["Parameter"]["Value"]
