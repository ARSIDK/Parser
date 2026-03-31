from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_parser import BaseParser

class AvitoParser(BaseParser):
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.avito.ru"
    
    def parse(self, query: str, region: str = "rossiya", limit: int = 50) -> List[Dict[str, Any]]:
        
        results = []
        url = f"{self.base_url}/{region}/muzykalnye_instrumenty?q={query}"
        
        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            items = soup.find_all('div', {'data-marker': 'item'})[:limit]
            
            for item in items:
                try:
                    data = self._extract_data(item)
                    if data:
                        results.append(data)
                except Exception as e:
                    self.logger.error(f"Ошибка обработки объявления: {e}")
                    continue
            
            self._delay()
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга Avito: {e}")
        
        self.logger.info(f"Найдено {len(results)} объявлений")
        return results
    
    def _extract_data(self, item) -> Dict[str, Any]:
        
        try:
            title_elem = item.find('h3', {'data-marker': 'item-title'})
            name = title_elem.text.strip() if title_elem else ""
            
            price_elem = item.find('span', {'data-marker': 'item-price'})
            price = price_elem.text.strip() if price_elem else ""
            
            address_elem = item.find('div', {'data-marker': 'item-address'})
            address = address_elem.text.strip() if address_elem else ""
            
            link_elem = item.find('a', {'data-marker': 'item-title'})
            link = self.base_url + link_elem.get('href') if link_elem else ""
            
            category = self._determine_category(name)
            
            return {
                'name': name,
                'price': price,
                'address': address,
                'website': link,
                'source': 'Avito',
                'category': category,
                'contacts': '',
                'email': '',
                'phone': '',
                'social_links': '',
                'region': '',
                'city': ''
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка извлечения данных: {e}")
            return None
    
    def _determine_category(self, name: str) -> str:
    
        name_lower = name.lower()
        
        from core.config import KEYWORDS
        
        for category, keywords in KEYWORDS.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return category
        
        return "other"