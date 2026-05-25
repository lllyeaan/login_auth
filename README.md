## Buat database dulu (mysql)
USE login_auth_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

## Ubah bagian ini di app.py (kalau mysqlnya username dan pwnya beda)
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""


## Cara Menjalankan Web
Jalankan perintah ini diterminal:
1. pip install -r requirements.txt
2. run program dengan: python app.py

Setelah itu buka dibrowser: http://127.0.0.1:5000