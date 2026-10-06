import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

def run_technical_analysis(ticker, start_date, end_date, output_dir):
    print(f"[{datetime.now()}] Morgan Stanley テクニカル分析開始: {ticker}")
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    try:
        df = pd.DataFrame({
            'Open': data['Open'][ticker],
            'High': data['High'][ticker],
            'Low': data['Low'][ticker],
            'Close': data['Close'][ticker],
            'Volume': data['Volume'][ticker]
        })
    except KeyError:
        df = pd.DataFrame({
            'Open': data['Open'], 'High': data['High'], 'Low': data['Low'],
            'Close': data['Close'], 'Volume': data['Volume']
        })
        
    df = df.dropna()

    # 移動平均線 (20, 50, 200)
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()

    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))

    # ボリンジャーバンド (20, 2σ)
    df['Std_20'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['SMA_20'] + (df['Std_20'] * 2)
    df['BB_Lower'] = df['SMA_20'] - (df['Std_20'] * 2)

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    clean_ticker = ticker.replace('.', '_')
    csv_filename = os.path.join(output_dir, f"{timestamp}_{clean_ticker}_MS_Technical_Indicators.csv")
    
    df.to_csv(csv_filename, encoding='utf-8-sig')
    print(f"[{datetime.now()}] 分析完了。データ出力先: {csv_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python ms_technical_indicators.py <ticker> <start_date> <end_date> <output_dir>")
        sys.exit(1)
    run_technical_analysis(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
