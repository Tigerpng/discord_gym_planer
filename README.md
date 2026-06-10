# discord_gym_planer
Simple Discord bot to help plan gym visits with friends.

## Set Bot Token:

Create `.env` file and add to it: `DISCORD_TOKEN='YOUR-TOKEN'`

## Run with docker

  `docker compose up --build`

## Required Libs

* `discord.py`
* `python-dotenv`


## Virtual Environment (venv)

### Linux / macOS
  `python3 -m venv gym-bot-env`

  `source gym-bot-env/bin/activate`

### Windows (CMD)
  `python -m venv gym-bot-env`

  `gym-bot-env\Scripts\activate`

## Install Dependencies

After activating the virtual environment:

  `pip install --upgrade pip`

  `pip install discord.py`

  `pip install python-dotenv`
