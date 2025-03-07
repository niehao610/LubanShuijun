# YouTube Automation Bot

This project implements a YouTube automation bot that can perform various actions on YouTube using a headless browser.

## Features

- Automated YouTube login
- Video playback automation
- Automatic video liking
- Automated comment posting
- Headless browser operation

## Requirements

- Python 3.8+
- Chrome browser installed
- Required Python packages (see requirements.txt)

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your credentials:
```
YOUTUBE_EMAIL=your_email@example.com
YOUTUBE_PASSWORD=your_password
COMMENT_API_URL=your_comment_api_url
```

3. Run the bot:
```bash
python youtube_bot.py
```

## Configuration

You can configure the following parameters in the `.env` file:
- YouTube login credentials
- Comment API URL
- Video URL

## Note

Please use this bot responsibly and in accordance with YouTube's terms of service. 