import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from .config import DATABASE_PATH
from .logger import setup_logger

logger = setup_logger("database")

class Database:
    
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS private_sector (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                address TEXT,
                region TEXT,
                city TEXT,
                contacts TEXT,
                email TEXT,
                phone TEXT,
                website TEXT,
                social_links TEXT,
                category TEXT,
                specialization TEXT,
                source TEXT,
                parsed_date TIMESTAMP,
                raw_data TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS public_institutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                address TEXT,
                region TEXT,
                city TEXT,
                contacts TEXT,
                email TEXT,
                phone TEXT,
                website TEXT,
                social_links TEXT,
                institution_type TEXT,
                source TEXT,
                parsed_date TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS government_procurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organizer TEXT,
                customer TEXT,
                amount REAL,
                subject TEXT,
                contacts TEXT,
                documentation_link TEXT,
                procurement_link TEXT,
                parsed_date TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                sector TEXT,
                options TEXT,
                results_count INTEGER,
                search_date TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        logger.info("База данных инициализирована")
    
    def save_private_data(self, data: List[Dict[str, Any]]) -> int:
        """Сохранение данных частного сектора"""
        
        count = 0
        for item in data:
            try:
                self.cursor.execute('''
                    INSERT INTO private_sector (
                        name, address, region, city, contacts, email, phone,
                        website, social_links, category, specialization, source,
                        parsed_date, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('name'),
                    item.get('address'),
                    item.get('region'),
                    item.get('city'),
                    item.get('contacts'),
                    item.get('email'),
                    item.get('phone'),
                    item.get('website'),
                    item.get('social_links'),
                    item.get('category'),
                    item.get('specialization'),
                    item.get('source'),
                    datetime.now(),
                    str(item)
                ))
                count += 1
            except Exception as e:
                logger.error(f"Ошибка сохранения: {e}")
        
        self.conn.commit()
        logger.info(f"Сохранено {count} записей")
        return count
    
    def save_procurement_data(self, data: List[Dict[str, Any]]) -> int:
        """Сохранение данных госзакупок"""
        
        count = 0
        for item in data:
            try:
                self.cursor.execute('''
                    INSERT INTO government_procurements (
                        organizer, customer, amount, subject, contacts,
                        documentation_link, procurement_link, parsed_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('organizer'),
                    item.get('customer'),
                    item.get('amount'),
                    item.get('subject'),
                    item.get('contacts'),
                    item.get('documentation_link'),
                    item.get('procurement_link'),
                    datetime.now()
                ))
                count += 1
            except Exception as e:
                logger.error(f"Ошибка сохранения: {e}")
        
        self.conn.commit()
        logger.info(f"Сохранено {count} закупок")
        return count
    
    def search(self, query: str, sector: str, limit: int = 100) -> List[Dict]:
        """Поиск по данным"""
        
        table = "private_sector" if sector == "private" else "public_institutions"
        
        self.cursor.execute(f'''
            SELECT * FROM {table}
            WHERE name LIKE ? OR address LIKE ? OR contacts LIKE ?
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        
        columns = [description[0] for description in self.cursor.description]
        results = []
        
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def close(self):
        """Закрытие соединения"""
        self.conn.close()