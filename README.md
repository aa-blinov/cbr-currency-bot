# cbr-currency-bot

A Telegram bot that answers with the exchange rate the Central Bank of Russia published today. The user taps a currency in the keyboard, or types any three-letter code, and the bot replies with the rate against the ruble: for the published nominal, for one unit, and for one ruble.

The interface is in Russian. The running instance is [@cbrfxbot](https://t.me/cbrfxbot).

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## Quick start

The bot needs a token from [@BotFather](https://t.me/botfather) and Python 3.10, the version the image pins (`python:3.10.17-slim`).

```bash
git clone https://github.com/aa-blinov/cbr-currency-bot.git
cd cbr-currency-bot
cp .env.example .env
```

Put the token in `.env`:

```ini
TELEGRAM_TOKEN=123456789:AAyourtokenhere
```

Then install and run:

```bash
pip install -r requirements.txt
python -m app
```

Docker runs the same code:

```bash
docker compose up -d currency-bot
docker compose logs -f currency-bot
```

| Command | What it does |
| --- | --- |
| `python -m app` | Runs the bot from a checkout. |
| `docker compose up -d currency-bot` | Builds the image and runs the bot. The service restarts itself. |
| `docker compose logs -f currency-bot` | Follows the bot's output. |
| `docker compose run --rm tests` | Runs the test suite in the same image. |
| `docker compose down` | Stops the bot and removes the containers. |

## What it does

- **Six currencies on the keyboard.** USD, EUR, CNY, KZT, KGS and BYN, two per row, and the set comes from `BASE_CURRENCIES`.
- **Any other currency by code.** The "Ввести свой код" button asks for a three-letter code and looks it up in the same daily document. A code that is not three letters is refused before a request is made.
- **Three numbers per answer.** The rate for the nominal the CBR publishes, the rate for one unit, and the rate for one ruble. Four decimals for the first two, six for the third.
- **A `/stats` command.** The total number of users, and for today and the last seven days the number of active users, the number of requests and the number of new users.
- **A whitelist for `/stats`.** With `STATS_WHITELIST` set, only the listed Telegram user IDs get an answer.
- **A local record of who writes to the bot.** Every user ID, username and first name that sends a message is kept in a SQLite file beside the bot.

## How it works

```
Telegram update -> handler -> counter -> CBR XML -> parse -> format -> reply
```

`app/__main__.py` builds the application with `python-telegram-bot` 22.0 and polls Telegram with `run_polling(allowed_updates=Update.ALL_TYPES)`. `/start`, `/help` and `/stats` are commands; every other text message goes to one handler.

`app/api/cbr.py` holds the client. Each request opens a new `httpx.AsyncClient`, gets `https://www.cbr.ru/scripts/XML_daily.asp` with a timeout of 10 seconds, and parses the reply with `xml.etree.ElementTree`. The CBR publishes one document per day that carries every currency it lists, and the parser takes the `Valute` element whose `CharCode` matches, together with its `Name`, `Nominal` and `Value`. The value arrives with a comma as the decimal separator.

`app/utils/text_utils.py` formats the answer and picks the Russian plural for "unit": one unit, two units, five units.

`app/stats/service.py` keeps the counters in SQLite through `aiosqlite`, in `bot_stats.db` in the repository root. The two tables are `users` and `daily_stats`.

## Configuration

| Variable | Default | What it does |
| --- | --- | --- |
| `TELEGRAM_TOKEN` | required | The token from BotFather. Without it the process stops during the import. |
| `BASE_CURRENCIES` | `["USD","EUR","CNY","KZT","KGS","BYN"]` | The currencies on the keyboard. A JSON array. |
| `LOG_LEVEL` | `INFO` | The level of both log sinks. |
| `LOG_DIR` | `logs/` in the repository root | Where `bot.log` is written. |
| `LOG_ROTATION` | `5 MB` | When the log file is rotated. |
| `CBR_API_URL` | `https://www.cbr.ru/scripts/XML_daily.asp` | The document the rates come from. |
| `STATS_WHITELIST` | none | The Telegram user IDs allowed to run `/stats`, comma-separated. Unset leaves the command open to every user. |

The values come from the environment and from a `.env` file in the repository root. `app/config.py` creates the log directory at import time, so that directory has to be writable.

## Development

```bash
pip install -r requirements.txt   # install
python -m app                     # run the bot
pytest                            # run the tests
ruff check .                      # lint
```

`pytest` needs the token, because `app/config.py` builds the settings at import time and the token is a required field:

```bash
TELEGRAM_TOKEN=123456789:AAyourtokenhere pytest
```

Two tests cover the plural helper and the message format. `ruff` is configured in `ruff.toml` (line length 120, rules E, F, W, B and C) and is not part of `requirements.txt`.

| Path | What it holds |
| --- | --- |
| `app/__main__.py` | The entry point: the application, the handlers, the polling loop. |
| `app/config.py` | The settings, the `.env` file, the log directory. |
| `app/bot/handlers.py` | The commands and the message handler. |
| `app/bot/keyboards.py` | The reply keyboard. |
| `app/api/cbr.py` | The HTTP client and the XML parser. |
| `app/stats/` | The SQLite service and its two models. |
| `app/utils/text_utils.py` | The message format and the Russian plural. |
| `tests/` | Two tests and the captured CBR document. |

## License

MIT, © Alexander Blinov. See [LICENSE](LICENSE).
