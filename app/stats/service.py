"""Service for managing bot statistics."""

import aiosqlite
from datetime import date, datetime
from pathlib import Path
from typing import Optional
from loguru import logger

from app.config import settings
from app.stats.models import UserActivity, DailyStats

BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "bot_stats.db"


class StatsService:
    """Service for collecting and retrieving bot statistics."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    async def initialize(self) -> None:
        """Initialize database tables."""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATE,
                    total_requests INTEGER DEFAULT 0
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date DATE PRIMARY KEY,
                    active_users INTEGER DEFAULT 0,
                    total_requests INTEGER DEFAULT 0,
                    new_users INTEGER DEFAULT 0
                )
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_last_activity 
                ON users(last_activity)
            """)

            await conn.commit()
            logger.info("Statistics database initialized")

    async def record_user_activity(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
    ) -> None:
        """Record user activity."""
        today = date.today()

        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            # Check if user exists
            cursor = await conn.execute(
                "SELECT user_id, last_activity, total_requests FROM users WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()

            if row:
                # Update existing user
                last_activity = datetime.fromisoformat(row["last_activity"]).date() if row["last_activity"] else None
                is_new_day = last_activity != today
                total_requests = row["total_requests"] + 1

                await conn.execute(
                    """
                    UPDATE users 
                    SET username = ?, first_name = ?, last_activity = ?, total_requests = ?
                    WHERE user_id = ?
                    """,
                    (username, first_name, today.isoformat(), total_requests, user_id),
                )

                # Update daily stats if it's a new day for this user
                if is_new_day:
                    await self._increment_daily_active_users(conn, today)
            else:
                # New user
                await conn.execute(
                    """
                    INSERT INTO users (user_id, username, first_name, last_activity, total_requests)
                    VALUES (?, ?, ?, ?, 1)
                    """,
                    (user_id, username, first_name, today.isoformat()),
                )
                await self._increment_daily_new_users(conn, today)
                await self._increment_daily_active_users(conn, today)

            # Increment daily requests
            await self._increment_daily_requests(conn, today)

            await conn.commit()

    async def _increment_daily_active_users(self, conn: aiosqlite.Connection, day: date) -> None:
        """Increment active users count for the day."""
        await conn.execute(
            """
            INSERT INTO daily_stats (date, active_users, total_requests, new_users)
            VALUES (?, 1, 0, 0)
            ON CONFLICT(date) DO UPDATE SET active_users = active_users + 1
            """,
            (day.isoformat(),),
        )

    async def _increment_daily_new_users(self, conn: aiosqlite.Connection, day: date) -> None:
        """Increment new users count for the day."""
        await conn.execute(
            """
            INSERT INTO daily_stats (date, active_users, total_requests, new_users)
            VALUES (?, 0, 0, 1)
            ON CONFLICT(date) DO UPDATE SET new_users = new_users + 1
            """,
            (day.isoformat(),),
        )

    async def _increment_daily_requests(self, conn: aiosqlite.Connection, day: date) -> None:
        """Increment total requests count for the day."""
        await conn.execute(
            """
            INSERT INTO daily_stats (date, active_users, total_requests, new_users)
            VALUES (?, 0, 1, 0)
            ON CONFLICT(date) DO UPDATE SET total_requests = total_requests + 1
            """,
            (day.isoformat(),),
        )

    async def get_total_users(self) -> int:
        """Get total number of registered users."""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT COUNT(*) as count FROM users")
            row = await cursor.fetchone()
            return row["count"] if row else 0

    async def get_daily_stats(self, day: Optional[date] = None) -> DailyStats:
        """Get statistics for a specific day (default: today)."""
        if day is None:
            day = date.today()

        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                "SELECT * FROM daily_stats WHERE date = ?",
                (day.isoformat(),),
            )
            row = await cursor.fetchone()

            if row:
                return DailyStats(
                    date=day,
                    active_users=row["active_users"],
                    total_requests=row["total_requests"],
                    new_users=row["new_users"],
                )
            return DailyStats(date=day, active_users=0, total_requests=0, new_users=0)

    async def get_stats_for_period(self, start_date: date, end_date: date) -> list[DailyStats]:
        """Get statistics for a date range."""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                SELECT * FROM daily_stats 
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
                """,
                (start_date.isoformat(), end_date.isoformat()),
            )
            rows = await cursor.fetchall()

            return [
                DailyStats(
                    date=datetime.fromisoformat(row["date"]).date(),
                    active_users=row["active_users"],
                    total_requests=row["total_requests"],
                    new_users=row["new_users"],
                )
                for row in rows
            ]

    async def get_recent_stats(self, days: int = 7) -> list[DailyStats]:
        """Get statistics for the last N days."""
        end_date = date.today()
        start_date = date.fromordinal(end_date.toordinal() - days + 1)
        return await self.get_stats_for_period(start_date, end_date)

