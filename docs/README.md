# Documentation

The documents for the CBR currency bot. The bot is a Telegram client, a
parser for one XML document and a SQLite counter, so the documentation is
short and points at the three parts that matter.

| Document | What it covers |
| --- | --- |
| [architecture.md](architecture.md) | The handlers, the CBR client, the counters, and the flow from a Telegram update to a reply. |
| [screenshots/README.md](screenshots/README.md) | Why there are no images, and the exact text of every reply. |
| [../README.md](../README.md) | The front door: what it does and how to run it. |
| [../AGENTS.md](../AGENTS.md) | The commands, the paths, and the traps. |
| [../PRODUCT.md](../PRODUCT.md) | What the bot is for, and the rules about the interface language. |
| [../DESIGN.md](../DESIGN.md) | The wording, the markers, the keyboard and the two weights the bot asks for. |

## Reading order

New here: [../README.md](../README.md), then [architecture.md](architecture.md).

Changing the code: [architecture.md](architecture.md), then
[../AGENTS.md](../AGENTS.md) for the traps.

Changing what the bot says to the user: [../DESIGN.md](../DESIGN.md) first.
It holds the exact wording of every reply, and the rules about the
language and the markers.

## What is not here

There is no guide to running the bot in production. The README says how it
runs under Docker Compose and the `Dockerfile` holds the image. There is no
database guide either: the counters live in two SQLite tables that
`app/stats/service.py` creates on the first successful start.
