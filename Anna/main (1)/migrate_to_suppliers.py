import sqlite3
import os

DB_NAME = 'database.db'

def migrate_to_suppliers():
    """Миграция: создание таблицы suppliers и перенос данных"""
    
    if not os.path.exists(DB_NAME):
        print(f"Файл {DB_NAME} не найден. Сначала запустите main.py")
        return
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Начинаю миграцию базы данных...")
    
    # 1. Проверяем, есть ли уже таблица suppliers
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='suppliers'")
    if cursor.fetchone():
        print("Таблица suppliers уже существует. Проверяем структуру...")
        
        # Проверяем, есть ли supplier_id в products
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'supplier_id' in columns and 'supplier' not in columns:
            print("Миграция уже выполнена ранее. Ничего не делаем.")
            conn.close()
            return
    
    # 2. Создаём таблицу suppliers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            rating REAL DEFAULT 0,
            address TEXT
        )
    ''')
    print("  Таблица suppliers создана")
    
    # 3. Копируем уникальных поставщиков из products в suppliers
    cursor.execute('SELECT DISTINCT supplier FROM products WHERE supplier IS NOT NULL AND supplier != ""')
    suppliers = cursor.fetchall()
    
    added = 0
    for sup in suppliers:
        supplier_name = sup[0]
        try:
            cursor.execute('INSERT INTO suppliers (name) VALUES (?)', (supplier_name,))
            added += 1
            print(f"    Добавлен поставщик: {supplier_name}")
        except sqlite3.IntegrityError:
            # Уже существует
            pass
    
    print(f"  Добавлено поставщиков: {added}")
    
    # 4. Добавляем колонку supplier_id в products (если ещё нет)
    cursor.execute("PRAGMA table_info(products)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'supplier_id' not in columns:
        cursor.execute('ALTER TABLE products ADD COLUMN supplier_id INTEGER')
        print("  Добавлена колонка supplier_id")
    
    # 5. Обновляем supplier_id на основе старых имён поставщиков
    cursor.execute('''
        UPDATE products 
        SET supplier_id = (SELECT id FROM suppliers WHERE suppliers.name = products.supplier)
        WHERE supplier IS NOT NULL AND supplier != ""
    ''')
    print(f"  Обновлено {cursor.rowcount} записей в products")
    
    # 6. Пересоздаём таблицу products без старой колонки supplier
    # Сохраняем все данные, удаляем текст. поле supplier
    
    # Получаем список всех колонок кроме supplier
    cursor.execute("PRAGMA table_info(products)")
    all_columns = cursor.fetchall()
    keep_columns = [col[1] for col in all_columns if col[1] != 'supplier']
    columns_str = ', '.join(keep_columns)
    
    # Переименов. старую таблицу
    cursor.execute('ALTER TABLE products RENAME TO products_old')
    
    # Создаём новую таблицу без supplier
    cursor.execute(f'''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            manufacturer TEXT,
            supplier_id INTEGER,
            price REAL NOT NULL,
            unit TEXT,
            quantity INTEGER NOT NULL DEFAULT 0,
            discount REAL DEFAULT 0,
            image_path TEXT,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
    ''')
    
    # Копируем данные из старой таблицы
    cursor.execute(f'''
        INSERT INTO products ({columns_str})
        SELECT {columns_str} FROM products_old
    ''')
    
    # Удаляем старую таблицу
    cursor.execute('DROP TABLE products_old')
    print("  Старая колонка supplier удалена, данные сохранены")
    
    # 7. Обновляем последовательность ID
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='products'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='suppliers'")
    
    conn.commit()
    conn.close()
    
    print("\nМиграция завершена успешно")
    print("   Теперь поставщики хранятся в отдельной таблице.")
    print("   Запустите main.py для проверки.")

if __name__ == "__main__":
    migrate_to_suppliers()