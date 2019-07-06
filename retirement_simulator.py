"""
    Daniel Alfonsetti, daniel.alfonsetti@gmail.com, July 6, 2019
    ------------------------------------------------------------
    
    Born out of my desire to retire at 40, this is a short script to get a 
    rough estimate of how much money one needs to save in order to have your 
    investments pay for your cost of living ('retire'). While working, 
    it assumes that you are saving all money
    that you make after you pay your cost of living and your taxes. 
    You can update the cost of living parameter to fit your lifestyle.
    During retirement, it assumes that your only source of income is however 
    much you withdraw from your investments.
        
    Personally, I am using this in the context of college graduates in
    technical discplines as it assumes a fairly high starting salary
    but, it also doesn't make any assumptions about you becoming the
    CEO of the next big bank, so I think it is a reasonable esimator. Several
    of the default parameter values I use are fairly conservative, but I think
    this is warranted since often things in life don't go as planned. 
    
    I encourage you to play with the parameters to fit your life.
    
    NOTE 1: The tax brackets are not being adjusted upperwards over time with
    inflation like they would in real life.  Therefore, this simulation is 
    likely being even more conservative than it should be since it is
    simulating you paying more than you actually would in taxes.
    
    NOTE 2: This simulation assumes you are single and have no kids for your 
    entire life. This obviously is quite an assumption, and 
    thus won't suite everyone, but I still think this simulation is a good
    benchmark and has pedagogical value even if you plan on having a family.
    
"""

import pandas as pd

################################################################################
# Parameters
################################################################################

"""
 Total wealth represents how much money you have in investments.
 Put in negative numbers if you are starting with debt.
 Average student debt is ~$30000.
 ref: https://studentloanhero.com/student-loan-debt-statistics/
"""

total_wealth = -30000

"""
  Assume a 10% yearly return from our invested total wealth. Reasonable. 
  As a reference, a fairly safe portfolio, the trinity portfolio is at 11.5%, 
  but let's  be on the safe sid and assume 10% returns.
  (Check out more about the trinity portfolio here: 
  http://www.cambriainvestments.com/wp-content/uploads/2016/07/Trinity_DIGITAL_final.pdf)
  Then let's assume 1% in comission and fees. 
  This gets us to 0.09 annulaized returns (not inflation adjusted)
"""
rate_of_return = 0.09

"""
 MIT living wage calculator estimates $27942 is the required (read: minimum)
 amount of money to live in New York City as a single adult in 2019. 
 Lets take on 40000 to be conservative though. This is approximately 
 the stipend for graduate students. at Columbia. If they can do it, we can do it.
 If you want to simulate living life more luxuriously, increase this number.
 ref: https://gsas.columbia.edu/student-guide/financing-your-education/stipend-and-salary-payments
 ref: http://livingwage.mit.edu/metros/35620
"""
cost_of_living = 40000 

"""
 Assume cost of living increases each year.
 US Fed Reserve keeps inflation around 2.5% on avearage. Let's say 3% to be conservative
"""
inflation = 0.03

"""
  Starting salary for someone with a masters degree in CS is around 93K in 2017
  ref: https://www.naceweb.org/job-market/compensation/computer-science-class-of-2017s-top-paid-masters-grads/
  In metro areas like NYC, its probably a bit higher and closer to 100k, 
  but let's say 93K anyways.
"""
wage = 93000

"""
 Average workers get a bump of ~2.7% in salary per year.
 The best workers get bumps of around ~4.7%. 
 ref: https://www.investopedia.com/articles/personal-finance/090415/salary-secrets-what-considered-big-raise.asp
 Even though I'm sure your an amazing worker, let's assume a bump of 
 2.7% to be conservative.
"""
yearly_raise = 0.027


"""
 Rate at which you with draw from your total wealth in retirement
 At four percent withdrawl, you are still netting rate_of_return-withdrawl_rate
 every year in retirement, and thus your wealth is still growing. Four percent
 is industry recommended.
 ref: https://www.investopedia.com/terms/f/four-percent-rule.asp
"""
withdrawl_rate = 0.04

"""
 Our goal is to retire by 40, starting work at age 23 after we get a masters in CS.
 This means  we want our post tax withdrawl to cover the cost of living when we retire.
 Given how we set the other parameters, it is not possible to do so at 40,
 but it is at 48/49 If other parameters were not so conservative, 
 retiring closer to 40 is more tangible.
"""
start_working_age = 23
retirement_age = 48
death_age = 100 # Doesn't really matter. This simulation isn't trying to use all our wealth by death anyways.

################################################################################
################################################################################
# Helper functions 
def calculate_longterm_capital_gains(amnt_to_sell):
    tax = 0
    # 2019 rates
    # https://www.nerdwallet.com/blog/taxes/capital-gains-tax-rates/
    brackets = {(0,39375):0.1,(39376, 434550):0.15, (434551, float('inf')):0.37}

    for bracket in brackets:
        if amnt_to_sell > bracket[0]:
            tax += brackets[bracket]*(min(amnt_to_sell, bracket[1])-bracket[0])
    return tax

def calculate_shortterm_capital_gains(amnt_to_sell):
    # Short term capitals gains are taxed as ordinary income
    return calculate_federal_tax(amnt_to_sell)


def calculate_state_tax(wage):
    # Based on NY state tax. Includes NYC city tax
    # https://www.thebalance.com/cities-that-levy-income-taxes-3193246
    return wage*0.10

def calculate_federal_tax(wage):
    tax = 0
    # Using 2019 single filer rates
    # https://taxfoundation.org/2019-tax-brackets/
    brackets = {(0,9700):0.1,(9700, 39475):0.12, (39475, 84200):0.22, (84200, 160725):0.24, (160725, 204100): 0.32, (204100, 510300):0.35, (510300, float('inf')):0.37}

    for bracket in brackets:
        if wage > bracket[0]:
            tax += brackets[bracket]*(min(wage, bracket[1])-bracket[0])
    return tax

################
# Working years
################
    
lifetime = [] 
for i in range(start_working_age, retirement_age):

    
  withdrawl_pre = total_wealth*withdrawl_rate
  withdrawl_post = withdrawl_pre - calculate_longterm_capital_gains(withdrawl_pre)
    
  lifetime.append({'Age': i, 'Total Wealth': total_wealth,
                   "Wage": wage, 
                   "Withdrawl (post tax)": None, 
                   "Cost of Living": cost_of_living,
                   "Portfolio Returns": total_wealth*rate_of_return, 
                   "Surplus": None,
                   "Theoretical Withdrawl (post tax)": withdrawl_post,
                   'Theoretical Surplus': withdrawl_post - cost_of_living})
    
    
  # The amount we save each year is our total wage from our job + our earnings from our portfolio 
  # minus the amount we pay in taxes and the current cost of living
  total_wealth += (wage -calculate_state_tax(wage)-calculate_federal_tax(wage) - cost_of_living)+total_wealth*rate_of_return
 
  # Cost of living increases each year
  cost_of_living += cost_of_living*inflation
  # Wage increases each year
  wage *= (yearly_raise+1)
  
################
# Retirement years
################
  
for i in range(retirement_age, death_age):
    
    
    withdrawl_pre = total_wealth*withdrawl_rate
    withdrawl_post = withdrawl_pre - calculate_longterm_capital_gains(withdrawl_pre)
    
    lifetime.append({'Age': i, 'Total Wealth': total_wealth,
                     "Wage": None,
                     "Withdrawl (post tax)": withdrawl_post, 
                     "Cost of Living": cost_of_living,
                     "Portfolio Returns": total_wealth*rate_of_return,
                     "Surplus": withdrawl_post - cost_of_living,
                     "Theoretical Withdrawl (post tax)": None,
                     'Theoretical Surplus': None})
    
    # Cost of living increases each year
    cost_of_living += cost_of_living*inflation

    total_wealth += total_wealth*rate_of_return-withdrawl_pre

summaryDf = pd.DataFrame(lifetime)
summaryDf = summaryDf[['Age', 'Total Wealth',  "Portfolio Returns", "Wage", "Cost of Living", 
                       'Withdrawl (post tax)', 'Surplus',
                       "Theoretical Withdrawl (post tax)", 'Theoretical Surplus']]

"""
CONCLUSION:
    
    Under conservative assumptions about your future income, cost of living,
    rates of returns, inflation, and taxes, it is possible to retire by 48/49 
    when you graduate with a decently paying STEM or other white collar job 
    in a city and assume average levels of pay raises. By 'retire', we mean 
    withdraw at a safe level from your investments such that it completely 
    covers the cost of living while simultaneously still growing
    your net worth.
    
    If some assumptions were relaxed, retiring at 40 is much more tangible.
    
    For example, keeping all other default parameter values constant, 
    it is possible to retire  at 41/42 by focusing on your income  and having 
    a starting salary of 100K rather than 93K and performing well enough to get 
    raises of 4.7% per year on average. Also, this simulation doesn't include
    bonuses or side hussles.
"""

