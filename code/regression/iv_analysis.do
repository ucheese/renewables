clear all

* ------------------------------------------------------------------------------
* Read data 
* ------------------------------------------------------------------------------

import delimited "/Users/yuqizhang/Dropbox/Thesis/intermediates/master/master.csv", encoding(ISO-8859-1)

* ------------------------------------------------------------------------------
* Final data cleaning
* ------------------------------------------------------------------------------

* there are 2 duplicates, drop for now
duplicates tag year fips, gen(dup)
drop if dup == 1
drop dup

* tsset the data
tsset fips year

* generate logged variables
gen ln_amt_orig = log(amt_orig)
gen ln_sf_housing_price = log(sf_housing_price)

* generate indicators
gen has_plants_wind = 0
replace has_plants_wind = 1 if n_plants_wind > 0
gen has_plants_solar = 0
replace has_plants_solar = 1 if n_plants_solar > 0

/*
fill in certain variables as 0 if they are missing

this is because if there are not enough establishments, 
the data provider makes them missing to deidentify
*/

replace employment_solar_power = 0 if employment_solar_power == .
replace employment_wind_power = 0 if employment_wind_power == .
replace n_esttabs_wind_power = 0 if n_esttabs_wind_power == .
replace employment_wind_power = 0 if employment_wind_power == .


* ------------------------------------------------------------------------------
* OLS (Outcome on Plants)
* ------------------------------------------------------------------------------

* Loan outcomes

global loan_outcomes n_loan_orig amt_orig ln_amt_orig n_loan_orig_sfam amt_orig_sfam ///
						n_sb_loan_orig sb_amt_orig n_sb

local i = 1
foreach y of global loan_outcomes {
	eststo m`i': qui reghdfe `y' l.has_plants_wind, absorb(fips year) vce(cluster fips year)
	local i = `i'+1
}

esttab m1 m2 m3 m4 m5 m6

* Housing prices

global housing_outcomes sf_housing_price ln_sf_housing_price
local i = 1
foreach y of global housing_outcomes {
	eststo m`i': qui reghdfe `y' l.has_plants_wind, absorb(fips year) vce(cluster fips year)
	local i = `i'+1
}

esttab m1 m2

* Government financing

global gov_fin_outcomes total_rev total_rev_own_sources total_taxes gen_charges ///
							property_tax total_exp

local i = 1
foreach y of global gov_fin_outcomes {
	eststo m`i': qui reghdfe `y' l.has_plants_solar, absorb(fips year) vce(cluster fips year)
	local i = `i'+1
}

esttab m1 m2 m3 m4 m5 m6

*  Employment

global emp_outcomes n_esttabs_total employment_total avg_wkly_wage_total employment_solar_power employment_wind_power

local i = 1
foreach y of global emp_outcomes {
	eststo m`i': qui reghdfe `y' l.has_plants_wind, absorb(fips year) vce(cluster fips year)
	local i = `i'+1
}

esttab m1 m2 m3 m4 m5


* ------------------------------------------------------------------------------
* First Stage
* ------------------------------------------------------------------------------

reghdfe has_plants_wind mean_wind, absorb(fips year) vce(cluster fips year)
predict y


* ------------------------------------------------------------------------------
* Second Stage
* ------------------------------------------------------------------------------

global housing_outcomes sf_housing_price ln_sf_housing_price
local i = 1
foreach y of global housing_outcomes {
	eststo m`i': qui reghdfe `y' y, absorb(fips year) vce(cluster fips year)
	local i = `i'+1
}

esttab m1 m2

