"""
Unit tests for the work_item module.
"""

import pytest

from src.models.work_item import (
    TaskType,
    WorkItem,
    WorkItemStatus,
    scrub_secrets,
)


class TestTaskType:
    """Tests for TaskType enum."""

    def test_task_type_values(self) -> None:
        """Test that TaskType has expected values."""
        assert TaskType.PLAN.value == "PLAN"
        assert TaskType.IMPLEMENT.value == "IMPLEMENT"
        assert TaskType.BUGFIX.value == "BUGFIX"

    def test_task_type_from_string(self) -> None:
        """Test creating TaskType from string."""
        assert TaskType("PLAN") == TaskType.PLAN
        assert TaskType("IMPLEMENT") == TaskType.IMPLEMENT


class TestWorkItemStatus:
    """Tests for WorkItemStatus enum."""

    def test_status_values(self) -> None:
        """Test that WorkItemStatus has expected label values."""
        assert WorkItemStatus.QUEUED.value == "agent:queued"
        assert WorkItemStatus.IN_PROGRESS.value == "agent:in-progress"
        assert WorkItemStatus.SUCCESS.value == "agent:success"
        assert WorkItemStatus.ERROR.value == "agent:error"
        assert WorkItemStatus.INFRA_FAILURE.value == "agent:infra-failure"


class TestWorkItem:
    """Tests for WorkItem model."""

    def test_work_item_creation(self) -> None:
        """Test creating a WorkItem instance."""
        item = WorkItem(
            id="123",
            issue_number=42,
            source_url="https://github.com/org/repo/issues/42",
            context_body="Test body",
            target_repo_slug="org/repo",
            task_type=TaskType.IMPLEMENT,
            status=WorkItemStatus.QUEUED,
            node_id="NODE123",
        )
        assert item.id == "123"
        assert item.issue_number == 42
        assert item.task_type == TaskType.IMPLEMENT
        assert item.status == WorkItemStatus.QUEUED

    def test_work_item_model_validation(self) -> None:
        """Test that Pydantic validates the model correctly."""
        item = WorkItem(
            id="123",
            issue_number=1,
            source_url="https://github.com/org/repo/issues/1",
            context_body="",
            target_repo_slug="org/repo",
            task_type=TaskType.PLAN,
            status=WorkItemStatus.QUEUED,
            node_id="NODE123",
        )
        assert item.task_type == TaskType.PLAN


class TestScrubSecrets:
    """Tests for the scrub_secrets function."""

    def test_scrub_github_pat(self) -> None:
        """Test scrubbing GitHub PAT tokens."""
        text = "Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        result = scrub_secrets(text)
        assert "ghp_" not in result
        assert "***REDACTED***" in result

    def test_scrub_github_app_token(self) -> None:
        """Test scrubbing GitHub App installation tokens."""
        text = "Token: ghs_1234567890abcdefghijklmnopqrstuvwxyz"
        result = scrub_secrets(text)
        assert "ghs_" not in result
        assert "***REDACTED***" in result

    def test_scrub_bearer_token(self) -> None:
        """Test scrubbing Bearer tokens."""
        text = "Authorization: Bearer abc123xyz789=="
        result = scrub_secrets(text)
        assert "Bearer" not in result or "***REDACTED***" in result

    def test_scrub_openai_key(self) -> None:
        """Test scrubbing OpenAI-style API keys."""
        text = "API Key: sk-1234567890abcdefghijklmnopqrst"
        result = scrub_secrets(text)
        assert "sk-" not in result
        assert "***REDACTED***" in result

    def test_scrub_no_secrets(self) -> None:
        """Test that text without secrets is unchanged."""
        text = "This is a normal log message without any secrets."
        result = scrub_secrets(text)
        assert result == text

    def test_scrub_multiple_secrets(self) -> None:
        """Test scrubbing multiple secrets in one text."""
        text = "ghp_token1 and ghs_token2 both need redaction"
        # Use fake tokens that match the patterns
        text = "ghp_1234567890123456789012345678901234 and ghs_1234567890123456789012345678901234"
        result = scrub_secrets(text)
        assert "ghp_" not in result
        assert "ghs_" not in result

    def test_scrub_custom_replacement(self) -> None:
        """Test using a custom replacement string."""
        text = "ghp_1234567890123456789012345678901234"
        result = scrub_secrets(text, replacement="[HIDDEN]")
        assert "[HIDDEN]" in result
        assert "***REDACTED***" not in result
