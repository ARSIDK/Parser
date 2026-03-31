from typing import List, Dict, Any
import requests
from .base_parser import BaseParser
from core.config import REQUEST_DELAY

class VKParser(BaseParser):
    """Парсер VK API"""
    
    def __init__(self, access_token: str = None):
        super().__init__()
        self.api_url = "https://api.vk.com/method/"
        self.access_token = access_token or self._get_default_token()
        self.api_version = "5.131"
    
    def _get_default_token(self) -> str:
        """Получение токена (в реальном приложении нужно получать через OAuth)"""
        # Для учебного проекта используем заглушку
        return "your_vk_access_token"
    
    def _make_api_request(self, method: str, params: Dict) -> Dict:
        """Выполнение запроса к VK API"""
        
        params.update({
            'access_token': self.access_token,
            'v': self.api_version
        })
        
        try:
            response = self._make_request(
                f"{self.api_url}{method}",
                params=params
            )
            return response.json()
        except Exception as e:
            self.logger.error(f"Ошибка API VK: {e}")
            return {}
    
    def parse(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Поиск групп и сообществ"""
        
        results = []
        
        # Поиск групп
        groups = self._search_groups(query, limit)
        
        for group in groups:
            data = self._extract_data(group)
            if data:
                results.append(data)
        
        return results
    
    def _search_groups(self, query: str, limit: int) -> List[Dict]:
        """Поиск групп по ключевому слову"""
        
        params = {
            'q': query,
            'type': 'group',
            'count': limit
        }
        
        response = self._make_api_request('groups.search', params)
        
        if response.get('response'):
            return response['response'].get('items', [])
        
        return []
    
    def _extract_data(self, group: Dict) -> Dict[str, Any]:
        """Извлечение данных о группе"""
        
        try:
            # Получаем дополнительную информацию о группе
            params = {
                'group_id': group['id'],
                'fields': 'contacts,site,status,description'
            }
            
            response = self._make_api_request('groups.getById', params)
            
            if response.get('response'):
                group_info = response['response'][0]
                
                return {
                    'name': group_info.get('name', ''),
                    'address': '',
                    'region': '',
                    'city': '',
                    'contacts': group_info.get('contacts', ''),
                    'email': '',
                    'phone': '',
                    'website': group_info.get('site', ''),
                    'social_links': f"https://vk.com/{group_info.get('screen_name', '')}",
                    'category': self._determine_category(group_info.get('description', '')),
                    'specialization': '',
                    'source': 'VK',
                    'parsed_date': ''
                }
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки группы: {e}")
        
        return None
    
    def _determine_category(self, description: str) -> str:
        """Определение категории по описанию"""
        
        if not description:
            return "other"
        
        description_lower = description.lower()
        
        from core.config import KEYWORDS
        
        for category, keywords in KEYWORDS.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return "other"