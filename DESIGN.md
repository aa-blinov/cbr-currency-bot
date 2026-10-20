---
name: cbr-currency-bot
description: The interface is Telegram's chat window. The repository owns the wording, the markers and the keyboard; Telegram owns the fonts and the colours.
colors:
  # No palette of its own. Telegram's client paints every pixel.
  primary: null
  neutral-bg: null
typography:
  body:
    # No family of its own. The client picks it, from the user's device.
    fontFamily: null
    fontSize: null
    fontWeight: 400
    lineHeight: null
  title:
    fontFamily: null
    fontSize: null
    fontWeight: 700
    lineHeight: null
    letterSpacing: null
rounded:
  # No radius of its own. Telegram draws the buttons.
  md: null
spacing:
  # No spacing scale of its own. Telegram lays the bubbles out.
  sm: null
  md: null
---

# The design record of cbr-currency-bot

The bot has no screen of its own. It writes into a Telegram chat, and
everything the reader sees is a message in a bubble drawn by the Telegram
client on the reader's device.

That leaves the repository with a small but real design surface: the
wording of every reply, the marker glyph at the start of a line, the arrow
that prefixes a rate, the bold labels in the statistics answer, and the
shape of the reply keyboard. The frontmatter above records the two weights
the repository asks for and nothing else, because those are the only
typographic decisions the code makes.

## Overview

**Creative North Star: "the rate slip"**

The Central Bank of Russia publishes one document a day, a long sheet with
every currency it lists on it. The bot takes one line from that sheet and
puts it in a chat. The design problem is small and the metaphor is the one
the product already uses: a slip of paper from a counter, printed once a
day, with a number on it and the unit spelled out next to the number.

A slip is short. It has a fixed shape. It carries no decoration beyond the
mark that tells you what kind of line you are reading. The bot's answers
follow that: a title line, a blank line, three lines of figures, each
prefixed with the same arrow.

The confirmed rejections are recorded here, because the code shows each of
them being made:

- No greeting once the bot is known. `/start` greets; the keyboard answers
  afterwards.
- No table. A table in a chat window is a table nobody can scroll on a
  phone, and the answer carries one currency at a time.
- No colour, no red for a fall and no green for a rise. The bot publishes
  one rate for the day and has no second figure to compare it with.
- No date on the answer. The CBR publishes one document per day, and a
  reader who asks in the evening means the same document as a reader who
  asks in the morning.

Key characteristics: one reply per question, three figures in a fixed
order, a marker glyph on every line that carries a status, and Russian
throughout.

## Colors

The repository names no colour. Telegram's client chooses the bubble
background, the text colour, the link colour and the keyboard colour from
the user's theme, and no theme setting reaches the bot.

### Primary

- **Telegram's own palette** (`null`): not a token of this project. There
  is no hex value in the code, no CSS and no theme file. Every colour a
  reader sees belongs to the client.

### Neutral

- **No surface of its own** (`null`): the bot paints nothing. There is no
  background behind the text and no rule between the lines.

### Named rules

**The marker rule.** A reply that reports a status starts its line with a
glyph, and a reply that reports a figure does not. The waiting notice, the
two refusals and the statistics answer all carry one; the rate answer
carries an arrow instead, because an arrow is a label and a marker is a
signal.

## Typography

**Display Font:** none of its own. **Body Font:** none of its own.

The Telegram client picks the family, the size and the line height, from
the platform the reader is on. The repository asks for two weights and
nothing more:

| Level | Weight | Where it appears |
| --- | --- | --- |
| Body | 400 | Every reply except the statistics answer. |
| Heading | 700 | The four labels in the `/stats` answer, each wrapped in `<b>`. |

Only one message asks for formatting. The statistics answer is sent with
`parse_mode="HTML"`, and every other reply is sent as plain text, so
Telegram applies no markup to it at all. The rate answer needs no
formatting because its structure carries the meaning: the arrow, the
number, and the unit in the same order every time.

The capitalisation follows the language. The interface is Russian, and
Russian sentences capitalise the first word and nothing else.

## Layout

The keyboard is two currencies per row, in the order `BASE_CURRENCIES`
gives, with the last row holding a single button that spans the width:

```
USD   EUR
CNY   KZT
KGS   BYN
Ввести свой код
```

The keyboard is built with `resize_keyboard=True`, so it shrinks to the
labels rather than filling the screen.

The rate answer is a block of five lines: a title, a blank line, and three
figures. The blank line is what separates the name of the currency from
the numbers, and it is the only vertical space the interface uses.

```
Курс USD (Доллар США)

→ за 1 единицу: 92.5678 RUB
→ за 1 USD: 92.5678 RUB
→ за 1 RUB: 0.010803 USD
```

Every other reply is one paragraph or one list, and none of them has a
blank line in it.

## Components

### The reply keyboard

- **Shape:** a grid, two buttons per row, plus one full-width row at the
  bottom.
- **Content:** the codes in `BASE_CURRENCIES`, then the text button
  "Ввести свой код".
- **Behaviour:** the keyboard stays under the chat until the user leaves
  the bot. It is rebuilt on every `/start`, from the current setting.

### The rate answer

- **Shape:** one title line, one blank line, three figure lines.
- **Title:** `Курс {code} ({name})`, with the name in the Russian the CBR
  publishes.
- **Figures:** the rate for the published nominal, the rate for one unit,
  and the rate for one ruble. Four decimals for the first two, six for the
  third.
- **Prefix:** every figure line starts with the arrow character.
- **Unit:** the word for "unit" is chosen for the nominal, so a nominal of
  1 reads "1 единицу" and a nominal of 100 reads "100 единиц".

### The waiting notice

```
⏳ Получаю данные...
```

One line, sent before the request to the CBR is made. It is the only
message in the bot that is sent while work is in progress.

### The refusals

Two of them, and they name what went wrong:

```
❌ Не удалось получить курс валюты USD.
Проверьте правильность кода валюты или попробуйте позже.
```

```
❌ Некорректный формат кода валюты. Пожалуйста, введите трехбуквенный код (например, USD).
```

The second one gives the format and an example, because the user typed
something the bot cannot use.

### The statistics answer

The one message with formatting. Four bold labels, two blocks, and a bullet
for each figure:

```
📊 <b>Статистика бота</b>

👥 <b>Всего пользователей:</b> 12

📅 <b>Сегодня (21.10.2026):</b>
   • Активных: 3
   • Запросов: 9
   • Новых: 1

📈 <b>За последние 7 дней:</b>
   • Активных: 14
   • Запросов: 41
   • Новых: 5
```

The bullet is a plain dot character followed by three spaces, not a list
markup. The date is written in the day, month and year order with dots
between the parts, the way the locale writes it.

### The log line

The bot writes to stderr and to `logs/bot.log` through two loguru sinks,
both with the same format:

```
2026-10-21 09:14:02 | INFO     | app.bot.handlers:get_currency_rate:141 - Пользователь 42 запросил курс валюты: USD
```

The level is padded to eight characters, and the module, the function and
the line number sit between it and the message.

## Do's and Don'ts

### Do:

- **Do** keep the three figures in the same order. The nominal, then the
  unit, then the ruble. A reader who has seen one answer knows the second
  line without reading it.
- **Do** keep the four decimals and the six decimals. Four for a ruble
  price, six for a foreign-currency price, because the second number is
  smaller and loses more.
- **Do** name the failure. Every refusal says which currency or which
  format was wrong.
- **Do** send the waiting notice before the request, not after. The CBR
  document is fetched per question and the wait is visible.
- **Do** keep the interface Russian, including the currency names, which
  arrive from the CBR in Russian.

### Don't:

- **Don't** add a second currency to a reply. One question, one currency,
  one block of three figures.
- **Don't** add a colour, a trend arrow or a percentage. The bot has one
  figure per direction and no history to compare it with.
- **Don't** send a message with `parse_mode="HTML"` unless it is the
  statistics answer. A stray tag in a rate line reaches the user as text.
- **Don't** change the number of decimals in one place only. The two
  precisions belong together.
- **Don't** put the marker glyph on a figure line. The arrow is the prefix
  for a figure, and a marker is for a status.
