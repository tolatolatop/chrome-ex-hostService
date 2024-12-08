from typing import Dict, Any
import json
import logging

from .fetch_command import FetchCommand, FetchCommandData
from fastapi import WebSocket
from app.models.message import Message, CommandType, MessageType
from app.exceptions import ParamTypeError

logger = logging.getLogger(__name__)


class AddFavCommand(FetchCommand):
    command_name = CommandType.ADD_FAV

    async def get_params(self, websocket: WebSocket) -> str:
        """从 WebSocket 获取参数"""
        try:
            # 获取必需参数
            rid = await self.get_command_param(
                websocket,
                "rid",
                "视频/专栏ID",
                str
            )
            
            add_media_ids = await self.get_command_param(
                websocket,
                "add_media_ids",
                "目标收藏夹ID",
                str
            )
            
            # 获取可选参数
            type_value = await self.get_command_param(
                websocket,
                "type",
                "内容类型，默认42(专栏)",
                int,
                default=42
            )
            
            platform = await self.get_command_param(
                websocket,
                "platform",
                "平台",
                str,
                default="web"
            )
            
            return f"rid={rid}&type={type_value}&add_media_ids={add_media_ids}&del_media_ids=&platform={platform}"
            
        except ParamTypeError as e:
            await self.send_error(websocket, str(e))
            raise

    async def execute(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        try:
            # 获取参数
            logger.debug("开始获取添加收藏命令参数")
            command_data = await self.get_params(websocket)
            logger.debug(f"获取到参数: {command_data}")
            
            # 构建请求数据
            logger.debug("构建请求数据")
            fetch_data = FetchCommandData(
                url="https://api.bilibili.com/x/v3/fav/resource/deal",
                method="POST",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data=command_data
            )
            logger.debug(f"构建的请求数据: {fetch_data}")

            # 使用 FetchCommand 发送请求
            logger.debug("开始发送请求")
            await self.send_fetch_request(websocket, fetch_data)
            fetch_response = await self.handle_fetch_response(websocket)
            logger.debug(f"收到响应: {fetch_response}")

            # 发送响应
            logger.debug("发送成功响应")
            await self.send_response(websocket, content="收藏添加完成", data=fetch_response.data) 
        except ParamTypeError:
            logger.debug("参数错误")
            return  # 参数错误已经发送了错误消息，直接返回