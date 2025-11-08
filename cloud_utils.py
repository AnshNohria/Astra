"""
Cloud utilities for interacting with mocked AWS S3.
Provides a high-level interface for storage operations with multi-cloud support.
"""
import boto3
from botocore.exceptions import ClientError
from typing import List, Dict, Optional


class S3Manager:
    """Manages S3 operations with mocked backend via moto. Supports multi-cloud simulation."""
    
    # Map cloud providers to AWS regions (for moto simulation)
    CLOUD_REGIONS = {
        'aws': 'us-east-1',
        'gcp': 'us-west-1',
        'azure': 'eu-west-1'
    }
    
    def __init__(self, cloud_name: str = 'aws', bucket_name: str = "intelligent-storage-bucket"):
        """
        Initialize S3 manager and create bucket if it doesn't exist.
        
        Args:
            cloud_name: Name of the cloud provider ('aws', 'gcp', or 'azure')
            bucket_name: Name of the S3 bucket to manage
        """
        self.cloud_name = cloud_name
        self.bucket_name = bucket_name
        self.region = self.CLOUD_REGIONS.get(cloud_name, 'us-east-1')
        self.s3_client = boto3.client('s3', region_name=self.region)
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create the S3 bucket if it doesn't already exist."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            # Bucket doesn't exist, create it
            if self.region == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                # Other regions need LocationConstraint
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            print(f"✓ Created S3 bucket: {self.bucket_name} ({self.cloud_name.upper()} - {self.region})")
    
    def upload_file(self, file_key: str, content: str = "mock-data", tier: str = 'STANDARD') -> bool:
        """
        Upload a file to S3 with specified storage class.
        
        Args:
            file_key: The key/path for the file in S3
            content: File content (using mock data for demo)
            tier: Storage class (STANDARD, STANDARD_IA, GLACIER, etc.)
        
        Returns:
            True if upload successful, False otherwise
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=content.encode('utf-8'),
                StorageClass=tier
            )
            return True
        except ClientError as e:
            print(f"✗ Error uploading {file_key}: {e}")
            return False
    
    def get_file_tier(self, file_key: str) -> Optional[str]:
        """
        Get the current storage class of a file.
        
        Args:
            file_key: The key/path for the file in S3
        
        Returns:
            Storage class string or None if file doesn't exist
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return response.get('StorageClass', 'STANDARD')
        except ClientError:
            return None
    
    def change_file_tier(self, file_key: str, new_tier: str) -> bool:
        """
        Change the storage class of an existing file using copy-and-delete pattern.
        
        Args:
            file_key: The key/path for the file in S3
            new_tier: Target storage class
        
        Returns:
            True if tier change successful, False otherwise
        """
        try:
            # Copy object to itself with new storage class
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': file_key
            }
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=file_key,
                StorageClass=new_tier,
                MetadataDirective='COPY'
            )
            return True
        except ClientError as e:
            print(f"✗ Error changing tier for {file_key}: {e}")
            return False
    
    def list_all_files(self) -> List[str]:
        """
        List all files in the bucket.
        
        Returns:
            List of file keys
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except ClientError as e:
            print(f"✗ Error listing files: {e}")
            return []
    
    def get_file_metadata(self, file_key: str) -> Optional[Dict]:
        """
        Get comprehensive metadata for a file.
        
        Args:
            file_key: The key/path for the file in S3
        
        Returns:
            Dictionary with file metadata or None
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return {
                'size': response.get('ContentLength', 0),
                'last_modified': response.get('LastModified'),
                'storage_class': response.get('StorageClass', 'STANDARD')
            }
        except ClientError:
            return None
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            file_key: The key/path for the file in S3
        
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError as e:
            print(f"✗ Error deleting {file_key}: {e}")
            return False
    
    def download_file_content(self, file_key: str) -> Optional[bytes]:
        """
        Download the content of a file from S3.
        
        Args:
            file_key: The key/path for the file in S3
        
        Returns:
            File content as bytes, or None if file doesn't exist
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return response['Body'].read()
        except ClientError as e:
            print(f"✗ Error downloading {file_key}: {e}")
            return None
    
    def get_cloud_name(self) -> str:
        """Get the cloud provider name."""
        return self.cloud_name
