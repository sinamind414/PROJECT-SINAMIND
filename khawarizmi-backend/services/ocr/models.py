from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class WordBox:
    text: str
    conf: float
    bbox: tuple

    def to_dict(self) -> Dict[str, Any]:
        return {"text": self.text, "conf": round(self.conf, 1), "bbox": self.bbox}


@dataclass
class PageResult:
    page: int
    text: str = ""
    char_count: int = 0
    confidence: float = 0.0
    status: str = "success"
    error: Optional[str] = None
    processing_time: float = 0.0
    words: List[WordBox] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page": self.page,
            "text": self.text,
            "char_count": self.char_count,
            "confidence": round(self.confidence, 2),
            "status": self.status,
            "words": [w.to_dict() for w in self.words],
            "word_count": len(self.words)
        }


@dataclass
class VolumeSummary:
    volume: str
    pdf: str
    total_pages: int
    pages_processed: int
    errors: int
    total_characters: int
    avg_confidence: float
    quality_warning: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    bundle_dir: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}
