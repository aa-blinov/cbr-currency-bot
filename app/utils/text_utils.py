def get_unit_word(nominal: int) -> str:
    """Get the correct form of the word "единица" based on the nominal value."""
    last_digit = nominal % 10
    last_two_digits = nominal % 100

    if last_digit == 1 and last_two_digits != 11:
        return "единицу"
    elif 2 <= last_digit <= 4 and (last_two_digits < 10 or last_two_digits >= 20):
        return "единицы"
    else:
        return "единиц"


def format_currency_message(currency_data: dict) -> str:
    """Format the currency data into a user-friendly message."""
    code = currency_data["code"]
    name = currency_data["name"]
    nominal = currency_data["nominal"]
    value = currency_data["value"]

    unit_word = get_unit_word(nominal)

    return (
        f"Курс {code} ({name})\n\n"
        f"→ за {nominal} {unit_word}: {value:.4f} RUB\n"
        f"→ за 1 {code}: {value / nominal:.4f} RUB\n"
        f"→ за 1 RUB: {nominal / value:.6f} {code}"
    )
