def get_currency_symbol(currency):
    """Возвращает символ валюты"""
    symbols = {"usd": "$", "gbp": "£"}
    return symbols.get(currency, currency + " ")
