# XTREAM API

# What is this application for? 

This application is needed to work as an xtream server API.
You enter a link to an IPTV playlist in M3U or M3U8 format and an EPG link in the configuration file, and the application processes it all and sends it as json responses to any xtream-enabled application.

# Why not use an off-the-shelf solution?

All the xtream server control panels I've found were last updated over 2 years ago. They also have a lot of problems and can't be fixed because of encrypted files.

This manual provides instructions on how to get the application up and running. 

## Prerequisites 
Before you start, make sure you have python3 installed.

## Step 1: Download and install the dependencies

```
git clone https://github.com/Divarion-D/xtream_api.git
cd xtream_api
pip3 install -r requirements.txt
```

## Step 2: Configure the application

Open the config.py file and fill in the fields:

## Step 3: Run the app

```
python3 api.py
```

## Step 4: Create an administrator account

Enter your username and password in the console when you run the application for the first time