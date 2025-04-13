import pytest
from app.channel import channel


@pytest.mark.asyncio
async def test_channel():
    channel.create_channel("test")
    request_id = await channel.send_request("test", {"test": "test"})
    await channel.send_response("test", request_id, {"test": "test"})
    response = await channel.receive_response("test", request_id)
    assert response.data == {"test": "test"}
