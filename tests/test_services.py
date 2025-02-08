from src.services import get_currency_rates, get_stock_prices


def test_get_currency_rates():
    rates = get_currency_rates()
    assert isinstance(rates, list)
    assert rates[0]["currency"] == "USD"


def test_get_stock_prices():
    stocks = get_stock_prices()
    assert isinstance(stocks, list)
    assert stocks[0]["stock"] == "AAPL"
