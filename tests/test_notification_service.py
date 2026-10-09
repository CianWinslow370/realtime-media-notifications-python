import json

from src.notification_service import MediaAsset, notify_processing_complete


class FakeResponse:
    status = 200

    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode()


def test_completed_job_publishes_ready_state():
    calls = []

    def opener(request):
        calls.append((request.method, request.full_url, json.loads(request.data) if request.data else None))
        return FakeResponse({"ok": True, "data": {"accepted": True}, "error": None, "metadata": {}})

    result = notify_processing_complete(
        MediaAsset("asset-7", "acct-9", "creator-9", "Trailer"),
        client=__import__("src.notification_service", fromlist=["InfraiClient"]).InfraiClient("test-key", opener),
    )
    assert result["data"]["accepted"] is True
    assert calls[1][2]["event"] == "media.processing.completed"
    assert calls[1][2]["data"]["state"] == "ready"
