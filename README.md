# WfRp-Builder [[LIVE LINK]](https://zyv1k.eu.pythonanywhere.com/warhammer/)
Character creator for Warhammer Fantasy Roleplay[PL].
## Tech stack
Programming language: Python 3.7

Web Framework: Django 3.0.5

Database: SqLite3

API: Django REST framework 3.11.0

Front-end: bootstrap 4, JavaScript

## Features:
* Create, develop (according to the rules), edit (freely) and save characters for Warhammer Fantasy RPG (2nd ed.).
* Description of every stat, skill, ability etc.
* Global dice roller and map (everyone can see them and they refresh every few seconds)
* Dice roller is "connected" to character's stats - it displays if roll was successful or not
* Register and login users
* If logged in - display "owned" characters
* If logged in - claim existing character
* (If character was created without registration everyone in possession of it's URL can access and edit it's stats.)
* Compendium - lookup every skill, profession etc.
* Contact form

## Installation
1. Install [python](https://www.python.org/downloads/)
1. Navigate your console to folder containing *requirements.txt*
2. Install required packages - run: `pip install requirements.txt`
3. Migrate database - run: `python manage.py migrate`
4. Populate database - run: `python manage.py loaddata fixtures.json`
5. Start server - run: `python manage.py runserver`
6. Open [127.0.0.1:8000/warhammer/](127.0.0.1:8000/warhammer/) in your browser
7. If for some reason you want to deploy it (why?) - change variables in `wh_project/secrets.py`