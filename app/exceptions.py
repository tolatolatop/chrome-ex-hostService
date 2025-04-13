class ChatError(Exception):
    """聊天应用的基础异常类"""
    pass


class ContextError(ChatError):
    """上下文相关的错误"""
    pass


class NoContextError(ContextError):
    """找不到上下文的错误"""
    pass


class NoUserContextError(ContextError):
    """找不到用户上下文的错误"""
    pass


class ParamTypeError(Exception):
    """参数类型错误"""
    pass


class ConnectionError(Exception):
    """连接错误"""
    pass


class NoConnectionError(ConnectionError):
    """没有连接的错误"""
    pass


class NoResponseError(Exception):
    """没有响应的错误"""
    pass
