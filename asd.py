import sqlite3

db_path = "data/universal/chroma.sqlite3"
conn = sqlite3.connect(db_path)

cursor = conn.execute("PRAGMA table_info(collections);")
columns = cursor.fetchall()

print("Estructura de la tabla 'collections':")
for column in columns:
    print(f"Nombre: {column[1]}, Tipo: {column[2]}")

conn.close()
