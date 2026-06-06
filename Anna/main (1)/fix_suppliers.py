import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Получаем уникальных поставщиков из товаров
cursor.execute('''
    SELECT DISTINCT supplier_name 
    FROM products 
    WHERE supplier_name IS NOT NULL AND supplier_name != ""
''')

suppliers = cursor.fetchall()
print(f"Найдено уникальных поставщиков в товарах: {len(suppliers)}")

# Добавляем их в таблицу suppliers
added = 0
for sup in suppliers:
    supplier_name = sup[0]
    try:
        cursor.execute('INSERT INTO suppliers (name) VALUES (?)', (supplier_name,))
        added += 1
        print(f"  Добавлен: {supplier_name}")
    except sqlite3.IntegrityError:
        print(f"  Уже существует: {supplier_name}")

conn.commit()
conn.close()
print(f"\nДобавлено поставщиков: {added}")