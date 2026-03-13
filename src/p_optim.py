import numpy as np
import pandas as pd
from scipy.optimize import minimize
from qpsolvers import solve_qp


def p_optim(data, rf=0, digits=4):

    
    if not isinstance(data, (pd.DataFrame, np.ndarray)):
        raise ValueError("Veri DataFrame veya Matrix olmalı.")

    returns = data.values if isinstance(data, pd.DataFrame) else data
    assets = data.columns if isinstance(data, pd.DataFrame) else [f"Asset{i + 1}" for i in range(returns.shape[1])]

    mu = np.mean(returns, axis=0)
    sigma = np.cov(returns, rowvar=False)

    sigma = (sigma + sigma.T) / 2
    sigma += np.eye(len(mu)) * 1e-10

    n = len(mu)

    def get_port_stats(w):
        p_ret = np.sum(w * mu)
        p_risk = np.sqrt(np.dot(w.T, np.dot(sigma, w)))
        p_sharpe = p_ret / p_risk if p_risk != 0 else 0
        return p_ret, p_risk, p_sharpe


    def sharpe_obj(w):
        _, p_risk, p_ret = get_port_stats(w)
        return - (p_ret / p_risk) 

    
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    bounds = tuple((0, 1) for _ in range(n))

    res_sharpe = minimize(sharpe_obj, x0=np.ones(n) / n,
                          method='SLSQP', bounds=bounds, constraints=cons)
    w_sharpe = res_sharpe.x


    P = 2 * sigma
    q = np.zeros(n)

    
    A = np.ones((1, n))
    b = np.array([1.0])

    G = np.vstack([
        -mu, 
        -np.eye(n) 
    ])
    h = np.hstack([
        -rf, 
        np.zeros(n)  
    ])

   
    w_var = solve_qp(P, q, G, h, A, b, solver="quadprog")

    stats_list = []
    for name, w in [("Max Sharpe", w_sharpe), ("Min Risk", w_var)]:
        ret, risk, shrp = get_port_stats(w)
        stats_list.append({
            "Type": name,
            "Sharpe": round(shrp, 6),
            "Return": round(ret, 6),
            "Risk": round(risk, 6)
        })

    weights_df = pd.DataFrame(
        [w_sharpe, w_var],
        index=["Max_Sharpe", "Min_Risk"],
        columns=assets
    ).round(digits)

    return {
        "stats": pd.DataFrame(stats_list),
        "weights": weights_df
    }