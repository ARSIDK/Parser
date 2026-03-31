"""
Парсер Avito.ru для поиска музыкальных инструментов
"""

import re
import time
import random
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent

# Добавляем путь для импортов
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from parsers.base_parser import BaseParser
except ImportError:
    # Создаем базовый класс если не найден
    class BaseParser:
        def __init__(self):
            self.logger = print
            self.session = requests.Session()
            self.ua = UserAgent()
        
        def _get_headers(self):
            return {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
        
        def _make_request(self, url):
            try:
                response = self.session.get(url, headers=self._get_headers(), timeout=30)
                response.raise_for_status()
                return response
            except Exception as e:
                print(f"Ошибка запроса: {e}")
                return None
        
        def _delay(self):
            time.sleep(random.uniform(2, 4))

class AvitoParser(BaseParser):
    """Парсер Avito.ru"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.avito.ru"
        print("AvitoParser инициализирован")
    
    def parse(self, query: str, region: str = "rossiya", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Парсинг объявлений Avito
        
        Args:
            query: поисковый запрос
            region: регион (по умолчанию Россия)
            limit: максимальное количество результатов
        
        Returns:
            список найденных объявлений
        """
        
        results = []
        
        # Формируем URL для поиска
        search_url = f"{self.base_url}/{region}/muzykalnye_instrumenty?q={query}"
        
        print(f"Парсинг Avito: {search_url}")
        
        try:
            response = self._make_request(search_url)
            if not response:
                print("Не удалось получить ответ от Avito")
                return results
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем объявления
            items = soup.find_all('div', {'data-marker': 'item'})
            
            if not items:
                # Альтернативный поиск
                items = soup.find_all('div', class_='iva-item-content')
            
            print(f"Найдено {len(items)} объявлений")
            
            # Ограничиваем количество
            items = items[:limit]
            
            for item in items:
                try:
                    data = self._extract_data(item, query)
                    if data and data.get('name'):
                        results.append(data)
                        print(f"  Найдено: {data['name'][:50]}")
                except Exception as e:
                    print(f"Ошибка обработки объявления: {e}")
                    continue
            
            self._delay()
            
        except Exception as e:
            print(f"Ошибка парсинга Avito: {e}")
        
        print(f"Всего найдено на Avito: {len(results)}")
        return results
    
    def _extract_data(self, item, query: str = "") -> Dict[str, Any]:
        """Извлечение данных из объявления"""
        
        try:
            data = {
                'name': '',
                'price': '',
                'address': '',
                'website': '',
                'source': 'Avito',
                'category': 'other',
                'contacts': '',
                'email': '',
                'phone': '',
                'social_links': '',
                'region': '',
                'city': ''
            }
            
            # Поиск названия
            title_elem = item.find('h3', {'data-marker': 'item-title'})
            if not title_elem:
                title_elem = item.find('a', class_='iva-item-title')
            
            if title_elem:
                data['name'] = title_elem.text.strip()
                # Получаем ссылку
                link = title_elem.get('href')
                if link:
                    if link.startswith('/'):
                        data['website'] = self.base_url + link
                    else:
                        data['website'] = link
            
            # Поиск цены
            price_elem = item.find('span', {'data-marker': 'item-price'})
            if not price_elem:
                price_elem = item.find('span', class_='price')
            
            if price_elem:
                data['price'] = price_elem.text.strip()
            
            # Поиск адреса
            address_elem = item.find('div', {'data-marker': 'item-address'})
            if not address_elem:
                address_elem = item.find('span', class_='geo')
            
            if address_elem:
                data['address'] = address_elem.text.strip()
            
            # Определяем категорию
            data['category'] = self._determine_category(data['name'] or query)
            
            return data
            
        except Exception as e:
            print(f"Ошибка извлечения данных: {e}")
            return None
    
    def _determine_category(self, text: str) -> str:
        """Определение категории инструмента"""
        
        text_lower = text.lower()
        
        categories = {
            'modular_synth': ['модульный синтезатор', 'eurorack', 'модуль', 'синтезатор модульный'],
            'percussion': ['барабан', 'ударная установка', 'тарелка', 'кахон', 'джембе', 'перкуссия'],
            'gong': ['гонг', 'трубогон', 'поющая чаша', 'тибетская чаша'],
            'guitar': ['гитара', 'электрогитара', 'акустическая гитара', 'бас-гитара'],
            'piano': ['пианино', 'фортепиано', 'рояль', 'синтезатор', 'клавиши'],
            'wind': ['саксофон', 'флейта', 'труба', 'кларнет', 'гобой'],
            'string': ['скрипка', 'виолончель', 'альт', 'контрабас']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        return 'other'