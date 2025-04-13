from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..channel import channel, Message, ResponseMessage
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/{uid}/client")
async def websocket_endpoint(websocket: WebSocket, uid: str):
    await websocket.accept()
    channel.create_channel(uid)
    while True:
        try:
            message = await channel.receive_request(uid)
            data = message.model_dump()
            logger.info("receive request %s %s", uid, data)
            await websocket.send_json(data)
            while True:
                response = await websocket.receive_json()
                response_message = ResponseMessage(**response)
                if response_message.request_id != message.request_id:
                    logger.info("drop response %s %s", uid,
                                response_message.data)
                    continue
                logger.info("send response %s %s", uid, response_message.data)
                await channel.send_response(uid, message.request_id, response_message.data)
        except WebSocketDisconnect:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            break
    channel.destory_channel(uid)
