# Architecture

How the CBR currency bot is put together.

## The shape

The bot is one package, `app/`, in five parts: the entry point that builds
the Telegram application, the handlers that answer, the client that reads
the CBR document, the counters, and the helper that formats a reply. Every
string the user sees is written in `app/bot/handlers.py`, except the rate
answer, which comes from `app/utils/text_utils.py`.

| Module | What it is responsible for |
| --- | --- |
| `app/__main__.py` | The entry point. Builds the application, registers three commands and one message handler, and runs the polling loop. |
| `app/__init__.py` | The two loguru sinks. Importing `app` removes the default sink and adds stderr and `logs/bot.log`. |
| `app/config.py` | The pydantic settings, the `.env` file, and the log directory, which is created at import time. |
| `app/bot/handlers.py` | The commands and the message handler. Every reply the user sees except the rate answer is written here. |
| `app/bot/keyboards.py` | The reply keyboard: two currencies per row and one full-width text button. |
| `app/api/cbr.py` | The HTTP call to cbr.ru and the XML parser. |
| `app/stats/service.py` | The SQLite counters, through `aiosqlite`. |
| `app/stats/models.py` | Two plain classes the service returns. |
| `app/utils/text_utils.py` | The rate message format and the Russian plural for "unit". |

Around the package sit the requirements: `requirements.txt` holds every
runtime and test dependency with its version pinned, `pytest.ini` and
`ruff.toml` hold the test and lint settings, and `docker-compose.yml`
defines the two services `currency-bot` and `tests`. The Dockerfile pins
`python:3.10.17-slim`.

## The data flow

```
Telegram update -> handler -> counters -> CBR XML -> parse -> format -> reply
```

A text message arrives at `handle_message`. The handler records the
activity in SQLite, then decides between three paths: the custom-code flag
in `context.user_data` is set, so the message is treated as a code; the
message carries the text of the custom-code button, so the flag is set and
the user is asked for a code; or the message carries a code that is on the
keyboard, so a rate is requested.

A rate request sends the waiting notice, calls `CBRClient.get_currency_rate`,
and formats the answer. The client opens an `httpx.AsyncClient`, gets
`https://www.cbr.ru/scripts/XML_daily.asp` with a timeout of 10 seconds,
and parses the reply with `xml.etree.ElementTree`. The parser walks the
`Valute` elements and stops at the one whose `CharCode` matches, taking its
`Name`, `Nominal` and `Value`. The value arrives with a comma as the
decimal separator and is read with the comma replaced by a dot.

The answer goes back to `format_currency_message`, which writes three
figures and sends them.

A second path runs in the other direction: `post_init` creates the two
tables in `bot_stats.db` and writes to the counters on every message. The
`/stats` command reads them back and formats them with HTML.

## Decisions worth knowing about

### The whole daily document is fetched for every question

`CBRClient.get_currency_rate` opens a new client, downloads the document
and parses it, once per question, with a timeout of 10 seconds and no
cache. The CBR publishes one document per day that carries every currency
it lists, so the same bytes travel for every user.

The cost is a request per question and a parse per question. The benefit is
that the answer cannot be older than the document the CBR published
today.

### The settings are built at import time

`app/config.py` ends with `settings = Settings()`, and `app/__init__.py`
imports it, so every entry into the package builds the settings. A missing
`TELEGRAM_TOKEN` therefore fails during the import rather than at startup:
`pytest` dies in collection with a pydantic `ValidationError`, and so does
`python -m app`. The log directory is created in the same place, so it has
to be writable.

### The custom-code flag lives in memory

`context.user_data[WAITING_FOR_CUSTOM_CODE]` is the only session the bot
keeps. It is per user, in memory, and it is gone when the process
restarts. A user who asks for a code and the bot restarts in between has to
ask again.

### The counters count messages, not lookups

`record_user_activity` runs on every text message, before the handler
decides what the message was. Opening the custom-code dialog and typing a
code that is not a currency both count as requests.

### The plural for "unit" is computed, not stored

`get_unit_word` picks between "единицу", "единицы" and "единиц" from the
last digit and the last two digits of the nominal, because Russian needs
all three. The CBR publishes a nominal of 1 for the dollar and 100 for the
yen, so the same sentence reads two ways.

### The statistics answer is the only formatted one

`/stats` is sent with `parse_mode="HTML"`, and the four labels are wrapped
in `<b>`. Every other reply is plain text with no parse mode, so Telegram
applies no markup to it. The refusal of a wrong code and the rate answer
carry their own structure in the text instead.

### The compose file and the image disagree about where the code lives

`docker-compose.yml` mounts `./logs:/app/logs` and
`./bot_stats.db:/app/bot_stats.db`, while the Dockerfile sets
`WORKDIR /workspace` and `PYTHONPATH=/workspace`, and the code writes the
database next to itself. The log file and the database therefore never
reach the host, and the counters die with the container. The two paths have
to be brought into line before the numbers can be trusted.

## Boundaries

- **`app/bot/handlers.py` owns the wording.** The strings the user sees
  live there, except the rate answer, which lives in
  `app/utils/text_utils.py` because it needs the plural helper. A new
  reply goes into one of those two files, and nowhere else.
- **`app/api/cbr.py` does not know about Telegram.** The client returns a
  dictionary with the code, the name, the nominal and the value, or
  `None`. It never formats a message and never imports a handler.
- **`app/utils/text_utils.py` does not know where the data came from.** It
  takes a dictionary and returns a string.
- **`app/stats/` does not talk to Telegram.** The service takes IDs, dates
  and counts, and it never reads an update.
- **`app/config.py` is imported by everything.** A new setting is a new
  field on `Settings`, and the module has to decide what happens when it
  is missing.
