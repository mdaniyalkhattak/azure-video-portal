import uuid
import json
from datetime import datetime, timedelta
from typing import List, Optional

from azure.storage.blob import (
    BlobServiceClient,
    ContentSettings,
    generate_blob_sas,
    BlobSasPermissions,
)
from werkzeug.datastructures import FileStorage

from config import Config
from models import Video, Comment

Config.validate()

_blob_service_client = BlobServiceClient.from_connection_string(
    Config.AZURE_BLOB_CONNECTION_STRING
)
_container_client = _blob_service_client.get_container_client(
    Config.AZURE_BLOB_CONTAINER
)

def ensure_container():
    try:
        _container_client.create_container()
    except Exception:
        pass

def _metadata_blob_name(video_id: str) -> str:
    return f"metadata/{video_id}.json"

def _detect_mime(filename: str, fallback: str = "video/mp4") -> str:
    name = (filename or "").lower()
    if name.endswith(".mp4"):
        return "video/mp4"
    if name.endswith(".webm"):
        return "video/webm"
    if name.endswith(".ogg") or name.endswith(".ogv"):
        return "video/ogg"
    return fallback

def _sas_for_blob(blob_name: str) -> str:
    expiry = datetime.utcnow() + timedelta(days=Config.AZURE_SAS_EXPIRY_DAYS)
    sas_token = generate_blob_sas(
        account_name=Config.AZURE_STORAGE_ACCOUNT,
        container_name=Config.AZURE_BLOB_CONTAINER,
        blob_name=blob_name,
        account_key=Config.AZURE_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=expiry,
    )
    blob_client = _container_client.get_blob_client(blob_name)
    base_url = blob_client.url.replace("http://", "https://")
    return f"{base_url}?{sas_token}"

def upload_video(file_storage: FileStorage, title: str) -> Video:
    ensure_container()

    video_id = str(uuid.uuid4())
    safe_name = (file_storage.filename or "video").replace("/", "_").replace("..", "_").strip()
    mime = _detect_mime(safe_name, fallback=file_storage.mimetype or "video/mp4")

    blob_name = f"videos/{video_id}/{safe_name}"
    blob_client = _container_client.get_blob_client(blob_name)

    data = file_storage.read()
    blob_client.upload_blob(
        data,
        overwrite=True,
        content_settings=ContentSettings(content_type=mime),
    )

    sas_url = _sas_for_blob(blob_name)

    video = Video(
        id=video_id,
        title=title or safe_name,
        filename=safe_name,
        blob_name=blob_name,
        blob_url=sas_url,
        uploaded_at=datetime.utcnow(),
        comments=[],
    )

    meta_client = _container_client.get_blob_client(_metadata_blob_name(video_id))
    meta_client.upload_blob(
        json.dumps(video.to_dict(), indent=2),
        overwrite=True,
        content_settings=ContentSettings(content_type="application/json"),
    )

    return video

def _video_from_metadata(data: dict) -> Video:
    v = Video.from_dict(data)
    v.blob_url = _sas_for_blob(v.blob_name)
    return v

def list_videos() -> List[Video]:
    ensure_container()
    videos: List[Video] = []
    for blob in _container_client.list_blobs(name_starts_with="metadata/"):
        meta_client = _container_client.get_blob_client(blob)
        raw = meta_client.download_blob().readall()
        data = json.loads(raw)
        videos.append(_video_from_metadata(data))
    videos.sort(key=lambda v: v.uploaded_at, reverse=True)
    return videos

def get_video(video_id: str) -> Optional[Video]:
    ensure_container()
    meta_name = _metadata_blob_name(video_id)
    meta_client = _container_client.get_blob_client(meta_name)
    try:
        raw = meta_client.download_blob().readall()
    except Exception:
        return None
    data = json.loads(raw)
    return _video_from_metadata(data)

def save_video_metadata(video: Video) -> None:
    ensure_container()
    meta_client = _container_client.get_blob_client(_metadata_blob_name(video.id))
    meta_client.upload_blob(
        json.dumps(video.to_dict(), indent=2),
        overwrite=True,
        content_settings=ContentSettings(content_type="application/json"),
    )

def add_comment(video_id: str, author: str, text: str) -> Optional[Video]:
    video = get_video(video_id)
    if not video:
        return None
    video.comments.append(
        Comment(author=author, text=text, created_at=datetime.utcnow())
    )
    save_video_metadata(video)
    return video

def delete_video(video_id: str) -> bool:
    video = get_video(video_id)
    if not video:
        return False

    video_blob = _container_client.get_blob_client(video.blob_name)
    try:
        video_blob.delete_blob()
    except Exception:
        pass

    meta_blob = _container_client.get_blob_client(_metadata_blob_name(video_id))
    try:
        meta_blob.delete_blob()
    except Exception:
        pass

    return True
