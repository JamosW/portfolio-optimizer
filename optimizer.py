
import numpy as np
import pandas as pd
import yahooquery as yq
from itertools import permutations


#source - Kolari and Pynnonen
#returns simulated
#r1 = [7, 13, 8, 16, 17]
#r2 = [7, 8, 5, 3, 10]
r1 = [1.1, 1.7, 2.1, 1.4, 0.2]
r2 = [3, 4.2, 4.9, 4.1, 2.5]
#get the means
mean_r1, mean_r2 = [sum(i)/len(i) for i in [r1, r2]]

#divide each value in realized returns from the mean method #1 to get variance
var_r1, var_r2 = map(lambda x,y: sum([(x - i)**2 for i in y])/(len(y) - 1), [mean_r1, mean_r2], [r1, r2])

#method2 uses more numpy but is slower
var_r1, var_r2 = [np.sum(np.square(x- y))/(len(y) - 1) for x,y in zip([mean_r1, mean_r2], [r1, r2])]

#get the standard deviation value
std_r1, std_r2 = [np.sqrt(i) for i in [var_r1, var_r2]]

#first weight column, convert to numpy for vectorized operations
weight1 = np.array([i / 10 for i in range(0,11,1)])

#second weight column
weight2 = np.array(list(reversed(weight1)))

#errors calculated by subtracticting each value from mean
errors_r1, errors_r2 = list(map(lambda x,y: [i-x for i in y], [mean_r1, mean_r2], [r1, r2]))

#product of errors
error_prod = [x*y for x,y in zip(errors_r1, errors_r2)]

#sum of square errors, used in the variance forumula
sserrors_r1, sserrors_r2 = list(map(lambda errors: sum([error**2 for error in errors]), [errors_r1, errors_r2]))

#covariance or r1 and r2, the sum of the product of the errors divided by n-1
cov = (sum(error_prod)/4)

#correlation of r1 and r2
corr = sum(error_prod)/np.sqrt(sserrors_r1 * sserrors_r2)
#or more simply
corr = cov/(std_r1 * std_r2)

#portfolio weighted returns
rp = np.add(*[x*y for x,y in zip([weight1, weight2], [mean_r1, mean_r2])])

#df structure, will change to an array
mydf = pd.DataFrame({"w1": weight1, "w2": weight2,
                     "R1": mean_r1, "R2" : mean_r2,
                     "Rp": rp,
                     "stdR1": std_r1, "stdR2": std_r2,
                     "cov": cov})

mydf

#minimum variance portfolio (to do)
w1 = (std_r2**2 - cov) / (std_r1**2  + std_r2**2 - (2 * cov))

#general portfolio variance formula
my_var = (weight1**2 * std_r1**2) + (weight2**2 * std_r2**2) + (2 * weight1 * weight2 * cov)

#creating a general plot, using portfolio standard deviation std and return lists
dat = pd.DataFrame({"std": np.sqrt(stds), "rets" : rp})

#three stock portfolio
#get the variance and weight of each and then add the combinations
#best to grab from a list

    
#get the data
#get the data
df2 = yq.Ticker([ "AMZN", "MMM"], asynchronous = True).history(period = "10y", interval="3mo", start = "2012-06-01")

def stock_returns() -> [pd.Series]:
    dfs = []
    for mf in [df2.loc[[i]] for i in np.unique(df2.index.get_level_values(0))]:
        #return all values from first month of year (every 4 months)
        close = np.array(mf.iloc[[i in range(0,mf.shape[0], 4) for i in range(0,mf.shape[0], 1)], :].close)
        #get returns in percentage
        ret = (close[1:]/close[:-1]) - 1
        dfs.append(ret)
    return dfs

df = stock_returns()

def get_params(rets):
    means = [i.mean() for i in rets]
    errors_list = [(ret - mean) for mean,ret in zip(means, rets)]
    squared_errors = [errors**2 for errors in errors_list]
    variances = [sum(sq_error)/(len(sq_error) - 1) for mean,sq_error in zip(means, squared_errors)]
    #might not need this
    standard_dev = np.sqrt(variances)

    return {"variances": variances, "std_dev": standard_dev, "mean": means, 
    "sq_errors": squared_errors, "errors" : errors_list}

params = get_params(df)

pkl_index_value = zip(range(2, 7, 1), [i+".pkl" for i in ["two", "three", "four", "five", "six"]])

#permutations, filter out the ones that don't equal 1 and
def filter_combo_write_pkl(n_combos: int, filename: str):
    weights = [i/100 for i in range(0, 101, 5)]
    combos = permutations(weights, n_combos)
    filters = pd.DataFrame(filter(lambda x: sum(x) == 1, combos))

    #convert to pickle
    filters.to_pickle(filename)


#write to csv   
for index, names in pkl_index_value:
    filter_combo_write_pkl(index, names)



def portfolio_variance(pkl_file, limit, params):
    param = [param[:limit] for param in params.values()]
    
    #sum of squared errors
    sserror = [sum(i) for i in param[3]]
    #weights
    weights = pd.read_pickle(pkl_file)
    #variance
    var = np.array(param[0])
    std = np.sqrt(var)
    #sum prod / sqrt(sq_error1 * sq_error2)
    cor = sum(list(map(lambda *error: np.prod(error), *param[4])))/np.sqrt(np.array(sserror).prod())
   
    w_a = weights**2 * var
    return cor

#next step correlation
#perhaps use a switch stagement for the csv file
portfolio_variance("two.csv", 2).sum(axis = 1) + (2 * wts.prod(axis = 1)