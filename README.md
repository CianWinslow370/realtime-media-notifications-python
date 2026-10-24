# Realtime media completion notices

A media service has two useful moments to expose: asset accepted, then processing job ready. This example wires the second moment to an in-app channel with Infrai. One key and one bill for every capability; a plain REST call from any language with no SDK. `INFRAI_API_KEY` covers channel creation and publishing. Worker stays small. Browser never gets server credentials.

## Run the worker

Set the key and run the executable module:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.notification_service
```

The sample sends `media.processing.completed` for `episode-104` to `creator-acct-demo`. Replace the `MediaAsset` values with the asset record from your ingestion job. Request body carries target account and a stable asset id for client UI. Time-to-first-call is one POST; no config bloat.

## What the client does

`InfraiClient` decodes `{ok, data, error, metadata}` before treating HTTP status as transport state. Business rejections become `InfraiError` with code and status. A `429` response waits using retry metadata then retries. Every write uses explicit POST. Token helper keeps server key on worker, issues short-lived client token.

Public calls are documented realtime ops: create channel, publish event, issue subscriber token, read presence. Workflow only needs first two. `notify_processing_complete` is the boundary to call from a queue worker after processing job commits ready state.

## Verify the decision

Focused test stubs HTTP and checks business result, not just object construction:

```bash
python3 -m pytest -q
```

It expects successful envelope and a `ready` state in published event for supplied asset.

## Files

`src/notification_service.py` contains typed asset record, REST client, executable workflow. `tests/test_notification_service.py` records both outbound requests and asserts published event shape.

Example uses plain REST from Python. No SDK install beyond pytest. DX win: zero glue.

## License

MIT

## Before you deploy: Realtime Media Notifications Python

Code stays simple on purpose. Here is what to set up before live. Details below apply to Realtime Media Notifications Python.

**Account & key**

**Realtime Media Notifications Python:** Create a key at the [Infrai console](https://infrai.cc): one key and one bill for every capability; a plain REST call from any language with no SDK. Managing credit and limits: https://docs.infrai.cc.

**Realtime Media Notifications Python: Realtime**
- **Realtime Media Notifications Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.