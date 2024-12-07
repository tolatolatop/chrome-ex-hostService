from typing import Dict, Type
from fastapi import WebSocket
from app.models.message import Message, CommandType
from app.exceptions import ChatError
from app.commands.base import BaseCommand
from app.commands.help_command import HelpCommand
from app.commands.clear_command import ClearCommand
from app.commands.rename_command import RenameCommand
from app.commands.status_command import StatusCommand
from app.commands.history_command import HistoryCommand
from app.commands.unknown_command import UnknownCommand
from app.commands.fetch_command import FetchCommand
from .context import ContextManager

class CommandHandler:
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
        self.commands: Dict[str, BaseCommand] = {}
        self._register_default_commands()

    def _register_default_commands(self) -> None:
        """注册默认命令"""
        self.register_commands([
            HelpCommand,
            ClearCommand,
            RenameCommand,
            StatusCommand,
            HistoryCommand,
            FetchCommand
        ])

    def register_commands(self, command_classes: list[Type[BaseCommand]]) -> None:
        """注册多个命令"""
        for command_class in command_classes:
            self.register_command(command_class)

    def register_command(self, command_class: Type[BaseCommand]) -> None:
        """注册单个命令"""
        command = command_class(self.context_manager)
        self.commands[command.command_name] = command

    def get_command(self, command_type: CommandType) -> BaseCommand:
        """获取命令处理器"""
        return self.commands.get(command_type, UnknownCommand(self.context_manager))

    async def handle_command(self, websocket: WebSocket, message: Message, conversation_id: str) -> None:
        """处理命令消息"""
        try:
            command = self.get_command(message.command)
            await command.execute(websocket, message, conversation_id)
        except ChatError as e:
            error_msg = Message.create_error(str(e))
            await websocket.send_text(error_msg.to_json()) 