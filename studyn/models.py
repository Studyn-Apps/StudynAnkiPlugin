from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class DailyStats:
    date: str
    reviews: int
    review_time_ms: int
    again_count: int
    hard_count: int
    good_count: int
    easy_count: int

    @property
    def retention(self) -> float:
        if self.reviews <= 0:
            return 0.0
        return round(((self.reviews - self.again_count) / self.reviews) * 100, 2)

    def to_payload(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "reviews": self.reviews,
            "reviewTimeMs": self.review_time_ms,
            "againCount": self.again_count,
            "hardCount": self.hard_count,
            "goodCount": self.good_count,
            "easyCount": self.easy_count,
        }


@dataclass(frozen=True)
class StatsSnapshot:
    range_start: str
    range_end: str
    days: List[DailyStats]
    current_streak: int
    lifetime_reviews: int
    lifetime_review_time_ms: int

    def to_payload(self) -> Dict[str, Any]:
        return {
            "range": {"start": self.range_start, "end": self.range_end},
            "days": [day.to_payload() for day in self.days],
            "summary": {
                "currentStreak": self.current_streak,
                "lifetimeReviews": self.lifetime_reviews,
                "lifetimeReviewTimeMs": self.lifetime_review_time_ms,
            },
        }


@dataclass(frozen=True)
class PairingSession:
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


@dataclass(frozen=True)
class TokenResult:
    access_token: str
    device_id: str
    display_name: Optional[str] = None


@dataclass(frozen=True)
class SyncResult:
    accepted_days: int
    synced_at: str
