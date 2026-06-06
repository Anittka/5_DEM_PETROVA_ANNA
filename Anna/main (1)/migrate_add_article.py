import sqlite3
import openpyxl
import os

DB_NAME = 'database.db'
EXCEL_FILE = 'data/товар.xlsx'

def add_article_column_and_fill():
    # Проверяем, существует ли БД, НА ВСЯКИЙ СЛУЧАЙ
    if not os.path.exists(DB_NAME):
        print(f"Файл {DB_NAME} не найден. Сначала запустите main.py")
        return
    
    if not os.path.exists(EXCEL_FILE):
        print(f"Файл {EXCEL_FILE} не найден.")
        return
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # 1. Проверяем, есть ли колонка article
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'article' not in columns:
            print("Добавляем колонку article...")
            cursor.execute('ALTER TABLE products ADD COLUMN article TEXT')
            print("  Колонка article добавлена")
        else:
            print("Колонка article уже существует")
        
        # 2. Читаем артикулы из Excel
        print("\nЧитаем артикулы из Excel...")
        wb = openpyxl.load_workbook(EXCEL_FILE)
        sheet = wb.active
        
        article_map = {}
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row and row[0] and row[1]:
                article = str(row[0]).strip()
                name = str(row[1]).strip()
                article_map[name] = article
        
        print(f"Найдено соответствий: {len(article_map)}")
        
        # 3. Обновляем артикулы
        print("\nОбновляем артикулы...")
        updated = 0
        
        for name, article in article_map.items():
            cursor.execute('UPDATE products SET article = ? WHERE name = ?', (article, name))
            if cursor.rowcount > 0:
                updated += cursor.rowcount
                print(f"  Обновлён: {name[:30]}... -> {article}")
        
        conn.commit()
        
        # 4. Результат, ВЫВОД!
        cursor.execute('SELECT COUNT(*) FROM products WHERE article IS NOT NULL')
        filled = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM products')
        total = cursor.fetchone()[0]
        
        print(f"\nРезультат:")
        print(f"  Всего товаров: {total}")
        print(f"  Заполнено артикулов: {filled}")
        print(f"  Обновлено: {updated}")

if __name__ == "__main__":
    add_article_column_and_fill()