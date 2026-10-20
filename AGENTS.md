# AGENTS.md — agent context for `cbr-currency-bot`

A Telegram bot that answers with the Central Bank of Russia exchange rates. It polls Telegram, reads one XML document from cbr.ru per question, and keeps its counters in a SQLite file beside the code.

This file is what you need to work on the project without reading all of it.

## Run / build / test

```bash
pip install -r requirements.txt   # install
python -m app                     # run the bot
pytest                            # the tests, two of them
ruff check .                      # the lint
```

The token has to be in the environment or in a `.env` in the root, or the import fails:

```bash
TELEGRAM_TOKEN=123456789:AAyourtokenhere pytest
```

Docker:

```bash
docker compose up -d currency-bot    # build the image and run the bot
docker compose logs -f currency-bot  # follow the log
docker compose run --rm tests        # the tests in the same image
docker compose down                  # stop
```

Python 3.10 is the version the image pins (`python:3.10.17-slim`). There is no build step and no package manifest: `requirements.txt` is the whole dependency list, every version pinned, the two test packages included.

## Where things live

| Path | What it holds |
| --- | --- |
| `app/__init__.py` | The two loguru sinks. Importing `app` sets logging up, so every entry into the package writes to the log. |
| `app/__main__.py` | The entry point: the application builder, the four handlers, the polling loop. |
| `app/config.py` | The settings, the `.env` file, and the log directory, which is created at import time. |
| `app/bot/handlers.py` | The commands and the message handler. Every string the user sees is written here. |
| `app/bot/keyboards.py` | The reply keyboard: two currencies per row and the custom-code button. |
| `app/api/cbr.py` | The HTTP call and the XML parsing. |
| `app/stats/service.py` | The SQLite counters. |
| `app/stats/models.py` | The two plain classes the service returns. |
| `app/utils/text_utils.py` | The message format and the Russian plural for "unit". |
| `tests/` | Two tests, and the captured CBR document in `tests/data/`. |
| `Dockerfile`, `docker-compose.yml` | The image, and the two services `currency-bot` and `tests`. |

## Traps

- **The settings are built at import time.** `app/config.py` ends with `settings = Settings()` and `app/__init__.py` imports it, so a missing `TELEGRAM_TOKEN` fails during the import rather than at startup. `pytest` dies in collection with a pydantic `ValidationError`, and so does every other entry point. Export the variable or put a `.env` in the root first.
- **The compose mounts point at `/app`, and the image works in `/workspace`.** `docker-compose.yml` mounts `./logs:/app/logs` and `./bot_stats.db:/app/bot_stats.db`, but the Dockerfile sets `WORKDIR /workspace` and `PYTHONPATH=/workspace`, and the code writes next to itself. The log file and the database never reach the host, and the counters die with the container. Fix the two paths before you trust the numbers.
- **A `bot_stats.db` that does not exist becomes a directory.** Docker creates the path it is handed, so the first `docker compose up` in an empty checkout leaves a directory with that name in the working tree.
- **The database is created on the first successful start.** `StatsService.initialize()` runs in `post_init`, which python-telegram-bot calls from `run_polling` after the token has been accepted. A bot that dies with `InvalidToken` leaves no database behind.
- **The whole daily document is fetched for every rate.** `CBRClient.get_currency_rate` opens a new `httpx.AsyncClient`, downloads `XML_daily.asp` and parses it, once per question, with a timeout of 10 seconds and no cache. The CBR publishes one document per day that carries every currency it lists.
- **The timeout clause in `app/api/cbr.py` never runs.** `httpx.TimeoutException` is a subclass of `httpx.RequestError`, and the `RequestError` clause comes first, so a timeout is logged as a network error.
- **One malformed `Valute` element loses the whole document.** The parser reads `CharCode`, `Name`, `Nominal` and `Value` without checking that they exist, and the `AttributeError` clause returns `None` for the response instead of skipping the entry.
- **`BASE_CURRENCIES` only accepts a JSON array.** The field validator has a comma-separated branch, but pydantic-settings decodes a list field from the environment as JSON first and raises a `SettingsError` before the validator runs. `STATS_WHITELIST` is optional, and optional fields are the ones the library hands over as raw strings, so the comma-separated form works there.
- **The counters count messages, not lookups.** `record_user_activity` runs on every text message, so opening the custom-code dialog and typing a wrong code still counts as a request.
- **The interface is Russian and the code is mixed.** The strings the user sees are Russian, the currency names come from the CBR in Russian, and the docstrings and comments are in both languages. Keep the interface Russian and leave the surrounding code the way it is.

## Style / safety rails

- **No emoji in the repository's files.** The house style bans them and the checker fails the build. The bot's own replies carry them, because the interface uses them as markers, and that is the one exception.
- **Comments explain why, never what.**
- **Do not add a dependency without the reason next to it.** `requirements.txt` pins every version, the two test packages included.
- **Do not change the interface language.** The users are Russian speakers, and the CBR publishes the currency names in Russian.
- **Do not remove functionality that looks intentional; ask first.** The custom-code path, the whitelist and the counters are all deliberate.

## Where the product truth lives

`PRODUCT.md` holds it. Read it before changing the behaviour of the bot, and write the change there when the behaviour changes.
