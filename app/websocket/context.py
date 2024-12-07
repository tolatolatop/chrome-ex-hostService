from typing import Dict, List, Optional
from datetime import datetime
from app.models.message import Message
from dataclasses import dataclass, field

@dataclass
class UserContext:
    """用户上下文信息"""
    user_id: str
    username: str
    connected_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    message_count: int = 0

@dataclass
class ChatContext:
    """聊天上下文信息"""
    conversation_id: str
    started_at: datetime = field(default_factory=datetime.now)
    message_history: List[Message] = field(default_factory=list)
    user_context: Optional[UserContext] = None
    metadata: Dict = field(default_factory=dict)

    def add_message(self, message: Message) -> None:
        """添加消息到历史记录"""
        self.message_history.append(message)
        if self.user_context:
            self.user_context.message_count += 1
            self.user_context.last_active = datetime.now()

    def get_last_n_messages(self, n: int) -> List[Message]:
        """获取最近的n条消息"""
        return self.message_history[-n:] if n > 0 else []

    def get_messages_by_type(self, message_type: str) -> List[Message]:
        """按类型获取消息"""
        return [msg for msg in self.message_history if msg.type == message_type]

    def clear_history(self) -> None:
        """清除消息历史"""
        self.message_history.clear()

class ContextManager:
    """对话上下文管理器"""
    def __init__(self):
        self.active_contexts: Dict[str, ChatContext] = {}
        self.user_contexts: Dict[str, UserContext] = {}

    def create_context(self, conversation_id: str, user_id: str, username: str) -> ChatContext:
        """创建新的对话上下文"""
        user_context = self.get_or_create_user_context(user_id, username)
        context = ChatContext(
            conversation_id=conversation_id,
            user_context=user_context
        )
        self.active_contexts[conversation_id] = context
        return context

    def get_or_create_user_context(self, user_id: str, username: str) -> UserContext:
        """获取或创建用户上下文"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = UserContext(user_id=user_id, username=username)
        return self.user_contexts[user_id]

    def get_context(self, conversation_id: str) -> Optional[ChatContext]:
        """获取对话上下文"""
        return self.active_contexts.get(conversation_id)

    def update_username(self, user_id: str, new_username: str) -> None:
        """更新用户名"""
        if user_id in self.user_contexts:
            self.user_contexts[user_id].username = new_username

    def close_context(self, conversation_id: str) -> None:
        """关闭对话上下文"""
        if conversation_id in self.active_contexts:
            del self.active_contexts[conversation_id] 