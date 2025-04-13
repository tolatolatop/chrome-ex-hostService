from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..channel import channel, Message

router = APIRouter()


@router.websocket("/ws/{uid}/client")
async def websocket_endpoint(websocket: WebSocket, uid: str):
    await websocket.accept()
    channel.create_channel(uid)
    while True:
        try:
            message = await channel.receive_request(uid)
            await websocket.send_json(message.data)
            response = await websocket.receive_json()
            await channel.send_response(uid, message.request_id, response)
        except WebSocketDisconnect:
            break
        except Exception as e:
            print(e)
            break
    channel.destory_channel(uid)
