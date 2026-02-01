import asyncio
import logging

import boto3
import aioboto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from src.core.config import settings
from typing import AsyncIterator, Dict, Any

class S3Service:
    def __init__(self):
        self.bucket_name = settings.AWS_BUCKET_NAME
        self.region = settings.AWS_REGION_NAME
        self.s3_config = {
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "region_name": self.region,
            "endpoint_url": settings.AWS_ENDPOINT_URL,
        }

    async def put_concurrent_parts(self, byte_source: AsyncIterator[bytes],
                                   target_key: str) -> None:
        session = aioboto3.Session()
        target_key = f"media/{target_key}"
        async with session.client('s3', **self.s3_config) as s3c:
            init_result = await s3c.create_multipart_upload(Bucket=self.bucket_name, Key=target_key)
            upload_token = init_result['UploadId']
            pending = []

            async def ship_piece(seq_no: int, payload: bytes) -> Dict[str, Any]:
                reply = await s3c.upload_part(
                    Bucket=self.bucket_name,
                    Key=target_key,
                    PartNumber=seq_no,
                    UploadId=upload_token,
                    Body=payload
                )
                return {
                    'ETag': reply['ETag'],
                    'PartNumber': seq_no
                }

            try:
                part_no = 1
                async for blob in byte_source:
                    job = asyncio.create_task(ship_piece(part_no, blob))
                    pending.append(job)
                    part_no += 1
                collected = await asyncio.gather(*pending)
                await s3c.complete_multipart_upload(
                    Bucket=self.bucket_name,
                    Key=target_key,
                    UploadId=upload_token,
                    MultipartUpload={'Parts': collected}
                )
                logging.info('Upload Done')
            except Exception as exc:
                await s3c.abort_multipart_upload(
                    Bucket=self.bucket_name,
                    Key=target_key,
                    UploadId=upload_token
                )
                logging.exception('An error occurred', exc)

    async def upload_file_async(self, file: UploadFile):
        session = aioboto3.Session()
        try:
            async with session.client("s3", **self.s3_config) as s3_client:
                object_name = file.filename
                path = f"media/{object_name}"
                await s3_client.upload_fileobj(
                    file.file,
                    self.bucket_name,
                    path,
                    ExtraArgs={"ContentType": file.content_type}
                )
            return path
        except ClientError as e:
            logging.error(f"S3 Upload Error: {e}")
            return False

    def download_file_sync(self, object_name: str, destination_path: str):
        s3_client = boto3.client("s3", **self.s3_config)
        try:
            s3_client.download_file(self.bucket_name, object_name, destination_path)
            return True
        except ClientError as e:
            logging.error(f"S3 Download Error: {e}")
            raise e

    def generate_presigned_url(self, object_name: str, expiration=3600):
        s3_client = boto3.client("s3", **self.s3_config)
        try:
            response = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logging.error(f"S3 Presign Error: {e}")
            return None

s3_client = S3Service()