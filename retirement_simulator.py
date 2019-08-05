"""
    Daniel Alfonsetti, daniel.alfonsetti@gmail.com, August 4, 2019
    ------------------------------------------------------------
    
    Born out of my desire to retire at 40, this is a short script to get a 
    rough estimate of how much money one needs to save in order to have your 
    investments pay for your cost of living ('retire'). While working, 
    it assumes that you are saving all money
    that you make after you pay your cost of living and your taxes. 
    You can update the cost of living parameter to fit your lifestyle.
    During retirement, it assumes that your only source of income is however 
    much you withdraw from your investments.
    
    I encourage you to play with the parameters to fit your life. Several
    of the default parameter values I use are fairly conservative, but I think
    this is warranted since often things in life don't go as planned. 
    
    NOTE 1: The tax brackets are not being adjusted upperwards over time with
    inflation like they would in real life.  Therefore, this simulation is 
    likely being even more conservative than it should be since it is
    simulating you paying more than you actually would in taxes.
    
    NOTE 2: This simulation assumes you are single and have no kids for your 
    entire life. This obviously is quite an assumption, and 
    thus won't suit everyone, but I still think this simulation is a good
    benchmark and has pedagogical value even if you plan on having a family.
    
"""

import pandas as pd
def place_value(number): 
    return ("{:,}".format(number)) 


class retirementSimulator():
    def __init__(self, starting_wealth = -30000, rate_of_return = 0.07,
             cost_of_living = 40000, inflation = 0.03,
             wage = 80000, yearly_raise = 0.027,
             withdrawl_rate = 0.04, start_working_age = 23,
             target_retirement_age = 64, work_till_at_least = 35, death_age = 100):
        
        """
         Total wealth represents how much money you have in investments.
         Put in negative numbers if you are starting with debt.
         Average student debt is ~$30000.
         ref: https://studentloanhero.com/student-loan-debt-statistics/
        """
        self.total_wealth = starting_wealth
        self.total_wealth_save = starting_wealth
        
        """
          Assume a 10% yearly return from our invested total wealth. Reasonable. 
          As a reference, a fairly safe portfolio, the trinity portfolio is at 11.5%, 
          but let's  be on the safe sid and assume 10% returns.
          (Check out more about the trinity portfolio here: 
          http://www.cambriainvestments.com/wp-content/uploads/2016/07/Trinity_DIGITAL_final.pdf)
          Then let's assume 1% in comission and fees. 
          This gets us to 0.09 annulaized returns (not inflation adjusted)
        """
        self.rate_of_return = rate_of_return
        self.rate_of_return_save = rate_of_return

        
        """
         MIT living wage calculator estimates $27942 is the required (read: minimum)
         amount of money to live in New York City as a single adult in 2019. 
         Lets take on 40000 to be conservative though. This is approximately 
         the stipend for graduate students. at Columbia. If they can do it, we can do it.
         If you want to simulate living life more luxuriously, increase this number.
         ref: https://gsas.columbia.edu/student-guide/financing-your-education/stipend-and-salary-payments
         ref: http://livingwage.mit.edu/metros/35620
        """
        self.cost_of_living = cost_of_living 
        self.cost_of_living_save = cost_of_living 

        
        """
         Assume cost of living increases each year.
         In modern times, the average yearly rate set by the US Fed. Reserve
         has mostly been less than 3%.
         ref: https://www.minneapolisfed.org/community/financial-and-economic-education/cpi-calculator-information/consumer-price-index-and-inflation-rates-1913
         Let's say 3% to be conservative though.
        """
        self.inflation = inflation
        self.inflation_save = inflation

        
        """
          Starting salary for someone with a masters degree in CS is around 93K in 2017
          ref: https://www.naceweb.org/job-market/compensation/computer-science-class-of-2017s-top-paid-masters-grads/
          In metro areas like NYC, its probably a bit higher and closer to 100k, 
          but let's say 93K anyways.
        """
        self.wage = wage
        self.wage_save = wage
        
        """
         Average workers get a bump of ~2.7% in salary per year.
         The best workers get bumps of around ~4.7%. 
         ref: https://www.investopedia.com/articles/personal-finance/090415/salary-secrets-what-considered-big-raise.asp
         Even though I'm sure your an amazing worker, let's assume a bump of 
         2.7% to be conservative.
        """
        self.yearly_raise = yearly_raise
        self.yearly_raise_save = yearly_raise
        
        
        """
         Rate at which you with draw from your total wealth in retirement
         At four percent withdrawl, you are still netting rate_of_return-withdrawl_rate
         every year in retirement, and thus your wealth is still growing. Four percent
         is industry recommended.
         ref: https://www.investopedia.com/terms/f/four-percent-rule.asp
        """
        self.withdrawl_rate = withdrawl_rate
        self.withdrawl_rate_save = withdrawl_rate
        
        """
         Our goal is to retire by 40, starting work at age 23 after we get a masters in CS.
         This means  we want our post tax withdrawl to cover the cost of living when we retire.
         Given how we set the other parameters, it is not possible to do so at 40,
         but it is at 48/49 If other parameters were not so conservative, 
         retiring closer to 40 is more tangible.
        """
        self.start_working_age = start_working_age
        self.start_working_age_save = start_working_age
        self.target_retirement_age = target_retirement_age
        self.target_retirement_age_save = target_retirement_age
        
        self.work_till_at_least = work_till_at_least
        self.work_till_at_least_save = work_till_at_least

        self.death_age = death_age # Doesn't really matter. This simulation isn't trying to use all our wealth by death anyways.
        self.death_age_save = death_age 
        
        # Storage container
        self.summaryDf = None
    ################################################################################
    ################################################################################
    # Helper functions 
    def calculate_longterm_cap_gains_tax(self, amnt_to_sell, yrs_since_base):
        tax = 0
        # Base year: 2019
        # 2019 rates: https://www.nerdwallet.com/blog/taxes/capital-gains-tax-rates/
    
        brackets = {(0,39375):              0.1,
                    (39376, 434550):        0.15,
                    (434551, float('inf')): 0.37}
        
        adj_brackets = {(bracket[0]*((self.inflation+1)**yrs_since_base), bracket[1]*((self.inflation+1)**yrs_since_base)): rate \
                                        for bracket, rate in brackets.items()}
    
        for bracket in adj_brackets:
            if amnt_to_sell > bracket[0]:
                tax += adj_brackets[bracket]*(min(amnt_to_sell, bracket[1])-bracket[0])
        return tax
    
    def calculate_shortterm_cap_gains_tax(self, amnt_to_sell):
        # Short term capitals gains are taxed as ordinary income
        return self.calculate_federal_tax(amnt_to_sell)
    
    
    def calculate_state_tax(self):
        # Based on NY state tax. Includes NYC city tax
        # https://www.thebalance.com/cities-that-levy-income-taxes-3193246
        return self.wage*0.10
    
    def calculate_federal_tax(self, yrs_since_base):
        tax = 0
        # Using 2019 single filer rates
        # https://taxfoundation.org/2019-tax-brackets/
        brackets = {(0,9700):0.1,(9700, 39475):0.12, (39475, 84200):0.22, (84200, 160725):0.24, (160725, 204100): 0.32, (204100, 510300):0.35, (510300, float('inf')):0.37}
    
        adj_brackets = {(bracket[0]*((self.inflation+1)**yrs_since_base), bracket[1]*((self.inflation+1)**yrs_since_base)): rate \
                                        for bracket, rate in brackets.items()}
        
        for bracket in adj_brackets:
            if self.wage > bracket[0]:
                tax += adj_brackets[bracket]*(min(self.wage, bracket[1])-bracket[0])
        return tax
    
    def run_simulation(self):
        ################
        # Working years
        ################
        
        lifetime = [] 
        for i in range(self.start_working_age, self.target_retirement_age):

            
          withdrawl_pre = self.total_wealth*self.withdrawl_rate
          withdrawl_post = withdrawl_pre - self.calculate_longterm_cap_gains_tax(withdrawl_pre, yrs_since_base = i - self.start_working_age)    
          lifetime.append({'Age': i, 'Total Wealth': self.total_wealth,
                           "Wage": self.wage, 
                           "Withdrawl (post tax)": None, 
                           "Cost of Living": self.cost_of_living,
                           "Portfolio Returns": self.total_wealth*self.rate_of_return, 
                           "Surplus": None,
                           "Theoretical Withdrawl (post tax)": withdrawl_post,
                           'Theoretical Surplus': withdrawl_post - self.cost_of_living})
            
            
          state_tax = self.calculate_state_tax()
          federal_tax = self.calculate_federal_tax(yrs_since_base = i - self.start_working_age)
          
          
          # The amount we save each year is our total wage from our job + our earnings from our portfolio 
          # minus the amount we pay in taxes and the current cost of living
          self.total_wealth += (self.wage -state_tax- federal_tax - self.cost_of_living)+self.total_wealth*self.rate_of_return
         
          # Cost of living increases each year
          self.cost_of_living += self.cost_of_living*self.inflation
          # Wage increases each year
          self.wage *= (self.yearly_raise+1)
          
        ################
        # Retirement years
        ################
          
        for i in range(self.target_retirement_age, self.death_age+1):
            
            
            withdrawl_pre = self.total_wealth*self.withdrawl_rate
            withdrawl_post = withdrawl_pre - self.calculate_longterm_cap_gains_tax(withdrawl_pre, yrs_since_base = i - self.start_working_age)
            
            lifetime.append({'Age': i, 'Total Wealth': self.total_wealth,
                             "Wage": None,
                             "Withdrawl (post tax)": withdrawl_post, 
                             "Cost of Living": self.cost_of_living,
                             "Portfolio Returns": self.total_wealth*self.rate_of_return,
                             "Surplus": withdrawl_post - self.cost_of_living,
                             "Theoretical Withdrawl (post tax)": None,
                             'Theoretical Surplus': None})
            
            # Cost of living increases each year
            self.cost_of_living += self.cost_of_living*self.inflation
        
            self.total_wealth += self.total_wealth*self.rate_of_return-withdrawl_pre
        
        self.summaryDf = pd.DataFrame(lifetime)
        self.summaryDf = self.summaryDf[['Age', 'Total Wealth',  "Portfolio Returns", "Wage", "Cost of Living", 
                               'Withdrawl (post tax)', 'Surplus',
                               "Theoretical Withdrawl (post tax)", 'Theoretical Surplus']]
        
    def get_earliest_retirement(self):
        """
            Gets earliest age in which a 4% withdrawl covers cost of living 
        """
        print("-----------------------")
        def strictly_increasing(L):
            return all(x<y for x, y in zip(L, L[1:]))
                
        
        if self.summaryDf is not None:
        
            vec= (self.summaryDf['Withdrawl (post tax)'] > self.summaryDf['Cost of Living']) | (self.summaryDf['Theoretical Withdrawl (post tax)'] > self.summaryDf['Cost of Living'])
            
            if any(vec):
                best_age = int(self.summaryDf[vec].iloc[0]['Age'])
                if self.work_till_at_least_save and best_age < self.work_till_at_least_save:
                    best_age = int(self.work_till_at_least)
                
                newSimulation = retirementSimulator(starting_wealth = self.total_wealth_save, rate_of_return = self.rate_of_return_save,
                                                    cost_of_living = self.cost_of_living_save, inflation = self.inflation_save, 
                                                    wage = self.wage_save, yearly_raise = self.yearly_raise_save, 
                                                    withdrawl_rate = self.withdrawl_rate_save, start_working_age = self.start_working_age_save,
                                                    target_retirement_age = int(best_age), work_till_at_least = self.work_till_at_least_save,  death_age = self.death_age_save)
                newSimulation.run_simulation()
                new_vec =(newSimulation.summaryDf['Withdrawl (post tax)'] > newSimulation.summaryDf['Cost of Living']) | (newSimulation.summaryDf['Theoretical Withdrawl (post tax)'] > newSimulation.summaryDf['Cost of Living'])
                runs_out =  int(newSimulation.summaryDf[new_vec].iloc[-1]['Age'])

                
                #runs_out = self.summaryDf[vec].iloc[-1]['Age']
                
                starting_retirement_wealth = round(newSimulation.summaryDf[vec].iloc[0]['Total Wealth'], 2)
                ending_retirement_wealth = round(newSimulation.summaryDf[vec].iloc[-1]['Total Wealth'], 2)
                
                delta_TW_retirement = round(ending_retirement_wealth - starting_retirement_wealth, 2)
                increasing_TW = ending_retirement_wealth > starting_retirement_wealth
                
                if runs_out < self.death_age:
                    print("You can retire at ", best_age, " but you will run out of money to pay for the cost of living at age ", runs_out, ".", sep="")
                else:
                                        
                    if increasing_TW:
                        print("You can retire at age ", best_age, ". At a withdrawl rate of ", self.withdrawl_rate*100, \
                              "%, your total wealth will support you till your death at age ", self.death_age_save, \
                              ", and you will have $", place_value(delta_TW_retirement), " more than you started with ($",place_value(starting_retirement_wealth)," increased to $",place_value(ending_retirement_wealth),")!", sep="")
                    else:                        
                        print("You can retire at age ", best_age, ". At a withdrawl rate of ", self.withdrawl_rate*100, \
                              "%, your total wealth will support you till your death at age ", self.death_age_save, \
                              ", but you should note that you will have $", place_value(delta_TW_retirement), " less than you started with ($",place_value(starting_retirement_wealth)," decreased to $",place_value(ending_retirement_wealth),")!", sep="")       
            else:
                print("You will not be able to retire ever! =(")
                
                
        else:
            print("Please run a simulation first!")
        print("\n")
        
if __name__ == "__main__":
    
    # Defaults
    sim1 = retirementSimulator()
    sim1.run_simulation()
    sim1_results = sim1.summaryDf
    sim1.get_earliest_retirement()
    
    # Start working after a master's degree at 23.
    sim2 = retirementSimulator(starting_wealth = -30000, rate_of_return = 0.10,
                 cost_of_living = 40000, inflation = 0.03,
                 wage = 90000, yearly_raise = 0.04,
                 withdrawl_rate = 0.04, start_working_age = 23,
                 target_retirement_age = 50, work_till_at_least = None, death_age = 100)
    sim2.run_simulation()
    sim2_results = sim2.summaryDf
    sim2.get_earliest_retirement()
    
    # Higher starting wage
    sim3 = retirementSimulator(starting_wealth = -30000, rate_of_return = 0.10,
                 cost_of_living = 40000, inflation = 0.03,
                 wage = 130000, yearly_raise = 0.04,
                 withdrawl_rate = 0.04, start_working_age = 23,
                 target_retirement_age = 50, work_till_at_least = 30, death_age = 100)
    sim3.run_simulation()
    sim3_results = sim3.summaryDf
    sim3.get_earliest_retirement()

    

