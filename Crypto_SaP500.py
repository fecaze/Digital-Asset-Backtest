import backtrader as bt
import yfinance as yf
from datetime import datetime, timedelta

# Estratégia de rebalanceamento trimestral
class RebalanceStrategy(bt.Strategy):
    params = (
        ('rebalance_days', 90),  # Rebalanceamento a cada 90 dias
        ('allocations', {'BTC-USD': 0.50, 'ETH-USD': 0.30, 'USDT-USD': 0.20}),  # Pesos iniciais
    )
    
    def __init__(self):
        self.next_rebalance = None  # Próxima data de rebalanceamento

    def start(self):
        # Definir a próxima data de rebalanceamento como o primeiro dia de negociação
        self.next_rebalance = self.datas[0].datetime.date(0) + timedelta(days=self.params.rebalance_days)
        self.rebalance_portfolio()  # Fazer o primeiro rebalanceamento no início

    def next(self):
        # Rebalancear a cada 90 dias
        if self.data.datetime.date(0) >= self.next_rebalance:
            self.rebalance_portfolio()
            self.next_rebalance = self.data.datetime.date(0) + timedelta(days=self.params.rebalance_days)

    def rebalance_portfolio(self):
        total_value = self.broker.getvalue()  # Valor total do portfólio

        for data in self.datas:
            ticker = data._name
            allocation = self.params.allocations.get(ticker, 0)

            # Calcular o valor a ser alocado para cada ativo
            target_value = total_value * allocation
            current_value = self.broker.getvalue(datas=[data])
            price = data.close[0]

            if price > 0:  # Evitar divisão por zero
                target_size = target_value // price
                current_size = self.getposition(data).size

                # Se o tamanho atual for diferente do tamanho alvo, ajustar
                if current_size != target_size:
                    # Se temos mais do que o necessário, vendemos o excedente
                    if current_size > target_size:
                        self.sell(data=data, size=current_size - target_size)
                    # Se temos menos, compramos a diferença
                    elif current_size < target_size:
                        self.buy(data=data, size=target_size - current_size)

# Função para obter dados históricos do Yahoo Finance
def get_data(ticker, start='2024-01-01', end='2024-09-01'):
    data = yf.download(ticker, start=start, end=end)
    return bt.feeds.PandasData(dataname=data)

# Configuração do Backtest
if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # Adicionar a estratégia ao backtest
    cerebro.addstrategy(RebalanceStrategy)

    # Definir período do backtest
    start_date = '2024-01-01'
    end_date = '2024-09-01'

    # Adicionar dados de BTC, ETH e USDT
    assets = ['BTC-USD', 'ETH-USD', 'USDT-USD']
    for asset in assets:
        data = get_data(asset, start=start_date, end=end_date)
        cerebro.adddata(data, name=asset)  # Nomear o ativo com o ticker

    # Adicionar dados do S&P 500 para benchmark
    sp500_data = get_data('^GSPC', start=start_date, end=end_date)
    cerebro.adddata(sp500_data, name='S&P 500')  # Nomear o benchmark

    # Configurações de capital inicial
    cerebro.broker.setcash(10000)  # Capital inicial de $10,000
    cerebro.broker.setcommission(commission=0.001)  # Comissão de 0.1% por trade

    # Executar o backtest
    print("Valor inicial: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("Valor final: %.2f" % cerebro.broker.getvalue())

    # Gráfico de performance
    cerebro.plot()
