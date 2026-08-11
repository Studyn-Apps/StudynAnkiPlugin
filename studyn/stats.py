from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta
from typing import Any, DefaultDict, Dict, Iterable, List, Optional, Sequence, Tuple

from .models import DailyStats, StatsSnapshot


ReviewRow = Tuple[int, int, int]


def _local_datetime(timestamp_ms: int) -> datetime:
    return datetime.fromtimestamp(timestamp_ms / 1000).astimezone()


def study_day_for_timestamp(timestamp_ms: int, day_starts_at_hour: int) -> date:
    reviewed_at = _local_datetime(timestamp_ms)
    return (reviewed_at - timedelta(hours=day_starts_at_hour)).date()


def current_study_day(
    day_starts_at_hour: int, now: Optional[datetime] = None
) -> date:
    local_now = now.astimezone() if now is not None else datetime.now().astimezone()
    return (local_now - timedelta(hours=day_starts_at_hour)).date()


def _range_start_ms(first_day: date, day_starts_at_hour: int) -> int:
    local_start = datetime.combine(first_day, time(hour=day_starts_at_hour)).astimezone()
    return int(local_start.timestamp() * 1000)


def aggregate_rows(
    rows: Iterable[ReviewRow],
    first_day: date,
    last_day: date,
    day_starts_at_hour: int,
) -> List[DailyStats]:
    buckets: DefaultDict[str, Dict[str, int]] = defaultdict(
        lambda: {
            "reviews": 0,
            "review_time_ms": 0,
            "again_count": 0,
            "hard_count": 0,
            "good_count": 0,
            "easy_count": 0,
        }
    )

    for review_id, ease, answer_time_ms in rows:
        study_day = study_day_for_timestamp(int(review_id), day_starts_at_hour)
        if study_day < first_day or study_day > last_day or int(ease) <= 0:
            continue

        bucket = buckets[study_day.isoformat()]
        bucket["reviews"] += 1
        bucket["review_time_ms"] += max(0, int(answer_time_ms or 0))

        if ease == 1:
            bucket["again_count"] += 1
        elif ease == 2:
            bucket["hard_count"] += 1
        elif ease == 3:
            bucket["good_count"] += 1
        elif ease == 4:
            bucket["easy_count"] += 1

    return [
        DailyStats(date=day, **values)
        for day, values in sorted(buckets.items())
    ]


def calculate_streak(study_days: Sequence[str], today: date) -> int:
    parsed_days = {date.fromisoformat(value) for value in study_days if value}
    anchor = today
    if anchor not in parsed_days:
        anchor -= timedelta(days=1)

    streak = 0
    while anchor in parsed_days:
        streak += 1
        anchor -= timedelta(days=1)
    return streak


def collect_snapshot(
    col: Any,
    days: int,
    day_starts_at_hour: int,
    now: Optional[datetime] = None,
) -> StatsSnapshot:
    if days < 1:
        raise ValueError("days must be at least 1")
    if day_starts_at_hour < 0 or day_starts_at_hour > 23:
        raise ValueError("day_starts_at_hour must be between 0 and 23")

    last_day = current_study_day(day_starts_at_hour, now)
    first_day = last_day - timedelta(days=days - 1)
    start_ms = _range_start_ms(first_day, day_starts_at_hour)

    rows = col.db.all(
        """
        SELECT id, ease, time
        FROM revlog
        WHERE id >= ? AND ease > 0
        ORDER BY id ASC
        """,
        start_ms,
    )
    daily = aggregate_rows(rows, first_day, last_day, day_starts_at_hour)

    streak_rows = col.db.all(
        """
        SELECT DISTINCT strftime(
            '%Y-%m-%d',
            datetime((id / 1000) - ?, 'unixepoch', 'localtime')
        ) AS study_day
        FROM revlog
        WHERE ease > 0
        ORDER BY study_day DESC
        """,
        day_starts_at_hour * 3600,
    )
    streak_days = [str(row[0]) for row in streak_rows if row and row[0]]

    lifetime = col.db.first(
        """
        SELECT COUNT(*), COALESCE(SUM(time), 0)
        FROM revlog
        WHERE ease > 0
        """
    ) or (0, 0)

    return StatsSnapshot(
        range_start=first_day.isoformat(),
        range_end=last_day.isoformat(),
        days=daily,
        current_streak=calculate_streak(streak_days, last_day),
        lifetime_reviews=max(0, int(lifetime[0] or 0)),
        lifetime_review_time_ms=max(0, int(lifetime[1] or 0)),
    )
