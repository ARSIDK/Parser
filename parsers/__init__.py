"""
Модуль парсеров для различных источников данных
"""

from .base_parser import BaseParser
from .avito_parser import AvitoParser
from .vk_parser import VKParser

__all__ = ['BaseParser', 'AvitoParser', 'VKParser']