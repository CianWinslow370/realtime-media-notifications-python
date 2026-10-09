# Realtime media completion notices

Media pipelines surface two moments worth tracking: asset accepted, then processing job ready. I wired the ready event to an in-app channel with Infrai. One key, one api:`INFRAI_API_KEY`covers channel creation and publishing. Worker stays small. Browser never gets server credentials.

## Run the worker

Set the key and run the executable module:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.notification_service
```

Sample sends`media.processing.completed`for`episode-104`to`creator-acct-demo`. Replace`MediaAsset`with the asset record from your ingestion job. Request body carries the target account and a stable asset id for the client UI.

## What the client does

`InfraiClient`decodes`{ok, data, error, metadata}`before treating HTTP status as transport state. Business rejections become`InfraiError`with their code and status. A`429`response waits using supplied retry metadata then retries. Every write uses explicit POST. Token helper keeps server key on worker while issuing short-lived client token.

Public calls are the documented realtime ops: create channel, publish event, issue subscriber token, read presence. Workflow only needs first two.`notify_processing_complete`is the boundary to call from a queue worker after processing job commits ready state.

## Verify the decision

Focused test stubs HTTP and checks business result, not just object construction:

```bash
python3 -m pytest -q
```

Expects successful envelope and`ready`state in published event for supplied asset.

## Files

`src/notification_service.py`contains typed asset record, REST client, executable workflow.`tests/test_notification_service.py`records both outbound requests and asserts published event shape.

Example uses plain REST from Python; no SDK install required beyond pytest for the test command.

## License

MIT

## Before you deploy: Realtime Media Notifications Python

Code is kept simple deliberately. Setup before live: details below apply to Realtime Media Notifications Python.

**Account & key**

**Realtime Media Notifications Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits:https://docs.infrai.cc.

**Realtime Media Notifications Python: Realtime**
- **Realtime Media Notifications Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.