"""Database models for statistics."""

from datetime import date
from typing import Optional


class UserActivity:
    """Model for user activity statistics."""

    def __init__(
        self,
        user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_activity: date,
        total_requests: int = 0,
    ):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_activity = last_activity
        self.total_requests = total_requests


class DailyStats:
    """Model for daily statistics."""

    def __init__(
        self,
        date: date,
        active_users: int,
        total_requests: int,
        new_users: int = 0,
    ):
        self.date = date
        self.active_users = active_users
        self.total_requests = total_requests
        self.new_users = new_users

