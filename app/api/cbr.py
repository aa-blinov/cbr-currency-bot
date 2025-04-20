import httpx
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Any
from loguru import logger

from app.config import settings


class CBRClient:
    """Class for interacting with the Central Bank of Russia (CBR) API."""

    def __init__(self, api_url: str = settings.cbr_api_url):
        """Initializes the CBRClient with the API URL."""
        self.api_url = api_url

    async def get_currency_rate(self, currency_code: str) -> Optional[Dict[str, Any]]:
        """Gets the currency rate from the CBR API."""
        try:
            logger.debug(f"Currency exchange rate request: {currency_code}")
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_url, timeout=10.0)

                if response.status_code != 200:
                    logger.error(f"Request error to CBR: {response.status_code}")
                    return None

                return self._parse_currency_data(response.text, currency_code.upper())

        except httpx.RequestError as exc:
            logger.error(f"Network request error: {exc}")
            return None
        except Exception as exc:
            logger.exception(f"Unexpected error while retrieving the exchange rate: {exc}")
            return None

    def _parse_currency_data(self, xml_data: str, currency_code: str) -> Optional[Dict[str, Any]]:
        """Parses the XML data from the CBR API and extracts currency information."""
        try:
            root = ET.fromstring(xml_data)

            for valute in root.findall("Valute"):
                char_code = valute.find("CharCode").text  # type: ignore

                if char_code == currency_code:
                    name = valute.find("Name").text  # type: ignore
                    nominal = int(valute.find("Nominal").text)  # type: ignore
                    value = float(valute.find("Value").text.replace(",", "."))  # type: ignore

                    logger.debug(f" Found a course for {currency_code}: {value} RUB for {nominal} unit.")

                    return {
                        "code": currency_code,
                        "name": name,
                        "nominal": nominal,
                        "value": value,
                    }

            logger.warning(f"Currency {currency_code} not found in CBR data")
            return None

        except ET.ParseError as exc:
            logger.error(f"XML parsing error: {exc}")
            return None
        except (AttributeError, ValueError) as exc:
            logger.error(f"Currency data processing error: {exc}")
            return None
