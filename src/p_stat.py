import numpy as np
import pandas as pd
from IPython.display import display

def p_stats(data_var, data_index, var_cols=None, index_col=None, weights=None, tau=0.05, rf=0.0, show=True, caption=None):
   
    if isinstance(data_var, pd.DataFrame) and var_cols is not None:
        df_assets = data_var[var_cols] if isinstance(var_cols, list) else data_var.iloc[:, var_cols]
    else:
        df_assets = pd.DataFrame(data_var)
        
    if isinstance(data_index, pd.DataFrame) and index_col is not None:
        s_index = data_index[index_col] if isinstance(index_col, str) else data_index.iloc[:, index_col]
    else:
        s_index = data_index.iloc[:, 0] if isinstance(data_index, pd.DataFrame) else pd.Series(data_index)

    def calc_beta(assets, mkt):
        return assets.apply(lambda col: col.cov(mkt) / mkt.var())

    # 1. Hesaplamalar
    beta = calc_beta(df_assets, s_index)
    q_low, q_high = s_index.quantile(tau), s_index.quantile(1 - tau)

    beta_low = calc_beta(df_assets[s_index <= q_low], s_index[s_index <= q_low])
    beta_high = calc_beta(df_assets[s_index >= q_high], s_index[s_index >= q_high])
    beta_mid = calc_beta(df_assets[(s_index > q_low) & (s_index < q_high)], s_index[(s_index > q_low) & (s_index < q_high)])

    # --- BAŞLIKLARI BURADA DÜZENLİYORUZ ---
    name_beta = "Beta"
    name_mid  = f"Beta (Mid %{100*(1-2*tau):g})"
    name_low  = f"Beta (Low %{100*tau:g})"
    name_high = f"Beta (High %{100*tau:g})"
    name_treynor = "Treynor Ratio"
    name_var = f"VaR (%{100*tau:g})"

    row_names = [name_beta, name_mid, name_low, name_high]
    beta_df = pd.DataFrame([beta, beta_mid, beta_low, beta_high], index=row_names)

    beta_df.loc[name_treynor] = (df_assets.mean() - rf) / beta
    beta_df.loc[name_var] = df_assets.quantile(tau).abs()

    if weights is not None:
        weights = np.array(weights)
        beta_p = beta_df.dot(weights)
        port_ret = df_assets.dot(weights)
        
        # Portföy metrikleri (doğrusal olmayanlar için yeniden hesaplama)
        beta_p[name_treynor] = (port_ret.mean() - rf) / np.sum(beta * weights)
        beta_p[name_var] = abs(port_ret.quantile(tau))
        beta_df["Portfolio"] = beta_p

    # 2. Düzenleme ve Sıralama
    result_df = beta_df.T.round(4)
    
    if "Portfolio" in result_df.index:
        other_tickers = sorted([idx for idx in result_df.index if idx != "Portfolio"])
        result_df = result_df.reindex(["Portfolio"] + other_tickers)
    
    # 3. Formatlama
    format_dict = {}
    for col in result_df.columns:
        if "beta" in col.lower(): format_dict[col] = "{:.2f}"
        elif "treynor" in col.lower(): format_dict[col] = "{:.4f}"
        elif "var" in col.lower(): format_dict[col] = "{:.2%}"
            
    styler = result_df.style.format(format_dict)
    if caption: styler = styler.set_caption(caption)
        
    styler = styler.set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#f4f4f4'), ('color', '#333333'), ('border', '1px solid #dddddd'), ('padding', '8px'), ('font-weight', 'bold')]},
        {'selector': 'td', 'props': [('border', '1px solid #dddddd'), ('padding', '8px'), ('text-align', 'right')]},
        {'selector': 'caption', 'props': [('font-size', '16px'), ('font-weight', 'bold'), ('margin-bottom', '10px')]}
    ])
    
    if show:
        display(styler)
        return None
    
    return styler