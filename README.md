![](__screenshots/bookmark_web.png)


# Introduction

This is a simple bookmark manager for the web. It keeps your favorites books, articles, songs or whatever else you come across while browsing and allows you to search them.

The project is written with django 4.1 and Python 3.9.

### Features
* Simple and intuitive interface
* Bootstrap 4 (static files included)
* Procfile for deployment
* SQLite database by default
* Search by title, description, links and tags
* Separate settings for development and production(environment variables)
* Add, edit and delete bookmarks, tags and categories
* Custom admin interface, with search and filters ( view, edit, delete all bookmarks, tags and categories)

### Roadmap

* Backup and restore bookmarks
* Export bookmarks for browsers
* Browser extension (Chrome, Firefox, Safari)

### Installation

- Create a virtual environment and activate it

```bash
python3 -m venv bohca-venv
source bohca-venv/bin/activate
```

- Clone the repository

```bash
git clone https://github.com/mofm/bohca.git
```

- Install the requirements

```bash
pip install -r requirements.txt
```

- Create environment files
    
```bash
mkdir .env
touch .env/development.env
touch .env/production.env
```

- Add the following variables to 'development.env' file

For production environment, use environment variables from 'production.env' file

```bash
DEBUG=True
SECRET_KEY=your_secret_key
ALLOWED_HOSTS= "127.0.0.1, localhost"
```

- Run the migrations

```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

- Create a superuser

```bash
python manage.py createsuperuser
```

- Collect static files

```bash
python manage.py collectstatic
```

- You can test out the application by running the following command:

```bash
python manage.py runserver 0.0.0.0:8000
```

- Open your browser and go to http://localhost:8000

### Deployment

- Install gunicorn

```bash
pip install gunicorn
```

- Create gunicorn systemd service files for production environment

```bash
sudo vi  /etc/systemd/system/gunicorn.service
```

- Add the following content to the 'gunicorn.service' file

```bash
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
Type=notify
User=user
Group=user
EnvironmentFile=/path/to/bohca_venv/bohca/.env/production.env
WorkingDirectory=/path/to/bohca_venv/bohca
ExecStart=/path/to/bohca_venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 bohca.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

- Start the gunicorn service

```bash
sudo systemctl start gunicorn
```

- Enable the gunicorn service

```bash
sudo systemctl enable gunicorn
```

- Check the status of the gunicorn service

```bash
sudo systemctl status gunicorn
```

- Create nginx configuration file for production environment

```bash
sudo vi /etc/nginx/sites-available/bohca
```

- Add the following content to the bohca file

```bash
server {
    listen 80;
    server_name your_domain_name;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /path/to/bohca_venv/bohca/staticfiles;
    }

    location / {
        include proxy_params;
        # proxy_pass gunicorn_socket or http://;
    }
}
```

- Enable the bohca configuration file

```bash
sudo ln -s /etc/nginx/sites-available/bohca /etc/nginx/sites-enabled
```

- Test the nginx configuration file

```bash
sudo nginx -t
```

- Restart the nginx service

```bash
sudo systemctl restart nginx
```

- Check the status of the nginx service

```bash
sudo systemctl status nginx
```

### License
GNU General Public License v3.0
