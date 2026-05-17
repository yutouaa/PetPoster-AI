import base64
import asyncio
from types import SimpleNamespace

from app.services.ai_service import AIService


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = "dummy error"

    def json(self):
        return self._payload


class DummyClient:
    def __init__(self, payload):
        self.payload = payload
        self.requests = []

    async def post(self, url, json):
        self.requests.append({"url": url, "json": json})
        return DummyResponse(self.payload)

    async def aclose(self):
        return None


def make_settings(tmp_path):
    return SimpleNamespace(
        rightcode_base_url="https://www.right.codes/draw",
        rightcode_model="gpt-image-2",
        rightcode_api_key="test-key",
        rightcode_timeout=30,
        generated_image_dir=str(tmp_path),
        public_base_url="http://127.0.0.1:8000",
    )


def test_generate_image_posts_to_rightcode_images_endpoint(tmp_path):
    client = DummyClient({"data": [{"url": "https://cdn.example.com/result.png"}]})
    service = AIService(settings=make_settings(tmp_path), client=client)

    result = asyncio.run(
        service.generate_image("一只猫的海报", "低清晰度", ["https://example.com/pet.png"])
    )

    assert result == {"image_url": "https://cdn.example.com/result.png", "cost": 0}
    assert client.requests[0]["url"] == "/v1/images/generations"
    assert client.requests[0]["json"]["model"] == "gpt-image-2"
    assert "一只猫的海报" in client.requests[0]["json"]["prompt"]
    assert "不要包含：低清晰度" in client.requests[0]["json"]["prompt"]
    assert "参考图片：https://example.com/pet.png" in client.requests[0]["json"]["prompt"]
    assert client.requests[0]["json"]["size"] == "1024x1024"
    assert client.requests[0]["json"]["n"] == 1


def test_generate_image_saves_base64_result_as_public_upload(tmp_path):
    raw_image = b"fake-png-bytes"
    b64 = base64.b64encode(raw_image).decode("ascii")
    client = DummyClient({"data": [{"b64_json": b64}]})
    service = AIService(settings=make_settings(tmp_path), client=client)

    result = asyncio.run(service.generate_image("一只狗的海报"))

    assert result["image_url"].startswith("http://127.0.0.1:8000/uploads/generated-")
    saved_name = result["image_url"].rsplit("/", 1)[-1]
    assert (tmp_path / saved_name).read_bytes() == raw_image
