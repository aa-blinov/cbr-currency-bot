# Screenshots

The repository holds no images, and there is nothing here to show.

The bot's interface is a Telegram chat. Every reply is a bubble drawn by
the Telegram client on the reader's device, and the client picks the
colours, the fonts and the layout. A screenshot of the bot would be a
screenshot of Telegram, with a bot in it.

## The text of every reply

What a picture would have shown is written down here instead. These are
the ten replies the bot can send, in the order a reader meets them.

**The greeting**, from `/start`:

```
Привет, {username}! Я помогу вам узнать курс ЦБ РФ на сегодня.

Выберите валюту из списка или нажмите 'Ввести свой код' для проверки своей валюты (потребуется ввести трехбуквенный код, например, AED).
```

**The help**, from `/help`:

```
🔹 Выберите валюту из кнопок для получения курса.
🔹 Нажмите 'Ввести свой код' для проверки любой валюты по коду.
🔹 Используйте команду /start для перезапуска бота.
🔹 Данные предоставлены Центральным Банком России.
```

**The request for a code**, after the reader pressed "Ввести свой код":

```
Введите международный код валюты (например, USD, EUR, GBP):
```

**The notice that the keyboard holds only the usual currencies**, sent when
a message is neither a code on the keyboard nor a code that was asked for:

```
Пожалуйста, выберите валюту из кнопок или нажмите 'Ввести свой код'.
```

**The waiting notice**, sent before the request to the CBR:

```
⏳ Получаю данные...
```

**The rate**, from `app/utils/text_utils.py`:

```
Курс USD (Доллар США)

→ за 1 единицу: 92.5678 RUB
→ за 1 USD: 92.5678 RUB
→ за 1 RUB: 0.010803 USD
```

**The refusal of a code the CBR does not publish:**

```
❌ Не удалось получить курс валюты AED.
Проверьте правильность кода валюты или попробуйте позже.
```

**The refusal of a code that is not three letters:**

```
❌ Некорректный формат кода валюты. Пожалуйста, введите трехбуквенный код (например, USD).
```

**The statistics**, from `/stats`, and the only reply sent with
`parse_mode="HTML"`:

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

**The two refusals of the statistics command**, one for a reader who is
not on the whitelist and one for a failure while reading the counters:

```
❌ У вас нет доступа к этой команде.
```

```
❌ Ошибка при получении статистики. Попробуйте позже.
```

The wording, the markers and the weights these replies use are described
in [../../DESIGN.md](../../DESIGN.md).
