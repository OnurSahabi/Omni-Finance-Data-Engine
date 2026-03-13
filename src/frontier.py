import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

def p_frontier(data, step=0.01, plot=False):
    """
    Markowitz Etkin Sınırını (Efficient Frontier) hesaplar.
    
    Parametreler:
    - data: Getiri serilerini içeren pandas DataFrame veya numpy array.
    - step: Hedef getiriler arasındaki adım büyüklüğünü belirler (Varsayılan: 0.01).
    - plot: True ise Etkin Sınır grafiğini ekrana çizer (Varsayılan: False).
    """
    
    # 1. Veri Hazırlığı
    # Eksik verileri (NA) kaldır ve matrise (numpy dizisine) çevir
    if isinstance(data, pd.DataFrame):
        df = data.dropna()
        R = df.values
    else:
        # Eğer zaten numpy dizisi ise NaN (boş) değer içeren satırları filtrele
        R = data[~np.isnan(data).any(axis=1)]
        
    # Sütun bazında ortalama getiriler
    mu = np.mean(R, axis=0)
    
    # Kovaryans matrisi ve simetrik olduğundan emin olma işlemi
    S = np.cov(R, rowvar=False)
    S = (S + S.T) / 2.0
    
    n = len(mu)
    
    # Optimizasyon için yardımcı fonksiyon: Portföy Varyansı
    # Amacımız bu değeri en aza indirmek.
    def portfolio_variance(w, cov_matrix):
        return np.dot(w.T, np.dot(cov_matrix, w))
    
    # Ağırlıkların 0'dan büyük olma koşulu (Açığa satış - short selling yasak)
    bounds = tuple((0.0, None) for _ in range(n))
    
    # Optimizasyon için başlangıç tahmini (eşit ağırlıklı dağılım)
    init_guess = np.repeat(1/n, n)
    
    # --- Adım 2: GMV (Global Minimum Variance - Küresel Minimum Varyans) Portföyü ---
    # Kısıt: Ağırlıkların toplamı 1'e eşit olmalı.
    gmv_constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
    
    # Varyansı minimize ediyoruz
    gmv_result = minimize(
        portfolio_variance, 
        init_guess, 
        args=(S,), 
        method='SLSQP', 
        bounds=bounds, 
        constraints=gmv_constraints
    )
    
    w_gmv = gmv_result.x
    ret_gmv = np.sum(w_gmv * mu) # En düşük riskli portföyün getirisi
    ret_max = np.max(mu)         # Tek bir varlıktan elde edilebilecek maksimum getiri
    
    # Hedef getirileri (targets) oluştur (R'daki seq ve length.out mantığı)
    num_steps = int(round(1 / step))
    targets = np.linspace(ret_gmv, ret_max, num_steps)
    
    frontier_risk = []
    frontier_return = []
    
    # --- Adım 3: Etkin Sınır (Efficient Frontier) Döngüsü ---
    for r in targets:
        # Kısıtlar: 
        # 1. Ağırlıkların toplamı 1 olmalı
        # 2. Portföy getirisi, hedef getiriye (r) eşit olmalı
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
            {'type': 'eq', 'fun': lambda x: np.sum(x * mu) - r}
        )
        
        opt_res = minimize(
            portfolio_variance, 
            init_guess, 
            args=(S,), 
            method='SLSQP', 
            bounds=bounds, 
            constraints=constraints
        )
        
        w = opt_res.x
        
        # Optimize edilmiş ağırlıklarla risk (standart sapma) ve getiriyi hesapla
        port_ret = np.sum(w * mu)
        port_risk = np.sqrt(np.dot(w.T, np.dot(S, w)))
        
        frontier_risk.append(port_risk)
        frontier_return.append(port_ret)
        
    result = {
        'Risk': np.array(frontier_risk),
        'Return': np.array(frontier_return)
    }
    
    # --- Adım 4: Görselleştirme (Plot) İşlemi ---
    if plot:
        plt.figure(figsize=(8, 5))
        plt.plot(result['Risk'], result['Return'], '-', linewidth=2, color='darkblue')
        plt.xlabel(r'Risk ($\sigma$)')
        plt.ylabel(r'Expected Return ($\mu$)')
        plt.title('Markowitz Efficient Frontier')
        plt.grid(True)
        # Sadece eksenleri/grafiği daha iyi göstermek için daraltma işlemleri yapılabilir
        plt.tight_layout()
        plt.show()
        
    return result