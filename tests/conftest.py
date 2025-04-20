import pytest
import asyncio
from unittest.mock import MagicMock
from pathlib import Path
import xml.etree.ElementTree as ET


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def cbr_xml_data():
    test_data_path = Path(__file__).parent / "data" / "cbr_response.xml"

    if not test_data_path.exists():
        test_data_path.parent.mkdir(exist_ok=True)

        root = ET.Element("ValCurs")
        root.set("Date", "20.04.2025")

        valute_usd = ET.SubElement(root, "Valute")
        valute_usd.set("ID", "R01235")

        ET.SubElement(valute_usd, "NumCode").text = "840"
        ET.SubElement(valute_usd, "CharCode").text = "USD"
        ET.SubElement(valute_usd, "Nominal").text = "1"
        ET.SubElement(valute_usd, "Name").text = "Доллар США"
        ET.SubElement(valute_usd, "Value").text = "92,5678"

        valute_eur = ET.SubElement(root, "Valute")
        valute_eur.set("ID", "R01239")

        ET.SubElement(valute_eur, "NumCode").text = "978"
        ET.SubElement(valute_eur, "CharCode").text = "EUR"
        ET.SubElement(valute_eur, "Nominal").text = "1"
        ET.SubElement(valute_eur, "Name").text = "Евро"
        ET.SubElement(valute_eur, "Value").text = "99,8765"

        valute_jpy = ET.SubElement(root, "Valute")
        valute_jpy.set("ID", "R01820")

        ET.SubElement(valute_jpy, "NumCode").text = "392"
        ET.SubElement(valute_jpy, "CharCode").text = "JPY"
        ET.SubElement(valute_jpy, "Nominal").text = "100"
        ET.SubElement(valute_jpy, "Name").text = "Японских иен"
        ET.SubElement(valute_jpy, "Value").text = "61,1234"

        tree = ET.ElementTree(root)
        tree.write(test_data_path, encoding="utf-8", xml_declaration=True)

    with open(test_data_path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def mock_httpx_response(cbr_xml_data):
    response = MagicMock()
    response.status_code = 200
    response.text = cbr_xml_data
    return response


@pytest.fixture
def mock_httpx_client(mock_httpx_response):
    client = MagicMock()
    client.__aenter__.return_value = client
    client.get.return_value = mock_httpx_response
    return client
