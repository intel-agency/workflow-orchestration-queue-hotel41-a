"""
Unit tests for the GitHub queue module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.models.work_item import TaskType, WorkItem, WorkItemStatus
from src.queue.github_queue import GitHubQueue, ITaskQueue


class TestGitHubQueueInit:
    """Tests for GitHubQueue initialization."""

    def test_init_with_all_params(self) -> None:
        """Test initialization with all parameters."""
        queue = GitHubQueue(token="test-token", org="test-org", repo="test-repo")
        assert queue.token == "test-token"
        assert queue.org == "test-org"
        assert queue.repo == "test-repo"
        assert "Authorization" in queue.headers

    def test_init_with_token_only(self) -> None:
        """Test initialization with only token (for notifier use case)."""
        queue = GitHubQueue(token="test-token")
        assert queue.token == "test-token"
        assert queue.org == ""
        assert queue.repo == ""


class TestGitHubQueueAddToQueue:
    """Tests for add_to_queue method."""

    @pytest.mark.asyncio
    async def test_add_to_queue_success(self) -> None:
        """Test successfully adding an item to the queue."""
        queue = GitHubQueue(token="test-token")

        item = WorkItem(
            id="123",
            issue_number=42,
            source_url="https://github.com/org/repo/issues/42",
            context_body="Test",
            target_repo_slug="org/repo",
            task_type=TaskType.IMPLEMENT,
            status=WorkItemStatus.QUEUED,
            node_id="NODE123",
        )

        with patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            result = await queue.add_to_queue(item)

            assert result is True
            mock_post.assert_called_once()

        await queue.close()

    @pytest.mark.asyncio
    async def test_add_to_queue_failure(self) -> None:
        """Test failure when adding an item to the queue."""
        queue = GitHubQueue(token="test-token")

        item = WorkItem(
            id="123",
            issue_number=42,
            source_url="https://github.com/org/repo/issues/42",
            context_body="Test",
            target_repo_slug="org/repo",
            task_type=TaskType.IMPLEMENT,
            status=WorkItemStatus.QUEUED,
            node_id="NODE123",
        )

        with patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_post.return_value = mock_response

            result = await queue.add_to_queue(item)

            assert result is False

        await queue.close()


class TestGitHubQueueFetchQueuedTasks:
    """Tests for fetch_queued_tasks method."""

    @pytest.mark.asyncio
    async def test_fetch_queued_tasks_no_org_repo(self) -> None:
        """Test that fetch requires org and repo to be set."""
        queue = GitHubQueue(token="test-token")

        result = await queue.fetch_queued_tasks()

        assert result == []

        await queue.close()

    @pytest.mark.asyncio
    async def test_fetch_queued_tasks_success(self) -> None:
        """Test successfully fetching queued tasks."""
        queue = GitHubQueue(token="test-token", org="test-org", repo="test-repo")

        mock_issues = [
            {
                "id": 1,
                "number": 42,
                "html_url": "https://github.com/test-org/test-repo/issues/42",
                "body": "Test issue",
                "node_id": "NODE123",
                "labels": [{"name": "agent:queued"}],
                "title": "Test Issue",
            }
        ]

        with patch.object(queue._client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_issues
            mock_get.return_value = mock_response

            result = await queue.fetch_queued_tasks()

            assert len(result) == 1
            assert result[0].issue_number == 42
            assert result[0].task_type == TaskType.IMPLEMENT

        await queue.close()

    @pytest.mark.asyncio
    async def test_fetch_queued_tasks_rate_limit(self) -> None:
        """Test that rate limit errors are propagated."""
        queue = GitHubQueue(token="test-token", org="test-org", repo="test-repo")

        with patch.object(queue._client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Rate limited", request=MagicMock(), response=mock_response
            )
            mock_get.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError):
                await queue.fetch_queued_tasks()

        await queue.close()


class TestGitHubQueueUpdateStatus:
    """Tests for update_status method."""

    @pytest.mark.asyncio
    async def test_update_status_with_comment(self) -> None:
        """Test updating status with a comment."""
        queue = GitHubQueue(token="test-token")

        item = WorkItem(
            id="123",
            issue_number=42,
            source_url="https://github.com/org/repo/issues/42",
            context_body="Test",
            target_repo_slug="org/repo",
            task_type=TaskType.IMPLEMENT,
            status=WorkItemStatus.IN_PROGRESS,
            node_id="NODE123",
        )

        with patch.object(queue._client, "delete", new_callable=AsyncMock) as mock_delete:
            with patch.object(queue._client, "post", new_callable=AsyncMock) as mock_post:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_delete.return_value = mock_response
                mock_post.return_value = mock_response

                await queue.update_status(item, WorkItemStatus.SUCCESS, "Done!")

                # Should be called twice: once for labels, once for comment
                assert mock_post.call_count == 2

        await queue.close()


class TestGitHubQueueClose:
    """Tests for the close method."""

    @pytest.mark.asyncio
    async def test_close_releases_client(self) -> None:
        """Test that close releases the HTTP client."""
        queue = GitHubQueue(token="test-token")

        await queue.close()
        # Client should be closed after this
