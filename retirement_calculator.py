import pandas as pd
import matplotlib as plt

# Starting out with school debt.
total_wealth = -20000

 # Assume a 10% yearly return from our invested total wealth. Reasonable. The trinity portfolio is at 11.5%, but let's
 # be on the safe side. (Check out more about the trinity portfolio)
 # Then let's assume 1% in comission and fees. This gets us to 0.09 annulaized returns (not inflation adjusted)
rate_of_return = 0.09 


# MIT living wage calculator estimates $27942 is the required amount of money
# to live in New York City as a single adult in 2019. Lets take on 40000 to be conservative though.
# wThis is approximately the stipend for graduate students at Columbia. If they can do it, we can do it.
# ref: https://gsas.columbia.edu/student-guide/financing-your-education/stipend-and-salary-payments
# ref: http://livingwage.mit.edu/metros/35620
cost_of_living = 40000 


# Assume cost of living increases each year.
# US Fed Reserve keeps inflation around 2.5% on avearage. Let's say 3% to be conservative
inflation = 0.03

# Our goal is to retire by 40, starting work at age 23 after we get a masters in CS.
start_working_age = 23
retirement_age = 40 
death_age = 100

# Reasonable starting salary for someone with a masters degree in CS. If you don't have a masters degree,
# you probably would have started generating income a year or two earlier and have gotten a couple pay raises,
# so it would probably roughly wash in the end.
job_income = 120000
yearly_raise = 0.027 
# Average workers get a bump of ~2.7%. Best workers get bumps of around ~4.7%. (ref: https://www.investopedia.com/articles/personal-finance/090415/salary-secrets-what-considered-big-raise.asp)
# Even though I'm sure your an amazing worker, let's assume a bump of 2.7% to be conservative.

def calculate_longterm_capital_gains(amnt_to_sell):
    tax = 0
    # 2019 rates
    brackets = {(0,39375):0.1,(39376, 434550):0.15, (434551, float('inf')):0.37}

    for bracket in brackets:
        if amnt_to_sell > bracket[0]:
            tax += brackets[bracket]*(min(amnt_to_sell, bracket[1])-bracket[0])
    return tax



def calculate_shortterm_capital_gains(amnt_to_sell):
    # Short term capitals gains are taxed as ordinary income
    return calculate_federal_tax(amnt_to_sell)


def calculate_state_tax(job_income):
    # Based on NYC state tax
    return job_income*0.08


def calculate_federal_tax(income):
    tax = 0
    # Using 2019 single filer rates
    brackets = {(0,9700):0.1,(9700, 39475):0.12, (39475, 84200):0.22, (84200, 160725):0.24, (160725, 204100): 0.32, (204100, 510300):0.35, (510300, float('inf')):0.37}

    for bracket in brackets:
        if income > bracket[0]:
            tax += brackets[bracket]*(min(income, bracket[1])-bracket[0])
    return tax

# Working years
lifetime = [] # 23: {age: , total_wealth: , 4% TW: , job_income: , cost_of_living: , 

for i in range(start_working_age, retirement_age):

  four_tw_pre = total_wealth*0.04
  four_tw_post = four_tw_pre - calculate_longterm_capital_gains(four_tw_pre)
    
  lifetime.append({'Age': i, 'Total Wealth': total_wealth, 
                   "4% TW (pre tax)": four_tw_pre, "4% TW (post tax)": four_tw_post, 
                   "job_income": job_income, "Cost of Living": cost_of_living,
                   "Portfolio Returns": total_wealth*rate_of_return})
    
    
  # The amount we save each year is our total job_income from our job + our earnings from our portfolio - taxes and cost of living
  total_wealth += (job_income -calculate_state_tax(job_income)-calculate_federal_tax(job_income) - cost_of_living)+total_wealth*rate_of_return
  # Cost of living increases each year
  cost_of_living += cost_of_living*inflation
  # Assume we make
  job_income *= yearly_raise+1
  
  
print(total_wealth)
print(job_income)
print(cost_of_living)

# Retirement years
for i in range(retirement_age, death_age):
    
    
    four_tw_pre = total_wealth*0.04
    four_tw_post = four_tw_pre - calculate_longterm_capital_gains(four_tw_pre)
    
    lifetime.append({'Age': i, 'Total Wealth': total_wealth,
                     "4% TW (pre tax)": four_tw_pre, "4% TW (post tax)": four_tw_post, 
                     "job_income": 0, "Cost of Living": cost_of_living,
                     "Portfolio Returns": total_wealth*rate_of_return})
    
       
    cost_of_living += cost_of_living*inflation
    total_wealth += total_wealth*rate_of_return-total_wealth*0.04

# $163,862
summaryDf = pd.DataFrame(lifetime)
summaryDf = summaryDf[['Age', 'Total Wealth', '4% TW (pre tax)', '4% TW (post tax)', "job_income", "Cost of Living", "Portfolio Returns"]]



