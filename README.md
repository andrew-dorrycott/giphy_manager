# Purpose
* A lightweight Giphy application to allow users to save, favorite, and categorize gifs


# Requirements
* Python 3.6+
* postgresql
* ReactJS


# Standards
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
pip3 install requirements.txt
sudo apt install postgresql
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
* Execute SQL
```
< Convert this to SQLAlchemy DB creation instead of handwritten SQL >
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

# Usage
* From any browser, go to http://127.0.0.1:5000/


# Possibilities
* Use nginx to handle Auth and Static File severing for requests
