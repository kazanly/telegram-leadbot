# Lead Capture Telegram Bot

A simple Telegram bot that collects name, phone number, and a short message from users.  
It sends the data to a Google Sheet and notifies you in Telegram.

## ✨ Features

- Collects leads via FSM
- Sends data to Google Sheets
- Sends notification to admin in Telegram

## 🔧 Setup

1. Clone the repo and install dependencies  
2. Get `creds.json` from Google Cloud and place it in the root folder  
3. Set up your sheet with columns: Name | Phone | Message | Timestamp  
4. Set your bot token and admin ID in `main.py` / `utils.py`

## 🟢 Start

```bash
python main.py
```
