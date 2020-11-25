# Purpose
* A lightweight Giphy application to allow users to save, favorite, and categorize gifs after registering with and logging into the application


# Requirements
* Python 3.6+
* postgresql


# Coding Standards
* Black
```
{
    "black_line_length": 79,
}
```
* Flake8


# Install & Setup
* It is assumed you have Python3 & pip3 already installed and configured

## Install Necessary Packages
```
sudo apt install postgresql
pip3 install requirements.txt
```

## Register with Giphy
* Goto https://developers.giphy.com/dashboard/?create=true and register
* Click "Create an App"
* Provide an App Name & Description
* Check "I only want to use the GIPHY API"
* Copy your new API Key to `api_key.txt` (Or a file of your choice, just update `config.yaml`)


## Setup Application
* Create postgres user and setup DB
```
sudo passwd postgres
su - postgres
psql
\password postgres

CREATE DATABASE giphy_manager;
CREATE USER giphy_manager;
GRANT ALL PRIVILEGES ON DATABASE giphy_manager TO giphy_manager;
\password giphy_manager
```
* Configure Flask
```
export FLASK_ENV=dev
export FLASK_APP=run.py
```
* Run Flask
```
python3 -m flask run
```

## Troubleshooting
1. If `psycopg2` fails to install due to `libpq-fe.h` error, run the following:
    `sudo apt install libpq-dev python3-dev`

# Usage
* From any browser, go to http://127.0.0.1:5000/register to create the first user
* Enter a username, password, and confirmation password
* Or go to http://127.0.0.1:5000/login to log into an existing user
* Once logged in, you should be redirected to http://127.0.0.1:5000/search
* Search for any gifs through this UI, save/favorite any gifs you find interesting
* Go to http://127.0.0.1:5000/view to view your saved/favorited gifs, add categories to any of the gifs you would like
* Go to http://127.0.0.1:5000/categories to add/change/remove categories you would like to use in the future


# Possibilities
* Use nginx to handle Auth and Static File severing for requests
* Use ReactJS for cleaner UI and modern Javascript design
