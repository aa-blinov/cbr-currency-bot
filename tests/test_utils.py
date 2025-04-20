from app.utils.text_utils import get_unit_word, format_currency_message


def test_get_unit_word():
    assert get_unit_word(1) == "единицу"
    assert get_unit_word(2) == "единицы"
    assert get_unit_word(3) == "единицы"
    assert get_unit_word(4) == "единицы"
    assert get_unit_word(5) == "единиц"
    assert get_unit_word(11) == "единиц"
    assert get_unit_word(21) == "единицу"
    assert get_unit_word(101) == "единицу"
    assert get_unit_word(111) == "единиц"


def test_format_currency_message():
    """Тест форматирования сообщения с курсом валюты."""
    currency_data = {
        "code": "USD",
        "name": "Доллар США",
        "nominal": 1,
        "value": 92.5678,
    }

    message = format_currency_message(currency_data)
    print(message)  # Для отладки

    assert "1 единицу: 92.5678 RUB" in message
    assert "1 USD: 92.5678 RUB" in message
    assert "1 RUB: 0.010803" in message
