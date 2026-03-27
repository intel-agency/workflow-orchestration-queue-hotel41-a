"""
OS-APOW GitHub Event Models

Pydantic models for parsing and validating GitHub webhook payloads.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GitHubUser(BaseModel):
    """GitHub user information."""

    id: int
    login: str
    node_id: str | None = None
    html_url: str | None = None
    type: str | None = None


class GitHubLabel(BaseModel):
    """GitHub label information."""

    id: int
    name: str
    color: str | None = None
    description: str | None = None


class GitHubRepository(BaseModel):
    """GitHub repository information."""

    id: int
    name: str
    full_name: str
    owner: GitHubUser
    html_url: str
    private: bool = False


class GitHubIssue(BaseModel):
    """GitHub issue information."""

    id: int
    number: int
    title: str
    body: str | None = None
    state: str
    html_url: str
    node_id: str
    user: GitHubUser
    labels: list[GitHubLabel] = Field(default_factory=list)
    assignees: list[GitHubUser] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GitHubWebhookPayload(BaseModel):
    """Base GitHub webhook payload."""

    action: str | None = None
    issue: GitHubIssue | None = None
    repository: GitHubRepository | None = None
    sender: GitHubUser | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GitHubWebhookPayload:
        """Create a payload instance from a raw dictionary."""
        return cls.model_validate(data)
