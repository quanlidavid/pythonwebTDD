from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

REPO_URL = 'https://github.com/quanlidavid/pythonwebTDD.git'


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        run(f'mkdir -p {site_folder}/{subfolder}')


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run(f'cd {source_folder} && git fetch')
    else:
        run(f'git clone {REPO_URL} {source_folder}')
    current_commit = local('git log -n 1 --format=%H', capture=True)
    run(f'cd {source_folder} && git reset --hard {current_commit}')


def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/pythonwebTDD/settings.py'
    sed(settings_path, 'DEBUG = True', 'DEBUG = False')
    sed(settings_path, 'ALLOWED_HOSTS = .+$', f'ALLOWED_HOSTS = ["{site_name}","111.229.126.162"]')
    secret_key_file = source_folder + '/pythonwebTDD/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, f'SECRET_KEY = {key}')
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run(f'python3 -m venv {virtualenv_folder}')
    run(f'{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt')


def _update_static_files(source_folder):
    run(f'cd {source_folder} && ../virtualenv/bin/python manage.py collectstatic --noinput')


def _update_database(source_folder):
    run(f'cd {source_folder} && ../virtualenv/bin/python manage.py migrate --noinput')

def _install_apps():
    run('sudo apt-get update')
    run('sudo apt-get install nginx')
    run('sudo apt-get install python3-venv')
    run('sudo apt-get install git')

def _nginx_and_gunicorn_config(source_folder):
    run(f'sed "s/SITENAME/{env.host}/g" {source_folder}/deploy_tools/nginx.template.conf | sudo tee /etc/nginx/sites-available/{env.host}')
    run(f'sudo ln -s /etc/nginx/sites-available/{env.host} /etc/nginx/sites-enabled/{env.host}')
    run(f'sed "s/SITENAME/{env.host}/g" {source_folder}/deploy_tools/gunicorn-systemd.template.service | sudo tee /etc/systemd/system/gunicorn-{env.host}.service')
    run('sudo rm /etc/nginx/sites-enabled/default')
    run('sudo systemctl daemon-reload')
    run('sudo systemctl start nginx')
    run('sudo systemctl reload nginx')
    run('sudo systemctl enable gunicorn-{env.host}')
    run('sudo systemctl start gunicorn-{env.host}')


def deploy():
    _install_apps()
    site_folder = f'/home/{env.user}/sites/{env.host}'
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)
    _nginx_and_gunicorn_config(source_folder)
