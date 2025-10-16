# 🧁Bakery Billing Management System
A complete **Django-based billing management system** built for bakeries to efficiently manage customers, products, and invoices.  
It automatically generates bills with **GST**, maintains records with **date && id**, and integrates with **MySQL** for data storage.

## Installation & Setup
1️⃣ **Clone the Repository**
```bash
git clone https://github.com/shaandhal13-ux/bakery-billing-django.git
cd bakery-billing-django
```

2️⃣ **Create Virtual Environment**
```bash
python -m venv (foldername)
venv\Scripts\activate     # For Windows
source venv/bin/activate  # For Mac/Linux
```

3️⃣ **Install Required Dependencies**
```bash
pip install -r requirements.txt
```

4️⃣ **Configure Your MySQL Database**
```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_mysql_username',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

5️⃣ **Configure Your Email**
```bash
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your_gmail"       
EMAIL_HOST_PASSWORD = "your_gmail_app_password"   
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```
**⚠️ Note: open gmail > go to manage your Google Acoount > enable 2 step verification > search app password> enter app name(any) > click create > 16 digits numbers will get created paste it under email_host_password**

6️⃣ **Apply Database Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7️⃣ **Run the Development Server**
```bash
python manage.py runserver
```
**⚠️ Note: Make sure you’re inside the folder that contains manage.py before running the server.**

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| **Frontend** | HTML, CSS, Bootstrap, JavaScript |
| **Backend** | Django (Python) |
| **Database** | MySQL |
| **Other Tools** | MySQL Workbench, xhtml2pdf, SMTP |

## 📄LICENSE
This project is licensed under the MIT License — you are free to use, modify, and distribute it with proper credit.
