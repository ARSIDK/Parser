from abc import ABC, abstractmethod
from typing import List, Dict, Any
import time
from core.logger import setup_logger
from core.config import REQUEST_DELAY, MAX_RETRIES, TIMEOUT
import requests
from fake_useragent import UserAgent

class BaseParser(ABC):
    """Базовый класс для всех парсеров"""
    
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        self.session = requests.Session()
        self.ua = UserAgent()
    
    def _get_headers(self) -> Dict[str, str]:
        """Получение заголовков для запроса"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """Выполнение HTTP запроса с повторными попытками"""
        
        for attempt in range(MAX_RETRIES):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(
                        url,
                        headers=self._get_headers(),
                        timeout=TIMEOUT,
                        **kwargs
                    )
                else:
                    response = self.session.post(
                        url,
                        headers=self._get_headers(),
                        timeout=TIMEOUT,
                        **kwargs
                    )
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Попытка {attempt + 1} не удалась: {e}")
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(REQUEST_DELAY)
        
        raise Exception("Превышено максимальное количество попыток")
    
    def _delay(self):
        """Задержка между запросами"""
        time.sleep(REQUEST_DELAY)
    
    @abstractmethod
    def parse(self, **kwargs) -> List[Dict[str, Any]]:
        """Основной метод парсинга"""
        pass
    
    @abstractmethod
    def _extract_data(self, raw_data: Any) -> Dict[str, Any]:
        """Извлечение данных из сырого ответа"""
        pass