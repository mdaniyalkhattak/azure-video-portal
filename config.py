import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
    AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
    AZURE_BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER", "videos")
    AZURE_SAS_EXPIRY_DAYS = int(os.getenv("AZURE_SAS_EXPIRY_DAYS", "30"))

    AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.AZURE_STORAGE_ACCOUNT:
            missing.append("AZURE_STORAGE_ACCOUNT")
        if not cls.AZURE_ACCOUNT_KEY:
            missing.append("AZURE_ACCOUNT_KEY")
        if not cls.AZURE_BLOB_CONTAINER:
            missing.append("AZURE_BLOB_CONTAINER")
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
