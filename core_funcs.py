
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt
from yahooquery import Ticker




def min_date_dfs(symbols, start, end):
    
    dfs = Ticker(symbols= symbols, asynchronous = True).history(interval="1mo", start = start, end = end)
        
    lower_bound = max([i for i in dfs.reset_index().groupby("symbol")["date"].min()])
    
    filtered_dfs = dfs[dfs.index.get_level_values(1) >= lower_bound]
    
    return lower_bound, filtered_dfs
    
    
def stock_returns(df):
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
    variances = [sum(sq_error)/len(sq_error) for sq_error in squared_errors]
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

    #covariance unique without diaganol values (variances)
    cov = np.unique(covar[np.where(~np.eye(covar.shape[0], dtype = bool))])

    weight_combos = list(map(lambda x: list(combinations(x, 2)), weights))

    #pair covariance and weights for the portfolio variance calculation
    connects = [[i, cov] for i in weight_combos]

    #right side of portfolio variance forumula
    p2 = np.sum(list(map(calc_weights_cov , connects)), axis = 1)

    #expected return
    e_r = np.sum(weights * means, axis = 1)
    
    #portfolio variance
    pv = np.sum(weights**2 * var, axis = 1) + p2 
    #* (cor * np.prod(std)))

    #pv = np.sum(weights**2 * var, axis = 1) + 2 * [list(combinations(i, r = 2)) for i in randos]
    p_stdv = np.sqrt(pv)

    #modified sharpe ratios
    s_rs = e_r / p_stdv
    
    #indexed optimal values and minimum variance
    optimals= np.where(s_rs == np.max(s_rs))
    min_variance_ind = np.where(p_stdv == np.min(p_stdv))
   
    #max sharpe ratio
    s_r = s_rs[optimals]
    
    #minimum variance gained from the index
    min_variance = p_stdv[min_variance_ind]
    
    #max sharpe ratio weights and min variance weight
    sharpe_weights, min_variance_weights = [weights[i] for i in [optimals, min_variance_ind]]
    
    return p_stdv, e_r, s_r, sharpe_weights, min_variance_weights, min_variance


def get_tickers():
    
    return(['A','AAL','AAP','AAPL','ABBV','ABC','ABT','ACA','ACGL','ACN','ADBE','ADI'
,'ADM','ADP','ADSK','ADTN','AEE','AEP','AES','AFL','AGOAF','AGS','AHT'
,'AIG','AIR','AIZ','AJG','AKAM','ALB','ALC','ALGN','ALK','ALL','ALLE'
,'ALRS','ALV','AMAT','AMCR','AMD','AME','AMGN','AMP','AMS','AMT','AMZN'
,'ANET','ANSS','AOF','AON','AOS','APA','APAM','APD','APH','APTV','ARE'
,'ARGX','ASM','ASML','ATO','ATVI','AVB','AVGO','AVY','AWK','AXP','AZN'
,'AZO','BA','BAC','BAX','BB','BBVA','BBWI','BBY','BDX','BEN','BF-B','BIDU'
,'BIIB','BIO','BK','BKNG','BKR','BKT','BLK','BME','BMY','BN','BOIVF'
,'BOSS','BR','BRK-B','BRO','BSL','BSX','BWA','BXP','C','CAG','CAH','CARM'
,'CAT','CB','CBOE','CBRE','CCI','CCL','CDAY','CDNS','CDW','CE','CF','CFG'
,'CFR','CGGYY','CGUSY','CHD','CHRW','CHTR','CI','CINF','CL','CLX','CMA'
,'CMCSA','CME','CMG','CMI','CMS','CNA','CNC','CNP','COF','COO','COP'
,'COST','CPB','CPG','CPRT','CPT','CRH','CRL','CRM','CRWD','CSCO','CSGP'
,'CSX','CTAS','CTLT','CTRA','CTSH','CTVA','CVS','CVX','CZR','D','DAL'
,'DDOG','DE','DFS','DG','DGX','DHI','DHR','DIS','DISH','DLR','DLTR','DOCU'
,'DOV','DOW','DPZ','DRI','DSM','DTE','DUK','DVA','DVN','DXC','DXCM','EA'
,'EBAY','ECL','ED','EDV','EFX','EIX','EL','ELV','EMN','EMR','ENG','ENPH'
,'ENR','EOG','EPAM','EQIX','EQR','EQT','ERMAY','ES','ESS','ETN','ETR'
,'ETSY','EUTLF','EVRG','EVT','EW','EXC','EXPD','EXPE','EXR','EZM','F'
,'FANG','FAST','FCX','FDS','FDX','FE','FFIV','FIS','FITB','FIVE','FLT'
,'FMC','FOXA','FRA','FRES','FRT','FTK','FTNT','FTV','GBF','GD','GE','GEN'
,'GILD','GIS','GL','GLPG','GLW','GM','GNRC','GOOGL','GPC','GPN','GRF'
,'GRMN','GRUPF','GS','GSEFF','GSK','GWW','HAL','HAS','HBAN','HCA','HD'
,'HEI','HES','HIG','HII','HLT','HOLX','HON','HPE','HPQ','HRL','HSIC','HST'
,'HSY','HUM','HWM','IAG','IBM','ICE','IDR','IDXX','IEX','IFF','IHG','III'
,'ILMN','INCY','INTC','INTU','INVH','IP','IPG','IQV','IR','IRM','ISP'
,'ISRG','IT','ITP','ITW','IVZ','JBHT','JCDXF','JCI','JD','JKHY','JNJ'
,'JNPR','JPM','K','KDP','KEY','KEYS','KHC','KIM','KLAC','KMB','KMI','KMX'
,'KO','KR','L','LAND','LDOS','LEG','LEN','LH','LHX','LIN','LKQ','LLY'
,'LMT','LNC','LNT','LOGN','LOW','LRCX','LULU','LUMN','LUV','LVS','LW'
,'LYB','LYV','MA','MAA','MAR','MAS','MBG','MC','MCD','MCHP','MCK','MCO'
,'MDLZ','MDT','MEIYF','MELI','MET','META','MGM','MGNT','MHK','MKC','MKTX'
,'MLM','MMC','MMM','MNST','MO','MOH','MOR','MOS','MPC','MPWR','MRK','MRNA'
,'MRO','MRVL','MS','MSCI','MSFT','MSI','MT','MTB','MTCH','MTD','MTX','MU'
,'NCLH','NDAQ','NDSN','NEE','NEM','NFLX','NI','NKE','NOC','NOVN','NOW'
,'NPACY','NRG','NSC','NTAP','NTES','NTRS','NUE','NVDA','NVR','NWL','NWSA'
,'NXPI','NXPRF','O','ODFL','OKE','OKTA','OMC','ON','OR','ORA','ORCL'
,'ORLY','OXY','PANW','PARA','PAYC','PAYX','PCAR','PCG','PDD','PEAK','PEG'
,'PEP','PFE','PFG','PG','PGR','PH','PHM','PKG','PLD','PM','PNC','PNR'
,'PNW','POOL','PPG','PPL','PRU','PSA','PSH','PSN','PSX','PTC','PWR','PXD'
,'PYPL','QCOM','QRVO','RAND','RBSFY','RCL','RE','REG','REGN','RF','RHI'
,'RIO','RJF','RL','RMD','ROG','ROK','ROL','ROP','ROST','RS','RSG','RTO'
,'SAN','SAP','SBAC','SBNY','SBS','SBUX','SCHW','SEDG','SEE','SGEN','SHW'
,'SIRI','SJM','SLB','SLOIF','SMIN','SNA','SNPS','SO','SPG','SPGI','SPLK'
,'SRE','STLA','STM','STT','STX','STZ','SU','SVT','SWK','SWKS','SYF','SYK'
,'SYY','T','TAP','TCS','TDG','TDY','TEAM','TECH','TEF','TEL','TER','TFC'
,'TFX','TGT','TJX','TMO','TMUS','TPR','TRGP','TRMB','TROW','TRV','TSCO'
,'TSLA','TSN','TT','TTWO','TXN','TXT','TYL','UAL','UDR','UHS','ULTA','UNH'
,'UNP','UPS','URI','USB','UTG','V','VFC','VICI','VIV','VLO','VMC','VNO'
,'VOD','VRBCF','VRSK','VRSN','VRTX','VTR','VTRS','VZ','WAB','WAT','WBA'
,'WBD','WDAY','WDC','WEC','WELL','WFC','WHR','WM','WMB','WMT','WNDLF'
,'WPP','WRB','WRK','WST','WY','WYNN','XEL','XOM','XRAY','XYL','YUM','ZBH'
,'ZBRA','ZION','ZM','ZS','ZTS'])
