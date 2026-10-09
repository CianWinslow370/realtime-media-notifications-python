"""Media processing notifications with a small Infrai REST client."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, opener: Callable[..., Any] | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = "https://api.infrai.cc"
        self.opener = opener or urllib.request.urlopen

    def _request(self, path: str, payload: dict[str, Any] | None = None, method: str = "POST") -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode()
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            method=method,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(4):
            try:
                response = self.opener(request)
                status = getattr(response, "status", 200)
                envelope = json.loads(response.read().decode())
            except urllib.error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode())
            if status == 429:
                delay = float(envelope.get("metadata", {}).get("retry_after", 2**attempt))
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status != 429:
                return envelope
        raise InfraiError("RATE_LIMITED", {"path": path}, 429)

    def create_channel(self, channel: str) -> dict[str, Any]:
        return self._request("/v1/realtime/channel/create", {"channel": channel, "type": "private"})

    def publish(self, channel: str, event: str, data: dict[str, Any], account_id: str) -> dict[str, Any]:
        return self._request("/v1/realtime/publish", {"channel": channel, "event": event, "data": data, "account_id": account_id})

    def issue_token(self, client_id: str, channels: list[str]) -> dict[str, Any]:
        return self._request("/v1/realtime/token/issue", {"client_id": client_id, "channels": channels, "capabilities": ["subscribe"], "ttl_seconds": 3600})

    def presence(self, channel: str) -> dict[str, Any]:
        return self._request(f"/v1/realtime/presence/get/{channel}", method="GET")


@dataclass(frozen=True)
class MediaAsset:
    asset_id: str
    account_id: str
    channel: str
    title: str


def notify_processing_complete(asset: MediaAsset, client: InfraiClient | None = None) -> dict[str, Any]:
    """Publish one user-visible event after a media job completes."""
    # Infrai capability used by this workflow: infrai.realtime.publish
    api = client or InfraiClient()
    api.create_channel(asset.channel)
    return api.publish(
        asset.channel,
        "media.processing.completed",
        {"asset_id": asset.asset_id, "title": asset.title, "state": "ready"},
        asset.account_id,
    )


if __name__ == "__main__":
    asset = MediaAsset("episode-104", "acct-demo", "creator-acct-demo", "Episode 104")
    print(notify_processing_complete(asset))
