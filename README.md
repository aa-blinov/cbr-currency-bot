# Telegram Currency Bot for Central Bank of Russia (CBR)

A Telegram bot that provides up-to-date exchange rates from the Central Bank of Russia. The bot allows users to retrieve current currency rates relative to the Russian ruble through a convenient Telegram interface.

DEMO: @cbrfxbot
---

## Key Features

- Retrieves current exchange rates for major currencies (USD, EUR, CNY, KZT, KGS, BYN).
- Allows users to query the rate of any currency using its international code.
- Automatically recalculates currency-to-ruble ratios.
- Provides an intuitive quick-select keyboard in the Telegram interface.
- Detailed logging of bot operations.
- Statistics tracking: user count, daily activity, and request metrics.
- Whitelist support for statistics access control.

---

## Requirements

- Docker and Docker Compose (for containerized setup)
- Вot token from [@BotFather](https://t.me/botfather)

---

## Setup

### Environment Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/currency-bot.git
   cd currency-bot
   ```

2. Create the `.env` file based on the example:

   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and add your Telegram bot token:

   ```ini
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   LOG_LEVEL=INFO
   BASE_CURRENCIES=["USD", "EUR", "CNY", "KZT", "KGS", "BYN"]
   STATS_WHITELIST=123456789,987654321
   ```

   **Note:** `STATS_WHITELIST` is optional. If set, only users with IDs listed (comma-separated) can access the `/stats` command. If not set, all users can access statistics.

---

## Running with Docker

The project includes a `docker-compose.yml` configuration for running the bot and tests in Docker containers.

### Start the Bot

1. Build and start the bot container:

   ```bash
   docker-compose up -d currency-bot
   ```

2. View logs:

   ```bash
   docker-compose logs -f currency-bot
   ```

### Stop the Bot

To stop the bot container:

```bash
docker-compose down
```

---

## Testing

The `docker-compose.yml` file includes a dedicated service for running tests. Since the project currently has a limited number of tests, the test execution is temporarily handled within the main Dockerfile. As the test suite grows, the tests will be moved to a separate Dockerfile and service configuration.

### Run Tests in Docker

1. Execute the test container:

   ```bash
   docker-compose run --rm tests
   ```

This command will run all tests using `pytest` inside the Docker container.

---

## Statistics

The bot automatically tracks usage statistics:
- Total number of registered users
- Daily active users
- Daily request count
- New user registrations

Use the `/stats` command to view statistics. Access can be restricted using the `STATS_WHITELIST` environment variable.

## Logging

Logs are stored in the `logs/` directory and include information about bot operations, user requests, and potential errors. By default, log rotation is configured by file size (5 MB) with archives retained for up to 10 days.

Statistics are stored in `bot_stats.db` (SQLite database) in the project root directory.

---

## Troubleshooting

### API Access Problems

If the bot cannot retrieve currency rates:

- Verify the availability of the CBR server.
- Check the internet connection on the bot's server.
- Ensure the XML response is parsed correctly.
