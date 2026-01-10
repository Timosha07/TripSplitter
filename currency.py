import yfinance as yf

def get_exchange_rate(currency_code):
    """
    Получает курс валюты к KZT через Yahoo Finance.
    Например: USD -> вернет 485.0
    """
    code = currency_code.upper().strip()
    
    # Если валюта уже тенге, курс 1 к 1
    if code in ["KZT", "ТГ", "ТЕНГЕ"]:
        return 1.0
    
    # Формируем тикер для Yahoo. 
    # Обычно формат такой: "USDKZT=X", "EURKZT=X", "RUBKZT=X"
    ticker_symbol = f"{code}KZT=X"
    
    try:
        # Запрашиваем данные
        ticker = yf.Ticker(ticker_symbol)
        # Берем данные за последний 1 день
        data = ticker.history(period="1d")
        
        if data.empty:
            return None
            
        # Возвращаем цену закрытия (Close)
        return float(data['Close'].iloc[-1])
        
    except Exception as e:
        print(f"Ошибка получения курса для {code}: {e}")
        return None