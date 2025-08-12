# SOFI Discord Card Bot

!!!ONLY WINDOWS!!!
An automation bot for Discord card-collecting games involving SOFI and Nori bots.

## Features

-   Automatically detects when Nori pings you to drop cards
-   Sends the `sd` command automatically
-   Reads heart counts from Nori's response
-   Clicks the card with the highest heart count
-   Clicks event cards
-   Works with multi-monitor setups

## Prerequisites

### 1. Python Installation

-   Install Python 3.8 or higher from [python.org](https://python.org)
-   On Windows, use `py` command instead of `python`

### 2. Tesseract OCR Installation

winget install UB-Mannheim.TesseractOCR

## Installation

1. **Download the files:**

    - `sofi.py` - Main bot script
    - `requirements.txt` - Python dependencies
    - `images/button1.png`, `images/button2.png`, `images/button3.png` - Button templates
    - `README.md` - This file

2. **Navigate to sofi directory:**

    Open command prompt
    cd "your directory to sofi file"

2. **Create a virtual environment (NEEDED ON EVERY LAUNCH):**

    py -m venv venv

3. **Activate the virtual environment:**

    venv\Scripts\activate

4. **Install dependencies:**

    pip install -r requirements.txt

    **If you get build errors, try:**

    # Update pip first
    python -m pip install --upgrade pip

    # Install packages individually
    pip install pyautogui
    pip install Pillow
    pip install pytesseract
    pip install opencv-python
    pip install numpy

## Configuration

1. **Run the bot for the first time:**

    py sofi.py

2. **The bot will automatically create a default `sofi_config.json` file** with default delay settings

3. **Choose option 1 to run configuration** (required for first-time setup)

    - The bot will guide you through setting up coordinates
    - Click on the chat area when prompted
    - Click on the input area when prompted
    - Enter your Discord username

4. **Configuration is saved to `sofi_config.json`** with both delays and user settings

## Usage

1. **Make sure Discord is open and visible**
2. **Run the bot:**
    ```bash
    py sofi.py
    ```
3. **Choose option 1 to start automation**
4. **The bot will:**
    - Wait for Nori's ping
    - Send `sd` command automatically
    - Read heart counts from Nori's response
    - Click the best card
    - Repeat the cycle

## Stopping the Bot

Press `Ctrl+C` to stop the bot safely.

## File Structure

```
sofi-bot/
├── sofi.py              # Main bot script
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── images/             # Button template images
│   ├── button1.png     # Button 1 template
│   ├── button2.png     # Button 2 template
│   └── button3.png     # Button 3 template
├── sofi_config.json    # Configuration (created automatically with defaults)
└── venv/               # Virtual environment (created during setup)
```

## Notes

-   The bot works best with Discord in dark mode
-   Keep Discord window size consistent
-   Configuration is persistent between runs
