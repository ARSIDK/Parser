import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui.main_window import ParserGUI
    print("Модуль gui.main_window успешно импортирован")
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Проверьте структуру проекта и наличие файла gui/main_window.py")
    sys.exit(1)

def main():
    
    try:
        print("Запуск Music Market Parser...")
        app = ParserGUI()
        app.run()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()