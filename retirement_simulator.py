"""
    Daniel Alfonsetti, daniel.alfonsetti@gmail.com, August 10, 2019
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

    If you like this, check out https://www.reddit.com/r/financialindependence/
    and the "FIRE" movement (Financial independent, retire early)

    Please feel free to clone and make pull requests!

    Note: Average cost of college varies a lot. You should look here
    (https://www.valuepenguin.com/student-loans/average-cost-of-college)
    to figure out what the price of college for your kids would be.
 """

# TODO: Add ability to adjust certain parameters during certain years.
# TODO: Add randomness/monte carlo aspects

import pandas as pd
import math
import copy

############################
# Helper functions
def Dprint(text, display=False): # For debugging
    if display:
        print(text)

def place_value(number):
    return ("{:,}".format(number))
############################


class Event():

    def __init__(self, start_age, net_flow = 0, end_age = math.inf, duration = None):

        self.start_age = start_age
        if duration:
            self.end_age = start_age + duration
        else:
            self.end_age = end_age

        self.active = False
        self.net_flow = net_flow

    def update(self, simulation_obj):

        if self.start_age <= simulation_obj.age < self.end_age:
            self.active = True
        else:
            self.active = False


class Kid(Event):

    def __init__(self, start_age, college = True):
        super().__init__(start_age)

        self.kid_age = 0
        self.college = college


    def update(self, simulation_obj):
        super().update(simulation_obj)

        if self.active:
            if self.kid_age < 18:
                self.net_flow = -simulation_obj.child_costs
            elif self.kid_age < 22 and self.college:
                self.net_flow = -simulation_obj.college_price
            else:
                self.net_flow = 0
                 # TODO: Your child could potentially give back.
                 # Run simlution for the child to estimate how much they will give back????
                 # Simulate child getting a disease (???)

            self.kid_age += 1


class Disease(Event):
    pass

class Marriage(Event):
    pass

class Divorce(Event):
    pass


class retirementSimulator():



    # TODO: Would storing these things in a dictionary help?
    def __init__(self, starting_wealth = -30000, rate_of_return = 0.07,
             cost_of_living = 40000, inflation = 0.03,
             wage = 80000, yearly_raise = 0.027,
             withdrawl_rate = 0.04, start_working_age = 22,
             target_retirement_age = 64, work_till_at_least = 35, death_age = 100,
             child_costs = 10000, college_price = 40000,
             events = [Kid(27)]):

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

        self.child_costs = child_costs
        self.child_costs_save = child_costs

        self.college_price = college_price
        self.college_price_save = college_price

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


        # Programming note: you need to make a copy of events each time you make a new retirementSimulator object
        # because, in python, the default parameters are evaluted in the function header before
        # it ever gets called. If you don't make a copy, the same event object in the default list
        # would be shared among multiple retirementSimulator instances.
        self.events = copy.deepcopy(events)
        self.events_save = copy.deepcopy(events)

        # Storage container
        self.summaryDf = None

        self.age = start_working_age
    ################################################################################
    ################################################################################

    def update_events(self):
        for event in self.events:
            event.update(self)

    def total_events_net_flow(self):
        total_net_flow = 0
        for event in self.events:
            if event.active:
                total_net_flow += event.net_flow
        return total_net_flow


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

        lifetime = []

        ################
        # Working years
        ###############

        # TODO: Separate retirement and working years into separate events maybe
        for i in range(self.start_working_age, self.target_retirement_age):

          self.update_events()
          self.total_wealth += self.total_events_net_flow()

          withdrawl_pre = self.total_wealth*self.withdrawl_rate
          withdrawl_post = withdrawl_pre - self.calculate_longterm_cap_gains_tax(withdrawl_pre, yrs_since_base = i - self.start_working_age)
          lifetime.append({'Age': i, 'Total Wealth': self.total_wealth,
                           "Wage": self.wage,
                           "Withdrawl (post tax)": None,
                           "Cost of Living": self.cost_of_living,
                           "Portfolio Returns": self.total_wealth*self.rate_of_return,
                           "Surplus": None,
                           "Surplus (Present $)": None,
                           "Theoretical Withdrawl (post tax)": withdrawl_post,
                           'Theoretical Surplus': withdrawl_post - self.cost_of_living,
                           'Theoretical Surplus (Present $)': (withdrawl_post - self.cost_of_living)/(1+self.inflation)**(i - self.start_working_age) # PDV calculation
                           })


          state_tax = self.calculate_state_tax()
          federal_tax = self.calculate_federal_tax(yrs_since_base = i - self.start_working_age)


          # The amount we save each year is our total wage from our job + our earnings from our portfolio
          # minus the amount we pay in taxes and the current cost of living
          self.total_wealth += (self.wage -state_tax- federal_tax - self.cost_of_living)+self.total_wealth*self.rate_of_return

          # Costs increase each year
          self.cost_of_living += self.cost_of_living*self.inflation
          self.child_costs += self.child_costs*self.inflation
          self.college_price += self.college_price*self.inflation

          # Wage increases each year
          self.wage *= (self.yearly_raise+1)

          self.age += 1


        ################
        # Retirement years
        ################

        for i in range(self.target_retirement_age, self.death_age+1):

            self.update_events()
            self.total_wealth += self.total_events_net_flow()

            withdrawl_pre = self.total_wealth*self.withdrawl_rate
            withdrawl_post = withdrawl_pre - self.calculate_longterm_cap_gains_tax(withdrawl_pre, yrs_since_base = i - self.start_working_age)

            lifetime.append({'Age': i, 'Total Wealth': self.total_wealth,
                             "Wage": None,
                             "Withdrawl (post tax)": withdrawl_post,
                             "Cost of Living": self.cost_of_living,
                             "Portfolio Returns": self.total_wealth*self.rate_of_return,
                             "Surplus": withdrawl_post - self.cost_of_living,
                             "Surplus (Present $)":  (withdrawl_post - self.cost_of_living)/(1+self.inflation)**(i - self.start_working_age),
                             "Theoretical Withdrawl (post tax)": None,
                             'Theoretical Surplus': None,
                             'Theoretical Surplus (Present $)': None
                            })


            # Costs increase each year
            self.cost_of_living += self.cost_of_living*self.inflation
            self.child_costs += self.child_costs*self.inflation
            self.college_price += self.college_price*self.inflation



            self.total_wealth += self.total_wealth*self.rate_of_return-withdrawl_pre

            self.age += 1


        self.summaryDf = pd.DataFrame(lifetime)
        self.summaryDf = self.summaryDf[['Age', 'Total Wealth',  "Portfolio Returns", "Wage", "Cost of Living",
                               'Withdrawl (post tax)', 'Surplus',"Surplus (Present $)",
                               "Theoretical Withdrawl (post tax)", 'Theoretical Surplus', 'Theoretical Surplus (Present $)']]




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
                                                    target_retirement_age = int(best_age), work_till_at_least = self.work_till_at_least_save,  death_age = self.death_age_save,
                                                    child_costs = self.child_costs_save, college_price = self.college_price_save,
                                                    events = self.events_save)

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
                print("You will not ever be able to meet your retirement goals! =(")
                print("Consider adjusting parameters until you have a reasonable goal.")


        else:
            print("Please run a simulation first!")
        print("\n")



# %%
if __name__ == "__main__":


    # Default. Start working at 22, have kid at 27.
    # Other parameters are fairly pessimistic.
    sim1 = retirementSimulator(events =[Kid(27)])
    sim1.run_simulation()
    sim1_results = sim1.summaryDf
    sim1.get_earliest_retirement()

    # Start working after a master's degree at 23, have kid at 27.
    sim2 = retirementSimulator(starting_wealth = -30000, rate_of_return = 0.10,
                 cost_of_living = 40000, inflation = 0.03,
                 wage = 90000, yearly_raise = 0.04,
                 withdrawl_rate = 0.04, start_working_age = 23,
                 target_retirement_age = 50, work_till_at_least = 30, death_age = 100,
                 events = [Kid(27)])
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

    # Higher starting wage, but without kids
    sim4 = retirementSimulator(starting_wealth = -30000, rate_of_return = 0.10,
             cost_of_living = 40000, inflation = 0.03,
             wage = 130000, yearly_raise = 0.04,
             withdrawl_rate = 0.04, start_working_age = 23,
             target_retirement_age = 50, work_till_at_least = 30, death_age = 100, events=[])
    sim4.run_simulation()
    sim4_results = sim4.summaryDf
    sim4.get_earliest_retirement()

    # High starting salary after a PhD, with a kid at 27
    sim5 = retirementSimulator(starting_wealth = -30000, rate_of_return = 0.10,
             cost_of_living = 40000, inflation = 0.03,
             wage = 185000, yearly_raise = 0.04,
             withdrawl_rate = 0.04, start_working_age = 26,
             target_retirement_age = 50, work_till_at_least = 30, death_age = 100, events=[Kid(27)])
    sim5.run_simulation()
    sim5_results = sim5.summaryDf
    sim5.get_earliest_retirement()


    # High starting salary after a PhD, with a kid at 27, 28 and 29 (3 kids)
    sim6 = retirementSimulator(starting_wealth = -30000, rate_of_return = 0.10,
             cost_of_living = 40000, inflation = 0.03,
             wage = 185000, yearly_raise = 0.04,
             withdrawl_rate = 0.04, start_working_age = 26,
             target_retirement_age = 50, work_till_at_least = 30, death_age = 100, events=[Kid(27), Kid(28), Kid(29)])
    sim6.run_simulation()
    sim6_results = sim6.summaryDf
    sim6.get_earliest_retirement()
