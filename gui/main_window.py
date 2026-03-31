import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread
from typing import Dict, Any

from core.database import Database
from parsers.avito_parser import AvitoParser
from parsers.vk_parser import VKParser
from exporters.data_exporter import DataExporter

class ParserGUI:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Music Market Parser")
        self.root.geometry("1200x700")
        
        self.db = Database()
        self.exporter = DataExporter()
        
        self._setup_ui()
    
    def _setup_ui(self):
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.parse_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.parse_frame, text="Парсинг")
        self._setup_parse_tab()
        
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Поиск")
        self._setup_search_tab()
        
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="История")
        self._setup_history_tab()
    
    def _setup_parse_tab(self):
        """Настройка вкладки парсинга"""
        
        sector_frame = ttk.LabelFrame(self.parse_frame, text="Сектор", padding=10)
        sector_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.sector_var = tk.StringVar(value="private")
        ttk.Radiobutton(sector_frame, text="Частный сектор", 
                       variable=self.sector_var, value="private").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sector_frame, text="Государственный сектор", 
                       variable=self.sector_var, value="public").pack(side=tk.LEFT, padx=5)
        
        params_frame = ttk.LabelFrame(self.parse_frame, text="Параметры", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Поисковый запрос:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.query_entry = ttk.Entry(params_frame, width=50)
        self.query_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(params_frame, text="Регион:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.region_entry = ttk.Entry(params_frame, width=50)
        self.region_entry.grid(row=1, column=1, pady=5, padx=5)
        self.region_entry.insert(0, "Россия")
        
        ttk.Label(params_frame, text="Лимит записей:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.limit_spinbox = ttk.Spinbox(params_frame, from_=1, to=1000, width=10)
        self.limit_spinbox.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        self.limit_spinbox.set(100)
        
        options_frame = ttk.LabelFrame(self.parse_frame, text="Опции", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.foreign_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Анализ зарубежных объектов", 
                       variable=self.foreign_var).pack(side=tk.LEFT, padx=5)
        
        buttons_frame = ttk.Frame(self.parse_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.parse_btn = ttk.Button(buttons_frame, text="Начать парсинг", 
                                    command=self.start_parsing)
        self.parse_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(buttons_frame, text="Экспорт результатов", 
                                     command=self.export_results, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        results_frame = ttk.LabelFrame(self.parse_frame, text="Результаты", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(self.parse_frame, show="headings", height=10)
        
    def _setup_search_tab(self):
        
        search_frame = ttk.Frame(self.search_frame, padding=10)
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Поисковый запрос:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Найти", command=self.search_data).pack(side=tk.LEFT, padx=5)
        
        self.search_tree = ttk.Treeview(self.search_frame, show="headings", height=20)
        self.search_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(self.search_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_tree.configure(yscrollcommand=scrollbar.set)
    
    def _setup_history_tab(self):
        
        self.history_tree = ttk.Treeview(self.history_frame, show="headings", height=20)
        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.history_tree["columns"] = ("query", "sector", "results_count", "date")
        self.history_tree.heading("query", text="Запрос")
        self.history_tree.heading("sector", text="Сектор")
        self.history_tree.heading("results_count", text="Результатов")
        self.history_tree.heading("date", text="Дата")
        
        ttk.Button(self.history_frame, text="Обновить", 
                  command=self.load_history).pack(pady=5)
    
    def start_parsing(self):
        """Запуск парсинга в отдельном потоке"""
        
        self.parse_btn.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Начинаем парсинг...\n")
        
        thread = Thread(target=self._parsing_thread)
        thread.start()
    
    def _parsing_thread(self):
        """Поток парсинга"""
        
        try:
            query = self.query_entry.get()
            region = self.region_entry.get()
            limit = int(self.limit_spinbox.get())
            
            if not query:
                messagebox.showwarning("Предупреждение", "Введите поисковый запрос")
                return
            
            results = []
            
            if self.sector_var.get() == "private":
                self.results_text.insert(tk.END, "Парсинг Avito...\n")
                avito_parser = AvitoParser()
                avito_results = avito_parser.parse(query, region, limit)
                results.extend(avito_results)
                
                self.results_text.insert(tk.END, "Парсинг VK...\n")
                vk_parser = VKParser()
                vk_results = vk_parser.parse(query, limit)
                results.extend(vk_results)
            
            if results:
                self.db.save_private_data(results)
                self.results_text.insert(tk.END, f"Сохранено {len(results)} записей\n")
                
                for i, result in enumerate(results[:5]):
                    self.results_text.insert(tk.END, f"\n--- Результат {i+1} ---\n")
                    self.results_text.insert(tk.END, f"Название: {result.get('name', '')}\n")
                    self.results_text.insert(tk.END, f"Категория: {result.get('category', '')}\n")
                    self.results_text.insert(tk.END, f"Источник: {result.get('source', '')}\n")
                
                self.export_btn.config(state=tk.NORMAL)
            else:
                self.results_text.insert(tk.END, "Результаты не найдены\n")
            
        except Exception as e:
            self.results_text.insert(tk.END, f"Ошибка: {str(e)}\n")
            messagebox.showerror("Ошибка", str(e))
        
        finally:
            self.parse_btn.config(state=tk.NORMAL)
    
    def export_results(self):
        """Экспорт результатов"""
        
        file_types = [
            ("Excel files", "*.xlsx"),
            ("Word files", "*.docx"),
            ("PDF files", "*.pdf")
        ]
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=file_types
        )
        
        if filename:
            try:
                
                messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    def search_data(self):
        """Поиск данных"""
        
        query = self.search_entry.get()
        
        if not query:
            messagebox.showwarning("Предупреждение", "Введите поисковый запрос")
            return
        
        results = self.db.search(query, "private")
        
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        if results:

            columns = list(results[0].keys())
            self.search_tree["columns"] = columns
            
            for col in columns:
                self.search_tree.heading(col, text=col)
                self.search_tree.column(col, width=100)
            
            for result in results:
                values = [str(result.get(col, ""))[:50] for col in columns]
                self.search_tree.insert("", tk.END, values=values)
        else:
            messagebox.showinfo("Результаты", "Ничего не найдено")
    
    def load_history(self):
        """Загрузка истории запросов"""
        
        pass
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()
        self.db.close()