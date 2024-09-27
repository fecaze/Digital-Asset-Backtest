import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Baixar os dados da ação
dados = yf.download('AAPL', start='2020-01-01', end='2023-01-01')

print(dados)

# 2. Calcular médias móveis de 50 e 200 dias
dados['SMA_50'] = dados['Close'].rolling(window=50).mean()
dados['SMA_200'] = dados['Close'].rolling(window=200).mean()

# 3. Criar sinais de compra/venda
dados['Sinal'] = 0
dados['Sinal'][50:] = np.where(dados['SMA_50'][50:] > dados['SMA_200'][50:], 1, 0)
dados['Posição'] = dados['Sinal'].diff()

# 4. Calcular retornos
dados['Retorno'] = dados['Close'].pct_change()
dados['Retorno_Estrategia'] = dados['Retorno'] * dados['Posição'].shift(1)

# 5. Retorno acumulado
dados['Retorno_Cumulativo'] = (1 + dados['Retorno_Estrategia']).cumprod()

# Plotar o desempenho
plt.figure(figsize=(10,5))
plt.plot(dados['Retorno_Cumulativo'], label='Retorno da Estratégia')
plt.title('Backtest da Estratégia de Médias Móveis')
plt.legend()
plt.show()

# Retorno final
print(f"Retorno final: {dados['Retorno_Cumulativo'][-1]}")