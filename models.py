from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class Comment:
    author: str
    text: str
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "author": self.author,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Comment":
        return cls(
            author=data.get("author", "Anonymous"),
            text=data.get("text", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
        )

@dataclass
class Video:
    id: str
    title: str
    filename: str
    blob_name: str
    blob_url: str
    uploaded_at: datetime
    comments: List[Comment] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "filename": self.filename,
            "blob_name": self.blob_name,
            "blob_url": "",
            "uploaded_at": self.uploaded_at.isoformat(),
            "comments": [c.to_dict() for c in self.comments],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Video":
        comments = [Comment.from_dict(c) for c in data.get("comments", [])]
        uploaded_at = datetime.fromisoformat(data["uploaded_at"])
        return cls(
            id=data["id"],
            title=data.get("title", ""),
            filename=data.get("filename", ""),
            blob_name=data.get("blob_name", ""),
            blob_url="",
            uploaded_at=uploaded_at,
            comments=comments,
        )
