import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime

# Estratégia de Cruzamento de Médias Móveis e RSI
class CryptoStrategy(bt.Strategy):
    params = (
        ('short_period', 10),   # Média Móvel Curta
        ('long_period', 30),    # Média Móvel Longa
        ('rsi_period', 14),     # Período do RSI
        ('rsi_buy', 30),        # Nível de RSI para compra
        ('rsi_sell', 70),       # Nível de RSI para venda
    )

    def __init__(self):
        # Definindo indicadores
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data.close, period=self.params.rsi_period)
        
        self.order = None  # Para armazenar ordens abertas

    def next(self):
        if self.order:
            return  # Ignorar enquanto houver ordens abertas

        # Sinal de Compra: SMA curta > SMA longa e RSI < 30 (sobrevenda)
        if not self.position:  # Se não há posição aberta
            if self.sma_short > self.sma_long and self.rsi < self.params.rsi_buy:
                self.order = self.buy()  # Comprar

        # Sinal de Venda: SMA curta < SMA longa e RSI > 70 (sobrecompra)
        elif self.sma_short < self.sma_long and self.rsi > self.params.rsi_sell:
            self.order = self.sell()  # Vender

# Função para obter dados históricos do Yahoo Finance (BTC/USD)
def get_data(ticker='BTC-USD', start='2021-01-01', end='2023-01-01'):
    data = yf.download(ticker, start=start, end=end)
    return bt.feeds.PandasData(dataname=data)

# Configurar Backtest
if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # Adicionar a estratégia ao backtest
    cerebro.addstrategy(CryptoStrategy)

    # Adicionar dados (BTC/USD)
    data = get_data()
    cerebro.adddata(data)

    # Configurações de capital inicial
    cerebro.broker.setcash(10000)  # Capital inicial
    cerebro.broker.setcommission(commission=0.001)  # Comissão de 0.1% por trade

    # Executar o backtest
    print("Valor inicial: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("Valor final: %.2f" % cerebro.broker.getvalue())

    # Gráfico de performance
    cerebro.plot()