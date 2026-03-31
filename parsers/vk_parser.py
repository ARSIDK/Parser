"""
Парсер VK для поиска групп и сообществ
"""

import time
import random
from typing import List, Dict, Any
import requests

class VKParser:
    """Парсер VK API"""
    
    def __init__(self):
        self.api_url = "https://api.vk.com/method/"
        # Для учебного проекта используем публичный API без токена (ограниченные возможности)
        self.api_version = "5.131"
        print("VKParser инициализирован")
    
    def parse(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Поиск групп ВК по ключевым словам
        
        Args:
            query: поисковый запрос
            limit: максимальное количество результатов
        
        Returns:
            список найденных групп
        """
        
        results = []
        
        # Для учебного проекта возвращаем тестовые данные, так как VK API требует токен
        # В реальном проекте нужно добавить access_token
        print(f"Поиск групп ВК по запросу: {query}")
        
        # Создаем тестовые данные на основе запроса
        test_groups = self._generate_test_data(query, limit)
        
        for group in test_groups:
            data = self._extract_data(group)
            if data:
                results.append(data)
                print(f"  Найдена группа: {data['name']}")
        
        print(f"Всего найдено в VK: {len(results)}")
        return results
    
    def _generate_test_data(self, query: str, limit: int) -> List[Dict]:
        """Генерация тестовых данных для демонстрации"""
        
        test_data = []
        
        # Базовые названия групп
        group_templates = [
            f"{query} - музыкальный магазин",
            f"{query} для музыкантов",
            f"{query} в России",
            f"Купить {query}",
            f"Школа игры на {query}",
            f"Мастерская {query}",
            f"Сообщество {query}",
            f"{query} бу",
            f"Магазин музыкальных инструментов: {query}",
            f"Группа любителей {query}"
        ]
        
        # Ограничиваем количество
        templates = group_templates[:limit]
        
        for i, name in enumerate(templates):
            test_data.append({
                'id': i + 1,
                'name': name,
                'screen_name': query.replace(' ', '_').lower(),
                'description': f'Группа посвящена {query}. Обсуждаем, продаем, покупаем. Лучшие предложения по {query} в России.',
                'site': f'https://{query}.ru',
                'members_count': random.randint(100, 10000)
            })
        
        return test_data
    
    def _extract_data(self, group: Dict) -> Dict[str, Any]:
        """Извлечение данных о группе"""
        
        try:
            return {
                'name': group.get('name', ''),
                'address': '',
                'region': '',
                'city': '',
                'contacts': '',
                'email': '',
                'phone': '',
                'website': group.get('site', ''),
                'social_links': f"https://vk.com/{group.get('screen_name', '')}",
                'category': self._determine_category(group.get('description', '')),
                'specialization': group.get('name', ''),
                'source': 'VK',
                'members': group.get('members_count', 0)
            }
            
        except Exception as e:
            print(f"Ошибка обработки группы: {e}")
            return None
    
    def _determine_category(self, description: str) -> str:
        """Определение категории по описанию"""
        
        if not description:
            return "other"
        
        description_lower = description.lower()
        
        categories = {
            'modular_synth': ['синтезатор', 'электроника', 'модульный'],
            'percussion': ['барабан', 'ударный', 'перкуссия'],
            'gong': ['гонг', 'чаша', 'медитация'],
            'guitar': ['гитара', 'струнный'],
            'piano': ['пианино', 'клавишный', 'синтезатор'],
            'wind': ['духовой', 'саксофон', 'флейта']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'