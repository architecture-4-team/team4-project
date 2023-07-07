# User Namagement Server
## Getting Started
1. Download source
2. Set virtual environment
3. Setup database - [Database Schema](https://github.com/architecture-4-team/team4-project/wiki/Database-Schme)
4. Test APIs - [REST API Document](https://github.com/architecture-4-team/team4-project/wiki/REST-API-Document)
   - It is recommended to use Postman. 
```python
# setup virtual env
# Windows OS, use Pycharm interpreter settings (root/venv)
pyenv virtualenv 3.10.x venv

pip install -r requirements.txt
```
## Start server
```bash
# http & local only
$ python manage.py runserver

# http & external interface
$ python manage.py runserver 0.0.0.0:8000

# https & external interface
$ python manage.py runsslserver --certificate django.crt --key django.key 0.0.0.0:8000
```