from .gpt import GPTService

SERVICES_MAP = {
    'chat': GPTService,
    'chathistory': GPTService,
    'chathist': GPTService,
    'chatload': GPTService,
    'chatsave': GPTService,
    'chatdiscard': GPTService,
}