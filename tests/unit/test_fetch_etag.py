import json

import httpx
import pytest

from ipoinsight.ingest.fetch import Source, fetch_all


@pytest.mark.asyncio
async def test_refresh_sends_etag_and_reuses_unchanged_file(tmp_path):
    requests = []
    body = b"test offer document"

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)

        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\\nAllow: /\\n")

        if request.headers.get("If-None-Match") == '"v1"':
            return httpx.Response(304, headers={"ETag": '"v1"'})

        return httpx.Response(
            200,
            content=body,
            headers={
                "Content-Type": "application/pdf",
                "ETag": '"v1"',
            },
        )

    source = Source(
        url="https://example.com/offer.pdf",
        source="test-source",
        licence="Test",
        title="Test offer document",
    )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        first = await fetch_all(
            [source],
            root=tmp_path,
            client=client,
            per_host_delay=0,
        )

        manifest_path = tmp_path / "data" / "manifest.jsonl"
        first_record = json.loads(manifest_path.read_text(encoding="utf-8").splitlines()[-1])
        saved_file = tmp_path / first_record["path"]
        original_bytes = saved_file.read_bytes()

        second = await fetch_all(
            [source],
            root=tmp_path,
            client=client,
            per_host_delay=0,
            refresh=True,
        )

    document_requests = [request for request in requests if request.url.path == "/offer.pdf"]

    assert first["downloaded"] == 1
    assert first_record["etag"] == '"v1"'
    assert second["unchanged"] == 1
    assert second["downloaded"] == 0
    assert len(document_requests) == 2
    assert document_requests[1].headers["If-None-Match"] == '"v1"'
    assert saved_file.read_bytes() == original_bytes

    latest_record = json.loads(manifest_path.read_text(encoding="utf-8").splitlines()[-1])
    assert latest_record["http_status"] == 304
    assert latest_record["status"] == "downloaded"
    assert latest_record["etag"] == '"v1"'
    assert latest_record["sha256"] == first_record["sha256"]
