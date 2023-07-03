from .gpt import GPTService
from .catering_service import CateringService

SERVICES_MAP = {
    'chat': GPTService,
    'chathistory': GPTService,
    'chathist': GPTService,
    'chatload': GPTService,
    'chatdelete': GPTService,
    'chatsave': GPTService,
    'chatdiscard': GPTService,
    'cater': CateringService,
    'Cater': CateringService,
    'catering': CateringService
}
