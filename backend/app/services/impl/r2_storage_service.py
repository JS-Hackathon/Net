import os
import logging
from app.core.config import settings
from app.services.interfaces.storage_service import StorageService

logger = logging.getLogger(__name__)

class R2StorageService(StorageService):
    def __init__(self):
        self.bucket_name = settings.R2_BUCKET_NAME
        self.account_id = settings.R2_ACCOUNT_ID
        self.access_key = settings.R2_ACCESS_KEY_ID
        self.secret_key = settings.R2_SECRET_ACCESS_KEY
        
        # Local fallback directory
        self.local_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "static", 
            "uploads"
        )
        os.makedirs(self.local_dir, exist_ok=True)

    async def upload_file(self, file_data: bytes, filename: str) -> str:
        # Check if R2 is configured
        if not all([self.bucket_name, self.account_id, self.access_key, self.secret_key]):
            logger.warning("R2 Credentials not fully configured. Using local file storage fallback.")
            local_path = os.path.join(self.local_dir, filename)
            with open(local_path, "wb") as f:
                f.write(file_data)
            return f"/static/uploads/{filename}"

        # If R2 is configured, we'd use boto3. Since we don't have boto3 in requirements, 
        # let's try to import it, and fallback to local storage if it's missing.
        try:
            import boto3
            from botocore.client import Config
            
            s3_client = boto3.client(
                service_name='s3',
                endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(signature_version='s3v4')
            )
            
            s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file_data
            )
            # URL format for Cloudflare R2 public bucket access (or custom domain)
            return f"https://{self.bucket_name}.r2.cloudflarestorage.com/{filename}"
            
        except ImportError:
            logger.error("boto3 package not installed. Falling back to local storage.")
            local_path = os.path.join(self.local_dir, filename)
            with open(local_path, "wb") as f:
                f.write(file_data)
            return f"/static/uploads/{filename}"
        except Exception as e:
            logger.error(f"R2 upload error: {e}. Falling back to local storage.")
            local_path = os.path.join(self.local_dir, filename)
            with open(local_path, "wb") as f:
                f.write(file_data)
            return f"/static/uploads/{filename}"

    async def download_file(self, filename: str) -> bytes:
        local_path = os.path.join(self.local_dir, filename)
        if os.path.exists(local_path):
            with open(local_path, "rb") as f:
                return f.read()
        
        # If not local, try R2 if credentials exist
        if all([self.bucket_name, self.account_id, self.access_key, self.secret_key]):
            try:
                import boto3
                from botocore.client import Config
                
                s3_client = boto3.client(
                    service_name='s3',
                    endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    config=Config(signature_version='s3v4')
                )
                response = s3_client.get_object(Bucket=self.bucket_name, Key=filename)
                return response['Body'].read()
            except Exception as e:
                logger.error(f"R2 download error: {e}")
        
        raise FileNotFoundError(f"File {filename} not found in storage")

    async def delete_file(self, filename: str) -> bool:
        local_path = os.path.join(self.local_dir, filename)
        local_deleted = False
        if os.path.exists(local_path):
            os.remove(local_path)
            local_deleted = True
            
        if all([self.bucket_name, self.account_id, self.access_key, self.secret_key]):
            try:
                import boto3
                from botocore.client import Config
                
                s3_client = boto3.client(
                    service_name='s3',
                    endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    config=Config(signature_version='s3v4')
                )
                s3_client.delete_object(Bucket=self.bucket_name, Key=filename)
                return True
            except Exception as e:
                logger.error(f"R2 delete error: {e}")
                
        return local_deleted
