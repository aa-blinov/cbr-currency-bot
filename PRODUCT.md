# Product

<!-- impeccable:product-schema 1 -->

## Platform

adaptive

The product is a Telegram bot. The interface is Telegram's own chat window, so it appears on whatever device the user opens Telegram on. The bot itself is a long-lived Python 3.10 process, deployed as a Docker container, that polls Telegram over HTTPS and reads the daily XML document from cbr.ru.

## Users

People who want the current rate of a currency against the ruble without opening a bank site or a finance app. The README names no audience beyond that, and the repository description on GitHub is empty, so nothing more specific is established.

The job: one rate, right now, in a chat window the user already has open. Three taps, or one typed code.

The second audience is the owner, who runs the bot and reads `/stats` to see how many people write to it.

The public instance is @cbrfxbot. The repository has 0 stars, 0 forks and 1 open issue, so there is no number to report about the people who use the bot.

## Product Purpose

The bot does one thing: it turns a currency code into the Central Bank of Russia rate for the day.

The CBR publishes one XML document per day with every currency it lists in it. The bot fetches that document when a user asks, finds the entry, and answers with three numbers: the rate for the nominal the CBR publishes, the rate for one unit, and the rate for one ruble. It does not correct the number, round it, or keep a history of it.

Success for the user: the rate is in the chat before they have thought about where to look for it. Success for the product: the bot answers from the CBR's own document, so the number is the number the bank publishes.

## Positioning

A bank site shows a table of every currency the bank lists and asks the reader to find theirs. This one shows six and asks for a code.

The part a neighbour cannot copy without doing the same work: the answer carries the inverse rate as well. The CBR publishes a ruble price for a nominal, and the bot divides it out to one unit and inverts it to one ruble, which is the number people who hold the currency are after.

The CBR publishes the data, and anyone can read the same XML document. The Telegram interface and the counters are the parts that belong to this repository.

## Operating Context

The user opens Telegram, sends `/start`, and gets the keyboard. It stays under the chat until they leave the bot. The bot holds no session: the "waiting for a custom code" flag lives in `context.user_data`, in memory, per user, and is lost when the process restarts.

The bot runs as a container on a server with `restart: always`. It holds the Telegram token, and it writes its own counters to a SQLite file next to the code. Nothing in the code throttles the outgoing messages.

The user's clock is not the bot's clock. The CBR publishes a daily document, so a rate asked for in the evening is the rate for that day, and the reply carries no date of its own.

## Capabilities and Constraints

Confirmed by the code:

- Six base currencies on the keyboard, two per row, set by `BASE_CURRENCIES`.
- Any three-letter code can be looked up in the CBR document. The code is checked before the request is made.
- The answer carries three numbers: the rate for the published nominal, the rate for one unit at four decimals, and the rate for one ruble at six decimals.
- The daily document is fetched per request over HTTP with a timeout of 10 seconds, and the value is read with a comma as the decimal separator.
- `/start`, `/help` and `/stats` are registered; every other text message goes to the message handler.
- The counters are the total number of users and, for a day, the active users, the requests and the new users. `/stats` shows today and the sum of the last seven days.
- `/stats` is limited to the Telegram user IDs in `STATS_WHITELIST` when it is set, and open to every user when it is not.
- The counters live in SQLite through `aiosqlite`, in two tables, `users` and `daily_stats`.
- The logs go to stderr and to `logs/bot.log`, rotated at 5 MB and kept for 10 days.
- The settings are read from the environment and from a `.env` file in the repository root.
- The token is required, and a rejected token stops the process at startup.

Deliberately not true, and worth knowing before a change:

- There is no cache. Every question downloads the daily document again.
- There is no history. The bot answers with the rate for the day and keeps nothing about the rates it has given.
- The counters count messages, not rate lookups.
- There is no admin interface beyond `/stats`, and no way to change the settings from inside Telegram.
- The repository carries no CI, no release process and no changelog.
- The token is the only secret, and it lives in the environment or in a `.env` file that the repository ignores.

## Brand Commitments

**Name:** cbr-currency-bot in the repository, @cbrfxbot for the running bot. **Voice:** Russian, short sentences, the rate first. Every answer is a number with its unit attached, and the unit is chosen for the number rather than fixed in the text.

The reply format is part of the promise: three lines, in the same order, with the same number of decimals. A user who has seen one answer knows what the other two lines mean.

The keyboard is the interface. Six currencies and one button, and nothing to type for the common case.

The replies carry markers of the interface's own. They are the product's decoration and stay in the reply strings.

## Evidence on Hand

- The README before this one named @cbrfxbot as the demo instance.
- The public page for @cbrfxbot is live and calls the bot "CBR RATES BOT", in Russian, and names the same popular currencies.
- `app/api/cbr.py` holds the endpoint, the timeout and the parser.
- `tests/data/cbr_response.xml` is a captured CBR document with USD, EUR and JPY in it.
- `tests/test_utils.py` covers the plural helper and the message format. Two tests in the repository.
- The GitHub API reports 0 stars, 0 forks, 1 open issue, the branch `master`, and no repository description.
- The GitHub API returns 404 for the licence endpoint: the repository had no licence of its own. The LICENSE file that now stands next to this document follows the house standard, and the owner's other repositories use the same terms.
- There is no screenshot, no recording and no transcript of a session in the repository.
- No number of users of @cbrfxbot is recorded anywhere. The counters live in a SQLite file that is not committed.

## Product Principles

1. **The CBR document is the single source.** The bot divides by the nominal and prints four and six decimals. It changes nothing else about the number.
2. **The keyboard is the interface.** Six currencies and one button. A rate is one tap, and the code path is for the currencies the keyboard does not carry.
3. **The interface stays Russian.** The users are Russian speakers, and the currency names the CBR publishes are Russian.
4. **The counters stay local.** The statistics live in a SQLite file beside the bot, and the only things that leave the machine are the rate request to the CBR and the answer to Telegram.
5. **A failure is a sentence in the chat.** A rate that cannot be fetched produces a refusal that names the currency, and a code that is not three letters produces a refusal that names the format.

## Accessibility & Inclusion

- **The keyboard is the main path.** Six buttons and one text button; nothing has to be typed for the common currencies.
- **The button label is a sentence.** "Ввести свой код" says what the button does.
- **A code is checked before anything else.** Three letters, and the refusal names the format and gives an example.
- **No standard has been set.** There is no work on contrast or screen readers in the repository, and no decision about what the bot owes a user who does not use the keyboard. Not decided.
