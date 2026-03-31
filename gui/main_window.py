"""
Главное окно приложения - исправленная версия
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from threading import Thread
import sys
import os
from datetime import datetime

# Добавляем путь для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем парсеры
try:
    from parsers.avito_parser import AvitoParser
    from parsers.vk_parser import VKParser
    from parsers.yandex_maps_parser import YandexMapsParser
    from exporters.data_exporter import DataExporter
    PARSERS_AVAILABLE = True
    print("Парсеры успешно загружены")
except ImportError as e:
    print(f"Ошибка импорта парсеров: {e}")
    PARSERS_AVAILABLE = False
    # Создаем заглушки для тестирования
    class AvitoParser:
        def parse(self, query, region, limit): 
            return self._generate_test_data(query, limit)
        def _generate_test_data(self, query, limit):
            return [{'name': f'Тест: {query}', 'source': 'Avito', 'category': 'test'}]
    
    class VKParser:
        def parse(self, query, limit): 
            return [{'name': f'Группа: {query}', 'source': 'VK', 'category': 'test'}]
    
    class YandexMapsParser:
        def parse(self, query, region, limit): 
            return [{'name': f'Магазин: {query}', 'source': 'Yandex', 'category': 'test'}]
    
    class DataExporter:
        def export_to_excel(self, data, filename): pass
        def export_to_word(self, data, filename): pass
        def export_to_pdf(self, data, filename): pass

class ParserGUI:
    """Главное окно приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Music Market Parser - Анализ рынка музыкальных инструментов")
        self.root.geometry("1200x800")
        
        # Инициализация парсеров
        self.avito_parser = AvitoParser() if PARSERS_AVAILABLE else None
        self.vk_parser = VKParser() if PARSERS_AVAILABLE else None
        self.yandex_parser = YandexMapsParser() if PARSERS_AVAILABLE else None
        self.exporter = DataExporter()
        self.last_results = []
        
        self._setup_ui()
        self._show_welcome_message()
    
    def _show_welcome_message(self):
        """Показать приветственное сообщение"""
        if not PARSERS_AVAILABLE:
            self.results_text.insert(tk.END, 
                "⚠️ ВНИМАНИЕ: Парсеры работают в тестовом режиме!\n"
                "Для реального парсинга установите все зависимости.\n\n")
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        
        # Создание вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка парсинга
        self.parse_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.parse_frame, text="🔍 Парсинг")
        self._setup_parse_tab()
        
        # Вкладка поиска
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="📁 Поиск")
        self._setup_search_tab()
        
        # Вкладка информации
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="ℹ️ Информация")
        self._setup_info_tab()
    
    def _setup_parse_tab(self):
        """Настройка вкладки парсинга"""
        
        # Верхняя панель с параметрами
        params_frame = ttk.LabelFrame(self.parse_frame, text="Параметры поиска", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Поисковый запрос
        ttk.Label(params_frame, text="Поисковый запрос:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.query_entry = ttk.Entry(params_frame, width=60, font=('Arial', 10))
        self.query_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        ttk.Label(params_frame, text="(например: гитара, синтезатор, барабаны)", 
                 font=('Arial', 8)).grid(row=0, column=2, pady=5, padx=5, sticky=tk.W)
        
        # Регион
        ttk.Label(params_frame, text="Регион:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.region_entry = ttk.Entry(params_frame, width=30)
        self.region_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        self.region_entry.insert(0, "Россия")
        
        # Лимит
        ttk.Label(params_frame, text="Лимит записей:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.limit_spinbox = ttk.Spinbox(params_frame, from_=1, to=50, width=10)
        self.limit_spinbox.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        self.limit_spinbox.set(10)
        
        # Выбор источников
        sources_frame = ttk.LabelFrame(self.parse_frame, text="Источники данных", padding=10)
        sources_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.use_avito = tk.BooleanVar(value=True)
        self.use_vk = tk.BooleanVar(value=True)
        self.use_maps = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(sources_frame, text="Avito.ru (объявления)", 
                       variable=self.use_avito).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(sources_frame, text="VK.com (группы)", 
                       variable=self.use_vk).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(sources_frame, text="Яндекс.Карты (магазины)", 
                       variable=self.use_maps).pack(side=tk.LEFT, padx=10)
        
        # Кнопки
        buttons_frame = ttk.Frame(self.parse_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.parse_btn = ttk.Button(buttons_frame, text="🚀 Начать парсинг", 
                                    command=self.start_parsing,
                                    width=20)
        self.parse_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(buttons_frame, text="🗑️ Очистить", 
                                    command=self.clear_results,
                                    width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(buttons_frame, text="💾 Экспорт", 
                                     command=self.export_results, 
                                     state=tk.DISABLED,
                                     width=15)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Прогресс
        self.progress = ttk.Progressbar(self.parse_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
        # Текстовое поле для результатов
        results_frame = ttk.LabelFrame(self.parse_frame, text="Результаты парсинга", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                      font=('Courier', 9), height=20)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.parse_frame, textvariable=self.status_var, 
                               relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, padx=10, pady=5)
    
    def _setup_search_tab(self):
        """Настройка вкладки поиска"""
        
        search_frame = ttk.Frame(self.search_frame, padding=10)
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Поисковый запрос:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="🔍 Найти", command=self.search_data).pack(side=tk.LEFT, padx=5)
        
        # Результаты поиска
        self.search_tree = ttk.Treeview(self.search_frame, show="headings", height=20)
        self.search_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(self.search_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_tree.configure(yscrollcommand=scrollbar.set)
    
    def _setup_info_tab(self):
        """Настройка вкладки информации"""
        
        info_text = scrolledtext.ScrolledText(self.info_frame, wrap=tk.WORD, font=('Arial', 10))
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info = """
╔══════════════════════════════════════════════════════════════╗
║           Music Market Parser v2.0                          ║
║           Анализ рынка музыкальных инструментов              ║
╚══════════════════════════════════════════════════════════════╝

📌 НАЗНАЧЕНИЕ:
   Парсер для сбора и анализа данных о музыкальных инструментах
   из открытых источников

🔧 ФУНКЦИИ:
   ✓ Поиск объявлений на Avito.ru
   ✓ Поиск групп в VK.com
   ✓ Поиск магазинов на Яндекс.Картах
   ✓ Классификация музыкальных инструментов
   ✓ Экспорт данных (Excel, Word, PDF)

🎵 ПРИМЕРЫ ЗАПРОСОВ:
   • гитара
   • синтезатор
   • барабаны
   • модульный синтезатор
   • гонг
   • йога центр

📊 КАТЕГОРИИ ИНСТРУМЕНТОВ:
   • modular_synth - синтезаторы, электроника
   • percussion - ударные инструменты
   • gong - гонги, тибетские чаши
   • guitar - гитары
   • piano - клавишные
   • wind - духовые
   • string - струнные

💡 СОВЕТЫ:
   • Для точного поиска используйте конкретные названия
   • Укажите регион для локального анализа
   • Выберите нужные источники данных
   • Результаты можно экспортировать в разные форматы

⚠️ ВАЖНО:
   • При первом запуске может потребоваться время
   • Для работы требуется интернет-соединение
   • Соблюдайте этику использования

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            Учебный проект | 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        info_text.insert(tk.END, info)
        info_text.config(state=tk.DISABLED)
    
    def clear_results(self):
        """Очистка результатов"""
        self.results_text.delete(1.0, tk.END)
        self.export_btn.config(state=tk.DISABLED)
        self.results_text.insert(tk.END, "Результаты очищены. Введите новый запрос.\n")
        self.last_results = []
    
    def start_parsing(self):
        """Запуск парсинга"""
        
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Предупреждение", "Введите поисковый запрос!")
            return
        
        self.parse_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"🔍 Начинаем поиск по запросу: '{query}'\n")
        self.results_text.insert(tk.END, "="*60 + "\n\n")
        
        thread = Thread(target=self._parsing_thread)
        thread.daemon = True
        thread.start()
    
    def _parsing_thread(self):
        """Поток парсинга"""
        
        query = self.query_entry.get().strip()
        region = self.region_entry.get().strip()
        limit = int(self.limit_spinbox.get())
        
        all_results = []
        
        try:
            # Парсинг Avito
            if self.use_avito.get() and self.avito_parser:
                self.status_var.set("Парсинг Avito.ru...")
                self.results_text.insert(tk.END, "📌 Парсинг Avito.ru:\n")
                self.results_text.see(tk.END)
                
                avito_results = self.avito_parser.parse(query, region, limit)
                if avito_results:
                    all_results.extend(avito_results)
                    self.results_text.insert(tk.END, f"   ✅ Найдено: {len(avito_results)} объявлений\n\n")
                else:
                    self.results_text.insert(tk.END, f"   ❌ Ничего не найдено на Avito\n\n")
                
                self.results_text.see(tk.END)
            
            # Парсинг VK
            if self.use_vk.get() and self.vk_parser:
                self.status_var.set("Парсинг VK.com...")
                self.results_text.insert(tk.END, "📌 Парсинг VK.com:\n")
                
                vk_results = self.vk_parser.parse(query, limit)
                if vk_results:
                    all_results.extend(vk_results)
                    self.results_text.insert(tk.END, f"   ✅ Найдено: {len(vk_results)} групп\n\n")
                else:
                    self.results_text.insert(tk.END, f"   ❌ Ничего не найдено в VK\n\n")
                
                self.results_text.see(tk.END)
            
            # Парсинг Яндекс.Карт
            if self.use_maps.get() and self.yandex_parser:
                self.status_var.set("Парсинг Яндекс.Карт...")
                self.results_text.insert(tk.END, "📌 Парсинг Яндекс.Карт:\n")
                
                maps_results = self.yandex_parser.parse(query, region, limit)
                if maps_results:
                    all_results.extend(maps_results)
                    self.results_text.insert(tk.END, f"   ✅ Найдено: {len(maps_results)} организаций\n\n")
                else:
                    self.results_text.insert(tk.END, f"   ❌ Ничего не найдено на Яндекс.Картах\n\n")
                
                self.results_text.see(tk.END)
            
            # Вывод результатов
            self.results_text.insert(tk.END, "="*60 + "\n")
            self.results_text.insert(tk.END, f"📊 ИТОГО НАЙДЕНО: {len(all_results)} записей\n")
            self.results_text.insert(tk.END, "="*60 + "\n\n")
            
            if all_results:
                # Показываем первые 10 результатов
                self.results_text.insert(tk.END, "ПЕРВЫЕ РЕЗУЛЬТАТЫ:\n")
                self.results_text.insert(tk.END, "-"*40 + "\n")
                
                for i, result in enumerate(all_results[:10], 1):
                    self.results_text.insert(tk.END, f"\n{i}. {result.get('name', 'Без названия')}\n")
                    self.results_text.insert(tk.END, f"   Источник: {result.get('source', 'N/A')}\n")
                    self.results_text.insert(tk.END, f"   Категория: {result.get('category', 'other')}\n")
                    
                    if result.get('price'):
                        self.results_text.insert(tk.END, f"   Цена: {result['price']}\n")
                    if result.get('address'):
                        self.results_text.insert(tk.END, f"   Адрес: {result['address']}\n")
                    if result.get('website'):
                        self.results_text.insert(tk.END, f"   Сайт: {result['website']}\n")
                    if result.get('social_links'):
                        self.results_text.insert(tk.END, f"   Соцсети: {result['social_links']}\n")
                
                if len(all_results) > 10:
                    self.results_text.insert(tk.END, f"\n... и еще {len(all_results) - 10} записей\n")
                
                self.results_text.insert(tk.END, "\n✅ Парсинг завершен успешно!\n")
                self.results_text.insert(tk.END, "💡 Для экспорта результатов нажмите кнопку 'Экспорт'\n")
                
                # Сохраняем результаты для экспорта
                self.last_results = all_results
                self.export_btn.config(state=tk.NORMAL)
            else:
                self.results_text.insert(tk.END, "❌ НИЧЕГО НЕ НАЙДЕНО\n")
                self.results_text.insert(tk.END, "\n💡 СОВЕТЫ:\n")
                self.results_text.insert(tk.END, "   • Попробуйте изменить поисковый запрос\n")
                self.results_text.insert(tk.END, "   • Убедитесь, что выбраны источники данных\n")
                self.results_text.insert(tk.END, "   • Проверьте подключение к интернету\n")
                self.last_results = []
            
            self.status_var.set(f"Готов. Найдено: {len(all_results)} записей")
            
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            self.results_text.insert(tk.END, f"\n❌ {error_msg}\n")
            self.status_var.set("Ошибка парсинга")
            import traceback
            traceback.print_exc()
        
        finally:
            self.progress.stop()
            self.parse_btn.config(state=tk.NORMAL)
    
    def search_data(self):
        """Поиск данных"""
        
        query = self.search_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Предупреждение", "Введите поисковый запрос!")
            return
        
        if not self.last_results:
            messagebox.showinfo("Информация", "Нет данных для поиска. Сначала выполните парсинг.")
            return
        
        # Очистка таблицы
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Поиск в результатах
        found = []
        for item in self.last_results:
            item_str = str(item).lower()
            if query.lower() in item_str:
                found.append(item)
        
        if found:
            # Настройка колонок
            columns = list(found[0].keys())
            self.search_tree["columns"] = columns
            
            for col in columns:
                self.search_tree.heading(col, text=col)
                self.search_tree.column(col, width=100)
            
            # Добавление данных
            for result in found[:50]:  # Показываем первые 50
                values = [str(result.get(col, ""))[:50] for col in columns]
                self.search_tree.insert("", tk.END, values=values)
            
            messagebox.showinfo("Результаты поиска", f"Найдено {len(found)} записей")
        else:
            messagebox.showinfo("Результаты поиска", "Ничего не найдено")
    
    def export_results(self):
        """Экспорт результатов"""
        
        if not self.last_results:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта!")
            return
        
        # Выбор формата
        export_window = tk.Toplevel(self.root)
        export_window.title("Экспорт данных")
        export_window.geometry("400x250")
        export_window.resizable(False, False)
        
        # Центрируем окно
        export_window.transient(self.root)
        export_window.grab_set()
        
        ttk.Label(export_window, text="Выберите формат экспорта:", 
                 font=('Arial', 12)).pack(pady=20)
        
        format_var = tk.StringVar(value="excel")
        
        formats_frame = ttk.Frame(export_window)
        formats_frame.pack(pady=10)
        
        ttk.Radiobutton(formats_frame, text="Excel (.xlsx)", 
                       variable=format_var, value="excel").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(formats_frame, text="Word (.docx)", 
                       variable=format_var, value="word").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(formats_frame, text="PDF (.pdf)", 
                       variable=format_var, value="pdf").pack(anchor=tk.W, pady=5)
        
        def do_export():
            fmt = format_var.get()
            
            # Формируем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            query = self.query_entry.get().strip() or "export"
            filename = f"{query}_{timestamp}"
            
            if fmt == "excel":
                filename += ".xlsx"
                filetypes = [("Excel files", "*.xlsx")]
            elif fmt == "word":
                filename += ".docx"
                filetypes = [("Word files", "*.docx")]
            else:
                filename += ".pdf"
                filetypes = [("PDF files", "*.pdf")]
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=f".{fmt}",
                filetypes=filetypes,
                initialfile=filename
            )
            
            if filepath:
                try:
                    if fmt == "excel":
                        self.exporter.export_to_excel(self.last_results, filepath)
                    elif fmt == "word":
                        self.exporter.export_to_word(self.last_results, filepath)
                    else:
                        self.exporter.export_to_pdf(self.last_results, filepath)
                    
                    messagebox.showinfo("Успех", f"Данные экспортированы в:\n{filepath}")
                    export_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось экспортировать:\n{str(e)}")
        
        ttk.Button(export_window, text="Экспортировать", 
                  command=do_export).pack(pady=20)
        ttk.Button(export_window, text="Отмена", 
                  command=export_window.destroy).pack()
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

# Точка входа для тестирования
if __name__ == "__main__":
    app = ParserGUI()
    app.run()