# CampusPulse AI - Production Deployment & Operations Guide

This guide provides complete instructions for deploying CampusPulse AI in production using Linux (Ubuntu 22.04 / 24.04 LTS), Nginx, Gunicorn, and MySQL 8.x, as well as Windows Server environments.

---

## 1. System Requirements

- **Operating System**: Ubuntu 22.04 / 24.04 LTS or Windows Server 2022+
- **Python**: Python 3.10 to Python 3.14
- **Database**: MySQL 8.0+ (or zero-friction embedded SQLite fallback)
- **Memory**: Minimum 4GB RAM (8GB recommended for concurrent ML inference)
- **Disk**: 20GB SSD storage

---

## 2. Linux Production Setup (Step-by-Step)

### 2.1 Install System Packages & MySQL
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv mysql-server nginx git libmysqlclient-dev
```

### 2.2 Configure MySQL Database
```sql
sudo mysql -u root -p
CREATE DATABASE campuspulse_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'campuspulse_user'@'localhost' IDENTIFIED BY 'StrongSecurePassword123!';
GRANT ALL PRIVILEGES ON campuspulse_db.* TO 'campuspulse_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2.3 Clone & Setup Virtual Environment
```bash
git clone https://github.com/your-repo/CampusPulse_AI.git /opt/campuspulse
cd /opt/campuspulse
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Configure Environment Variables (`.env`)
Create or edit `/opt/campuspulse/.env`:
```env
DEBUG=False
SECRET_KEY=generate-a-cryptographically-secure-50-character-secret-key
ALLOWED_HOSTS=campus.university.edu,192.168.1.100,localhost

# Dual-Database Engine Configuration
DB_ENGINE=mysql
DB_NAME=campuspulse_db
DB_USER=campuspulse_user
DB_PASSWORD=StrongSecurePassword123!
DB_HOST=127.0.0.1
DB_PORT=3306

# Weather Telemetry
OPEN_METEO_LATITUDE=13.0827
OPEN_METEO_LONGITUDE=80.2707
```

### 2.5 Run Migrations, Train ML Models & Seed
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py train_models
python manage.py seed_demo_data
python manage.py collectstatic --noinput
```

---

## 3. Web Server & Process Supervision

### 3.1 Systemd Service Unit (`/etc/systemd/system/campuspulse.service`)
```ini
[Unit]
Description=CampusPulse AI Gunicorn Daemon
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/campuspulse
ExecStart=/opt/campuspulse/venv/bin/gunicorn \
          --workers 4 \
          --bind 127.0.0.1:8000 \
          --access-logfile /var/log/campuspulse/access.log \
          --error-logfile /var/log/campuspulse/error.log \
          config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo mkdir -p /var/log/campuspulse
sudo chown -R www-data:www-data /var/log/campuspulse /opt/campuspulse
sudo systemctl daemon-reload
sudo systemctl enable --now campuspulse.service
```

### 3.2 Nginx Reverse Proxy Configuration (`/etc/nginx/sites-available/campuspulse`)
```nginx
server {
    listen 80;
    server_name campus.university.edu;

    client_max_body_size 25M;

    location /static/ {
        alias /opt/campuspulse/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /opt/campuspulse/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/campuspulse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 4. Windows Development & Demonstration Quickstart

For local evaluation or project presentations on Windows:
```powershell
cd c:\Users\Santhoskrishna\Documents\CampusPulse_AI
python manage.py runserver 127.0.0.1:8000
```
Open `http://127.0.0.1:8000` in your web browser. Use the header **Demo Role Switcher** to seamlessly navigate through all 12 roles without logging in and out.
