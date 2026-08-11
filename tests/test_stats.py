import unittest
import sqlite3
from datetime import datetime, timedelta

from studyn.stats import aggregate_rows, calculate_streak, collect_snapshot


def timestamp_ms(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    value = datetime(year, month, day, hour, minute).astimezone()
    return int(value.timestamp() * 1000)


class FakeDb:
    def __init__(self, rows, streak_days, lifetime):
        self.rows = rows
        self.streak_days = streak_days
        self.lifetime = lifetime

    def all(self, query, *_args):
        if "SELECT id, ease, time" in query:
            return self.rows
        if "SELECT DISTINCT" in query:
            return [(day,) for day in self.streak_days]
        raise AssertionError(query)

    def first(self, query, *_args):
        if "SELECT COUNT(*)" in query:
            return self.lifetime
        raise AssertionError(query)


class FakeCollection:
    def __init__(self, db):
        self.db = db


class SqliteDb:
    def __init__(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute(
            "CREATE TABLE revlog (id INTEGER, ease INTEGER, time INTEGER)"
        )

    def all(self, query, *args):
        return self.connection.execute(query, args).fetchall()

    def first(self, query, *args):
        return self.connection.execute(query, args).fetchone()


class StatsTests(unittest.TestCase):
    def test_review_before_day_boundary_belongs_to_previous_day(self) -> None:
        first = datetime(2026, 8, 9).date()
        last = datetime(2026, 8, 10).date()
        rows = [
            (timestamp_ms(2026, 8, 10, 3, 30), 1, 1000),
            (timestamp_ms(2026, 8, 10, 4, 30), 3, 2000),
        ]
        result = aggregate_rows(rows, first, last, 4)
        self.assertEqual([day.date for day in result], ["2026-08-09", "2026-08-10"])
        self.assertEqual(result[0].again_count, 1)
        self.assertEqual(result[1].good_count, 1)

    def test_aggregation_counts_answers_and_time(self) -> None:
        target = datetime(2026, 8, 10).date()
        rows = [
            (timestamp_ms(2026, 8, 10, 8), 1, 1000),
            (timestamp_ms(2026, 8, 10, 9), 2, 2000),
            (timestamp_ms(2026, 8, 10, 10), 3, 3000),
            (timestamp_ms(2026, 8, 10, 11), 4, 4000),
        ]
        day = aggregate_rows(rows, target, target, 4)[0]
        self.assertEqual(day.reviews, 4)
        self.assertEqual(day.review_time_ms, 10000)
        self.assertEqual(day.retention, 75.0)

    def test_streak_allows_today_to_be_empty(self) -> None:
        today = datetime(2026, 8, 10).date()
        days = [(today - timedelta(days=offset)).isoformat() for offset in (1, 2, 3)]
        self.assertEqual(calculate_streak(days, today), 3)

    def test_collect_snapshot_contains_no_card_content(self) -> None:
        now = datetime(2026, 8, 10, 12).astimezone()
        rows = [(timestamp_ms(2026, 8, 10, 8), 3, 2500)]
        collection = FakeCollection(
            FakeDb(rows, ["2026-08-10", "2026-08-09"], (42, 123456))
        )
        snapshot = collect_snapshot(collection, 31, 4, now)
        payload = snapshot.to_payload()
        serialized = str(payload).lower()
        self.assertEqual(snapshot.current_streak, 2)
        self.assertEqual(snapshot.lifetime_reviews, 42)
        self.assertNotIn("card", serialized)
        self.assertNotIn("deck", serialized)
        self.assertNotIn("note", serialized)

    def test_collection_queries_execute_against_sqlite(self) -> None:
        db = SqliteDb()
        db.connection.executemany(
            "INSERT INTO revlog (id, ease, time) VALUES (?, ?, ?)",
            [
                (timestamp_ms(2026, 8, 9, 8), 1, 1000),
                (timestamp_ms(2026, 8, 10, 8), 3, 2500),
            ],
        )
        snapshot = collect_snapshot(
            FakeCollection(db),
            days=2,
            day_starts_at_hour=4,
            now=datetime(2026, 8, 10, 12).astimezone(),
        )
        self.assertEqual(len(snapshot.days), 2)
        self.assertEqual(snapshot.lifetime_reviews, 2)
        self.assertEqual(snapshot.lifetime_review_time_ms, 3500)


if __name__ == "__main__":
    unittest.main()
