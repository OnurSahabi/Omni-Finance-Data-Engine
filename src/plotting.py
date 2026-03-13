import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_time_series_subplots(df, title, format_type='stock'):

    
    df_plot = df.copy()
    num_cols = len(df_plot.columns)
    
    
    height_multiplier = 3 if format_type == 'index' else 2.5
    fig, axes = plt.subplots(nrows=num_cols, ncols=1, figsize=(14, height_multiplier * num_cols), sharex=True)
    
    if num_cols == 1:
        axes = [axes]
    
    for i, column in enumerate(df_plot.columns):
        data = df_plot[column]
        valid_data = data.dropna()
        color_idx = f"C{i % 10}"
        
        if not valid_data.empty:
            first_date, first_price = valid_data.index[0], valid_data.iloc[0]
            last_date, last_price = valid_data.index[-1], valid_data.iloc[-1]
            
            
            y_min, y_max = data.min(), data.max()
            padding = (y_max - y_min) * 0.2 if y_max != y_min else (y_min * 0.1 if y_min != 0 else 0.1)
            
         
            lw = 2.5 if format_type == 'index' else 2.0
            axes[i].plot(df_plot.index, data, color=color_idx, linewidth=lw)
            axes[i].fill_between(df_plot.index, data, alpha=0.1, color=color_idx)
            axes[i].set_ylim(y_min - padding, y_max + padding)
            axes[i].margins(x=0.08)
            
           
            if format_type == 'index':
                first_label = f'{first_price:,.0f}'
                last_label = f'{last_price:,.0f}'
                scatter_size = 40
            else:
                first_label = f'{first_price:.3f}'
                last_label = f'{last_price:.3f}'
                scatter_size = 30

           
            axes[i].annotate(first_label, xy=(first_date, first_price), xytext=(-8, 0), 
                             textcoords='offset points', fontweight='bold', color='gray', fontsize=10, ha='right')
            
            axes[i].annotate(last_label, xy=(last_date, last_price), xytext=(8, 0), 
                             textcoords='offset points', fontweight='bold', color=color_idx, fontsize=11, ha='left')
            
            axes[i].scatter([first_date, last_date], [first_price, last_price], color=['gray', color_idx], s=scatter_size, zorder=5)
        
       
        axes[i].set_title(column, loc='left', fontsize=12, fontweight='bold', color='#333333')
        axes[i].grid(True, axis='y', alpha=0.3, linestyle='--')
        
        if format_type == 'index':
            axes[i].get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.suptitle(title, fontsize=16, fontweight='bold', y=0.98 if format_type == 'index' else 1.0) 
    plt.xlabel('Tarih', fontsize=12)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95] if format_type == 'index' else [0, 0, 1, 0.98]) 
    plt.show()







def plot_correlation_heatmap(df, title, time_col=None, figsize=(10, 8), annot=True, cmap='coolwarm'):
        
    if time_col and time_col in df.columns:
        df_calc = df.set_index(time_col)
    else:
        df_calc = df.copy()
            
    df_numeric = df_calc.select_dtypes(include=['float64', 'int64'])
    corr_matrix = df_numeric.corr()
       
    plt.figure(figsize=figsize)
    
   
    sns.heatmap(corr_matrix, annot=annot, cmap=cmap, fmt='.2f', 
                vmin=-1, vmax=1, linewidths=0.5, cbar_kws={"shrink": .8})
      
    plt.title(title, fontsize=14, fontweight='bold', color='#333333', pad=15)
    
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    
    plt.tight_layout()
    plt.show()






def plot_normalized_performance(df, title, time_col=None):
    
    
    if time_col and time_col in df.columns:
        df_plot = df.set_index(time_col)
    else:
        df_plot = df.copy()
        
   
    normalized_df = df_plot.copy()
    for column in normalized_df.columns:
        valid_data = normalized_df[column].dropna()
        if not valid_data.empty:
            first_valid_value = valid_data.iloc[0]
            normalized_df[column] = (normalized_df[column] / first_valid_value) * 100
    
    style_to_use = 'default'
    if 'seaborn-v0_8-whitegrid' in plt.style.available:
        style_to_use = 'seaborn-v0_8-whitegrid'
    elif 'seaborn-whitegrid' in plt.style.available:
        style_to_use = 'seaborn-whitegrid'
        
    with plt.style.context(style_to_use):
        plt.figure(figsize=(14, 8))
        
        for column in normalized_df.columns:
            if not normalized_df[column].dropna().empty:
                plt.plot(normalized_df.index, normalized_df[column], label=column, linewidth=2)
        
        plt.axhline(y=100, color='black', linestyle='--', alpha=0.6, label='Başlangıç (100)')
        
        plt.title(f"{title} - Görece Performans (Başlangıç=100)", fontsize=16, fontweight='bold', pad=20, color='#333333')
        plt.ylabel('Performans Katsayısı (100 Bazlı)', fontsize=12)
        plt.xlabel('Tarih', fontsize=12)
        
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()