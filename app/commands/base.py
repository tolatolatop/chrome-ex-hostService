from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, Union
from fastapi import WebSocket
from app.exceptions import ParamTypeError
from app.models.message import Message, CommandType, MessageType
from app.websocket.context import ContextManager
import json
import logging

logger = logging.getLogger(__name__)

class BaseCommand(ABC):
    """命令处理器的基类"""
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    @property
    @abstractmethod
    def command_name(self) -> str:
        """命令名称"""
        pass

    @property
    def help_text(self) -> str:
        """命令帮助文本"""
        return "没有帮助信息"

    async def get_command_param(
        self,
        websocket: WebSocket,
        name: str,
        help_text: str,
        d_type: Type,
        default: Any = None
    ) -> Any:
        """获取命令参数
        
        Args:
            websocket: WebSocket 连接
            name: 参数名称
            help_text: 参数说明
            d_type: 参数类型
            default: 默认值，如果提供则为可选参数
        
        Returns:
            解析后的参数值
            
        Raises:
            ParamTypeError: 参数类型错误
        """
        logger.debug(
            "开始获取参数: name=%s, type=%s, required=%s, default=%s",
            name,
            d_type.__name__,
            default is None,
            default
        )
        
        # 构建参数请求消息
        param_request = Message.create_system_command(
            CommandType.PARAMS_REQUEST,
            data={
                "param_name": name,
                "description": help_text,
                "required": default is None,
                "default": default
            }
        )
        await websocket.send_text(param_request.to_json())
        
        # 接收参数值
        response = await websocket.receive_text()
        logger.debug("收到参数响应: %s", response)
        param_data = json.loads(response)
        logger.debug("解析后的参数数据: %s", param_data)
        
        try:
            # 获取参数值
            value = param_data.get('content', default)
            
            # 如果是必需参数但没有提供值
            if value is None and default is None:
                raise ParamTypeError(f"必需参数 {name} 未提供值")
                
            # 尝试转换类型
            if value is not None:
                if d_type == bool and isinstance(value, str):
                    value = value.lower() in ('true', '1', 'yes', 'y')
                else:
                    value = d_type(value)
                    
            return value
            
        except (ValueError, TypeError) as e:
            raise ParamTypeError(f"参数 {name} 的值 '{value}' 无法转换为 {d_type.__name__} 类型")

    @abstractmethod
    async def execute(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        """执行命令"""
        pass

    async def send_response(self, websocket: WebSocket, content: str, data: Optional[Dict[str, Any]] = None) -> None:
        """发送响应消息"""
        response = Message.create_response(content, data)
        await websocket.send_text(response.to_json())

    async def send_error(self, websocket: WebSocket, error_message: str) -> None:
        """发送错误消息"""
        error = Message.create_error(error_message)
        await websocket.send_text(error.to_json()) 