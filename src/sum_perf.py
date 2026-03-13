import numpy as np
import pandas as pd
from IPython.display import display

def sum_perf_report(price_df, return_df, time_col=None, risk_free_rate=0, caption="Risk ve Performans Analizi", show=True):
    
    if time_col and time_col in price_df.columns:
        p_df = price_df.set_index(time_col)
        r_df = return_df.set_index(time_col)
    else:
        p_df = price_df.copy()
        r_df = return_df.copy()

    stats = []
    
    for ticker in p_df.columns:
        prices = p_df[ticker].dropna()
        returns = r_df[ticker].dropna()
        
        if len(prices) < 2: 
            continue
            
        last_p = prices.iloc[-1]
        total_ret = (last_p / prices.iloc[0]) - 1
        daily_avg_ret = returns.mean()
        ann_return = daily_avg_ret * 252
        
        daily_vol = returns.std()
        ann_vol = daily_vol * np.sqrt(252)
        sharpe = (ann_return - risk_free_rate) / ann_vol if ann_vol != 0 else 0
        
        var_10 = returns.quantile(0.10)
        var_5 = returns.quantile(0.05)
        max_dd = ((prices / prices.cummax()) - 1).min()
        
        stats.append({
            'Ticker': ticker,
            'Son Fiyat': last_p,
            'Toplam Getiri (%)': total_ret * 100,
            'Günlük Ort. Getiri (%)': daily_avg_ret * 100,
            'Sharpe Oranı': sharpe,
            'Risk Değeri (Günlük %)': daily_vol * 100,
            'Yıllık Volatilite (%)': ann_vol * 100,
            'VaR (%10)': abs(var_10) * 100,
            'VaR (%5)': abs(var_5) * 100,
            'Maks. Düşüş (%)': max_dd * 100
        })
        
    df = pd.DataFrame(stats)
    df.index = df.index + 1
    
    if df.empty:
        return df
        
    max_ret = df['Toplam Getiri (%)'].abs().max()
    
    styled_summary = df.style \
        .format({
            'Son Fiyat': '{:,.2f}$', 'Toplam Getiri (%)': '{:+.2f}%', 
            'Günlük Ort. Getiri (%)': '{:+.3f}%', 'Sharpe Oranı': '{:.2f}',
            'Risk Değeri (Günlük %)': '{:.2f}%', 'Yıllık Volatilite (%)': '{:.2f}%',
            'VaR (%10)': '{:.2f}%', 'VaR (%5)': '{:.2f}%', 'Maks. Düşüş (%)': '{:.2f}%'
        }) \
        .background_gradient(subset=['Toplam Getiri (%)'], cmap='RdYlGn', vmin=-max_ret, vmax=max_ret) \
        .background_gradient(subset=['Sharpe Oranı'], cmap='YlGn', vmin=0, vmax=2) \
        .background_gradient(subset=['VaR (%10)'], cmap='Reds') \
        .background_gradient(subset=['VaR (%5)'], cmap='Reds') \
        .set_caption(caption)
        
    if show:
        display(styled_summary)
        return None 
    else:
        return styled_summary