from .gpt import GPTService

SERVICES_MAP = {
    'chat': GPTService,
    'chathistory': GPTService,
    'chathist': GPTService,
    'chatload': GPTService,
    'chatdelete': GPTService,
    'chatsave': GPTService,
    'chatdiscard': GPTService,
}
