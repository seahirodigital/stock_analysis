import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

def run_quant_analysis(ticker, start_date, end_date, output_dir):
    print(f"[{datetime.now()}] RenTech Quant スクリーニング開始: {ticker}")
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    
    try:
        df = pd.DataFrame({'Close': data['Close'][ticker], 'Volume': data['Volume'][ticker]})
    except KeyError:
        df = pd.DataFrame({'Close': data['Close'], 'Volume': data['Volume']})
        
    df = df.dropna()

    # 移動平均線算出
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()

    # クオンツ・モメンタム指標: 移動平均乖離率（ファクターとしての歪み検知）
    df['Deviation_from_SMA20_Pct'] = ((df['Close'] - df['SMA_20']) / df['SMA_20']) * 100
    df['Deviation_from_SMA200_Pct'] = ((df['Close'] - df['SMA_200']) / df['SMA_200']) * 100
    
    # 出来高Zスコア（異常検知ファクター）
    df['Volume_Mean_20'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Std_20'] = df['Volume'].rolling(window=20).std()
    df['Volume_Z_Score'] = (df['Volume'] - df['Volume_Mean_20']) / df['Volume_Std_20']

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    clean_ticker = ticker.replace('.', '_')
    csv_filename = os.path.join(output_dir, f"{timestamp}_{clean_ticker}_RenTech_Quant_Factors.csv")
    
    df.to_csv(csv_filename, encoding='utf-8-sig')
    print(f"[{datetime.now()}] 分析完了。データ出力先: {csv_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python quant_momentum_factors.py <ticker> <start_date> <end_date> <output_dir>")
        sys.exit(1)
    run_quant_analysis(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
