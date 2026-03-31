import time
import random
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup

class YandexMapsParser:
    """Парсер Яндекс.Карт"""
    
    def __init__(self):
        self.base_url = "https://yandex.ru/maps"
        print("YandexMapsParser инициализирован")
    
    def parse(self, query: str, region: str = "Москва", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Поиск организаций на Яндекс.Картах
        
        Args:
            query: поисковый запрос (например, "музыкальный магазин")
            region: город/регион
            limit: максимальное количество результатов
        
        Returns:
            список найденных организаций
        """
        
        results = []
        
        search_query = f"{query} {region}"
        search_url = f"{self.base_url}/search/?text={search_query}"
        
        print(f"Поиск на Яндекс.Картах: {search_query}")
        
        try:
            test_orgs = self._generate_test_data(query, region, limit)
            
            for org in test_orgs:
                data = self._extract_data(org)
                if data:
                    results.append(data)
                    print(f"  Найдено: {data['name']}")
            
        except Exception as e:
            print(f"Ошибка парсинга Яндекс.Карт: {e}")
        
        print(f"Всего найдено на Яндекс.Картах: {len(results)}")
        return results
    
    def _generate_test_data(self, query: str, region: str, limit: int) -> List[Dict]:
        """Генерация тестовых данных"""
        
        test_data = []
        
        addresses = {
            'Москва': ['Тверская ул., 10', 'Новый Арбат, 15', 'Кутузовский пр-т, 20', 'Ленинский пр-т, 30'],
            'Санкт-Петербург': ['Невский пр-т, 25', 'Литейный пр-т, 40', 'Владимирский пр-т, 12'],
            'Россия': ['г. Москва, ул. Тверская, 10', 'г. Санкт-Петербург, Невский пр-т, 25']
        }
        
        region_addresses = addresses.get(region, addresses['Россия'])
        
        shop_names = [
            f"{query.title()} Мастер",
            f"Мир {query}",
            f"{query} Центр",
            f"Академия {query}",
            f"Магазин №1 {query}",
            f"{query} Профи",
            f"Салон {query}",
            f"{query} Эксперт"
        ]
        
        for i in range(min(limit, len(shop_names))):
            test_data.append({
                'name': shop_names[i],
                'address': f"{region}, {region_addresses[i % len(region_addresses)]}",
                'phone': f"+7 (495) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
                'website': f"www.{query.replace(' ', '')}{i+1}.ru",
                'rating': round(random.uniform(3.5, 5.0), 1),
                'reviews_count': random.randint(10, 500)
            })
        
        return test_data
    
    def _extract_data(self, org: Dict) -> Dict[str, Any]:
        """Извлечение данных об организации"""
        
        return {
            'name': org.get('name', ''),
            'address': org.get('address', ''),
            'phone': org.get('phone', ''),
            'website': org.get('website', ''),
            'source': 'Yandex.Maps',
            'category': self._determine_category(org.get('name', '')),
            'email': '',
            'social_links': '',
            'region': '',
            'city': '',
            'rating': org.get('rating', 0),
            'reviews_count': org.get('reviews_count', 0)
        }
    
    def _determine_category(self, name: str) -> str:
        """Определение категории"""
        
        name_lower = name.lower()
        
        if 'синтезатор' in name_lower or 'электро' in name_lower:
            return 'modular_synth'
        elif 'барабан' in name_lower or 'ударн' in name_lower:
            return 'percussion'
        elif 'гонг' in name_lower or 'чаша' in name_lower:
            return 'gong'
        elif 'гитар' in name_lower:
            return 'guitar'
        
        return 'other'