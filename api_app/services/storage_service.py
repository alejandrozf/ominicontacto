# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3, as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
from __future__ import unicode_literals

import os
import boto3
import logging

from botocore.client import Config

logger = logging.getLogger(__name__)


class StorageService(object):

    def __init__(self):
        self.access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.url = os.getenv('S3_ENDPOINT') or None
        self.internal_url = os.getenv('S3_ENDPOINT_MINIO') or 'https://minio:9000'
        self.region_name = os.getenv('S3_REGION_NAME') or 'us-east-1'
        self.storage_type = os.getenv('CALLREC_DEVICE')

        if self.storage_type == 's3-aws':
            self.client = boto3.client("s3",
                                       aws_access_key_id=self.access_key_id,
                                       aws_secret_access_key=self.secret_access_key,
                                       region_name=self.region_name)
        elif self.storage_type == 's3-minio':
            self.client = boto3.client("s3",
                                       aws_access_key_id=self.access_key_id,
                                       aws_secret_access_key=self.secret_access_key,
                                       config=Config(signature_version='s3v4'),
                                       endpoint_url=self.internal_url,
                                       region_name=self.region_name,
                                       verify=False)
            self.url_client = boto3.client("s3",
                                           aws_access_key_id=self.access_key_id,
                                           aws_secret_access_key=self.secret_access_key,
                                           config=Config(signature_version='s3v4'),
                                           endpoint_url=self.url,
                                           region_name=self.region_name,
                                           verify=False)
        else:
            self.client = boto3.client("s3",
                                       aws_access_key_id=self.access_key_id,
                                       aws_secret_access_key=self.secret_access_key,
                                       endpoint_url=self.internal_url,
                                       region_name=self.region_name)

    def get_file_url(self, filename):
        client = self.client
        if self.storage_type == 's3-minio':
            client = self.url_client
        return client.generate_presigned_url('get_object',
                                             Params={'Bucket': self.bucket_name,
                                                     'Key': filename[1:]},
                                             ExpiresIn=3600)

    def download_file(self, file_name, local_destination, root_s3_folder=None):
        file_dest = os.path.join(local_destination, file_name)
        full_local_path = os.path.dirname(file_dest)
        if not os.path.exists(full_local_path):
            try:
                os.makedirs(full_local_path, mode=0o755)
            except Exception:
                pass
        try:
            s3_file_path = file_name
            if root_s3_folder is not None:
                s3_file_path = f'{root_s3_folder}/{s3_file_path}'
            self.client.download_file(self.bucket_name, s3_file_path, file_dest)
        except Exception as e:
            logger.error(f'Error descargando archivo desde S3 {e.__str__()}')
            return False
        return True

    def upload_file(self, filename, local_path, remote_destination):
        file_dest = os.path.join(remote_destination, filename)
        try:
            self.client.upload_file(local_path, self.bucket_name, file_dest)
        except Exception as e:
            logger.error(f'Error subiendo archivo desde S3 {e.__str__()}')
            return False
        return True

    def delete_file(self, filename, remote_destination):
        file_dest = os.path.join(remote_destination, filename)
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_dest)
        except Exception as e:
            logger.error(f'Error borrando archivo desde S3 {e.__str__()}')
            return False
        return True
