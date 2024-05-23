# XTREAM API

# What is this application for? 

This application is needed to work as an xtream server API.
You put a link to an IPTV playlist in M3U or M3U8 format and an EPG link into the configuration file and the application processes it all and sends it as json responses to any xtream enabled application.

# Why not use an off-the-shelf solution?

All the xtream server control panels I've found were last updated over 2 years ago. They also have many problems and cannot be fixed due to encrypted files.

This guide will show you how to get the application up and running. 

## Requirements 
Before you begin, make sure you have python3 installed.

## Step 1: Download and install the dependencies

```
git clone https://github.com/Divarion-D/xtream_api.git
cd xtream_api
pip3 install -r requirements.txt
```

## Step 2: Configure the application

Open config.py and fill in the fields

## Step 3: Run the application

```
python3 main.py
```

## Step 4: Create an administrator account

Enter your username and password in the console when you run the application for the first time.