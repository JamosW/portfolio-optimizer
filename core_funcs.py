
from yahooquery.base import _YahooFinance as yf
import numpy as np
import pandas as pd
from itertools import combinations
from pytickersymbols import PyTickerSymbols
import matplotlib.pyplot as plt
from yahooquery import Ticker

def get_dfs(in_symbols, in_interval, in_start, in_end):
    dfs = Ticker(in_symbols, asynchronous = True).history(interval=in_interval, start = in_start, end = in_end)
        
    #the lowest date we can go due to difference in stocks ipo
    #lower_bound = max([i for i in dfs.reset_index().groupby("symbol")["date"].min()])
    
    return dfs

def extra_params():
    config = yf._CONFIG["chart"]
    intervals = config["query"]["interval"]["options"]
    
    extras = {"intervals": intervals}
    return extras

def stock_returns(df) -> [pd.Series]:
    df_list = []
    for df in [df.loc[[i]] for i in np.unique(df.index.get_level_values(0))]:
        close = np.array(df.close)
        #get returns in percentage
        ret = (np.diff(close) / close[:-1]) * 100
        df_list.append(ret)
    return df_list

#reads stock returns and extracts some statistical values
def get_params(rets):
    means = [i.mean() for i in rets]
    errors_list = [(ret - mean) for mean,ret in zip(means, rets)]
    squared_errors = [errors**2 for errors in errors_list]
    variances = [sum(sq_error)/len(sq_error) for mean,sq_error in zip(means, squared_errors)]
    #might not need this
    standard_dev = np.sqrt(variances)

    return {"variances": variances, "std_dev": standard_dev, "mean": means, 
    "sq_errors": squared_errors, "errors" : errors_list}

#calculate some random weights
def random_weights(samples, limit):
    randos = np.random.rand(samples, limit)
    #normalized
    randos = ((randos.T/np.sum(randos, axis = 1)).T)
    
    return randos

def calc_weights_cov(lst):
        weights,cov = lst
    
        weight_prod = np.prod(weights, axis = 1) 
        val = 2 * weight_prod * cov
    
        return val

#main plot
def portfolios_plot(portfolio_stdv, expected_ret):
    #switch plotting back end
    plt.switch_backend('agg')
    
    #plot
    x = portfolio_stdv
    y = expected_ret

    # plot
    fig, ax = plt.subplots()

    ax.scatter(x, y, s = 1)

    ax.set(xticks=np.arange(min(portfolio_stdv), max(portfolio_stdv)),
       yticks=np.arange(min(expected_ret), max(expected_ret)))

    return fig
    
    
def portfolios(limit, params, df, samples):
    
    param = [param[:limit] for param in params.values()]
    
    means = param[2]
   
    #weights
    weights = random_weights(samples, limit)
    
    #variance
    var = np.array(param[0])

    #covariance matrix
    covar = np.cov(df, ddof = 0)

    #covariance unique
    cov = np.unique(covar[np.where(~np.eye(covar.shape[0], dtype = bool))])

    weight_combos = list(map(lambda x: list(combinations(x, 2)), weights))

    #pair covariance and weights for the portfolio variance calculation
    connects = [[i, cov] for i in weight_combos]

    #right side of portfolio variance forumula
    p2 = np.sum(list(map(calc_weights_cov , connects)), axis = 1)

    #expected return
    e_r = np.sum(weights * means, axis = 1)
    
    #portfolio variance, may not be correct
    pv = np.sum(weights**2 * var, axis = 1) + p2 
    #* (cor * np.prod(std)))

    #pv = np.sum(weights**2 * var, axis = 1) + 2 * [list(combinations(i, r = 2)) for i in randos]
    p_stdv = np.sqrt(pv)

    #modified sharpe ratio
    s_r = e_r / p_stdv
    return p_stdv, e_r

def get_symbols():
    
    stock_data = PyTickerSymbols()
    s_and_p = stock_data.get_all_stocks()
    symbols = [i["symbol"] for i in s_and_p if i["symbol"] is not None]
    symbols.sort()
    return symbols