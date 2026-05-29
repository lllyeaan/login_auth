from werkzeug.security import generate_password_hash
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="login_auth_db"
)

cursor = db.cursor()

username = "admin"
password = "Admin123"
password_hash = generate_password_hash(password)

cursor.execute(
    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
    (username, password_hash, "admin")
)

db.commit()
cursor.close()
db.close()

print("Akun admin berhasil dibuat.")