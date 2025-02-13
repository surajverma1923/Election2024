# INDIAN ELECTIONS DATA WEB SCRAPER. USES DATA FROM ECI.GOV.IN, SELENIUM, AND BEAUTIFULSOUP.

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from pathlib import Path
import pandas as pd
import csv

# PART 0: SET UP
# End fields to hold scraped data
state = []
constituency = []
candidates = []
parties = []
evm_votes = []
postal_votes = []
total_votes = []
vote_percentages = []

# Field to hold state abbreviations (not end data)
state_abbreviations_list = []

# Temporary field to store values for each constituency (will update for each state) (not end data)
constituency_value_holder = []

# Field to hold number of constituencies in each state (not end data)
constituencies_in_state_list = []

# Temporary field to store constituency count (not end data)
constituency_number = 0

# Temporary fields to store data about candidates, parties, EVM votes, postal votes, total votes, and vote percentage in each constituency (not end data). 
constituency_candidates_holder = []
constituency_parties_holder = []
constituency_evm_votes_holder = []
constituency_postal_votes_holder = []
constituency_total_votes_holder = []
constituency_vote_percentages_holder = []

# End and temporary fields specific to Jammu & Kashmir, which has an additional field, "Migrant Votes"
jk_constituency = []
jk_candidates = []
jk_parties = []
jk_evm_votes = []
jk_migrant_votes = []
jk_postal_votes = []
jk_total_votes = []
jk_vote_percentages = []
constituency_migrant_votes_holder = []

# PART 1: GET ECI STATE CODES/ABBREVIATIONS
# Use selenium to open starting URL
start_url = 'http://results.eci.gov.in/pc/en/constituencywise/ConstituencywiseU011.htm?ac=1'
driver = webdriver.Chrome()
driver.get(start_url)

# Identify state codes for each of India's state & union territories - using HTML text from page source
initial_soup = BeautifulSoup(driver.page_source, 'lxml')
state_options = initial_soup.find('table', class_='tabc').findAll('tr')[10].td.findAll('option')[1:37]
for option in state_options:
    state_abbreviations_list.append(option['value'])
state_abbreviations_list.sort()
print(state_abbreviations_list)

# PART 2: GET NUMBER OF CONSTITUENCIES IN EACH STATE (used for navigating URLs)
for state_code in state_abbreviations_list:
    state_url ='https://results.eci.gov.in/PcResultGenJune2024/partywisewinresultState-369.htm'
    driver.get(state_url)
    state_soup = BeautifulSoup(driver.page_source, 'lxml')
    constituency_values = state_soup.find('table', class_='tabc').findAll('tr')[10].td.findAll('option')[38:]
    for option in constituency_values:
        constituency_value_holder.append(option['value'])
    constituencies_in_state_list.append(len(constituency_value_holder))
    constituency_value_holder = []
    sleep(1)
print(constituencies_in_state_list)

# PART 3: WEB SCRAPER
# Obtain data for each constituency by looping through all of the states and all of the constituencies in each state
for i in range(len(state_abbreviations_list)):
    for j in range(1, (constituencies_in_state_list[i]+1)):
        
        # Navigate to the particular URL        
        constituency_url = 'http://results.eci.gov.in/pc/en/constituencywise/Constituencywise' + state_abbreviations_list[i] + str(j) + '.htm?ac=' + str(j)
        driver.get(constituency_url)

        # Use BeautifulSoup to retrieve relevant data
        constituency_soup = BeautifulSoup(driver.page_source, 'lxml')
        text = constituency_soup.find('table', class_='tabc').findAll('table')[7]
        constituency_info = text.th.string
        tabular_data = text.findAll('tr')
        usable_data = tabular_data[6:(len(tabular_data)-1)]
        
        # Insert data from temporary fields into end result fields. For state and constituency fields, one value is inserted for each constituency. Need to do this before the next step because the data for the Jammu & Kashmir state is formatted differently.
        constituency_info_list = constituency_info.replace('\n', '').strip().split('-', 1)
        state.append(constituency_info_list[0].title())
        constituency.append(constituency_info_list[1].title())

        # Insert data into temporary fields for each row of the ECI table for that particular constituency. Each row responds to one candidate for office in that constituency. Also, format data as string/int/float and edit data in final 'Total' row to better represent desired information
        #Jammu and Kashmir table has an extra column - "Migrant Votes" - which means the web scraper has to act differently in that case
        if (state[constituency_number] != 'Jammu & Kashmir'):
            
            for row in usable_data:
                candidate_data = []
                candidate_info = row.findAll('td')
                for data_entry in candidate_info:
                    candidate_data.append(data_entry.string)
                constituency_evm_votes_holder.append(int(candidate_data[3]))
                constituency_postal_votes_holder.append(int(candidate_data[4]))
                constituency_total_votes_holder.append(int(candidate_data[5]))  
                if candidate_data[6] is None:
                    constituency_candidates_holder.append('TOTAL')
                    constituency_parties_holder.append('TOTAL')
                    constituency_vote_percentages_holder.append(100.0)
                else:
                    constituency_candidates_holder.append(candidate_data[1].title())
                    constituency_parties_holder.append(candidate_data[2].title())
                    constituency_vote_percentages_holder.append(float(candidate_data[6]))
        
            # Insert data from temporary fields into end result fields. In the other fields from state and constituency (candidates, parties, evm_votes, etc.), a list of values is inserted which represents the information for each candidate running for office.
            candidates.append(constituency_candidates_holder)
            parties.append(constituency_parties_holder)
            evm_votes.append(constituency_evm_votes_holder)
            postal_votes.append(constituency_postal_votes_holder)
            total_votes.append(constituency_total_votes_holder)
            vote_percentages.append(constituency_vote_percentages_holder)

            # Reset temporary fields
            constituency_candidates_holder = []
            constituency_parties_holder = []
            constituency_evm_votes_holder = []
            constituency_postal_votes_holder = []
            constituency_total_votes_holder = []
            constituency_vote_percentages_holder = []

            # Rest one second to approximate human web use
            sleep(1)

        # Now handle the Jammu & Kashmir case. I will create a separate Pandas dataframe for Kashmir (so am using special fields to capture the data) as well as incorporate the data from Jammu & Kashmir that fits under existing fields into the larger dataframe
        else:
            
            for row in usable_data:
                candidate_data = []
                candidate_info = row.findAll('td')
                for data_entry in candidate_info:
                    candidate_data.append(data_entry.string)
                constituency_evm_votes_holder.append(int(candidate_data[3]))
                constituency_migrant_votes_holder.append(int(candidate_data[4]))
                constituency_postal_votes_holder.append(int(candidate_data[5]))
                constituency_total_votes_holder.append(int(candidate_data[6]))  
                if candidate_data[7] is None:
                    constituency_candidates_holder.append('TOTAL')
                    constituency_parties_holder.append('TOTAL')
                    constituency_vote_percentages_holder.append(100.0)
                else:
                    constituency_candidates_holder.append(candidate_data[1].title())
                    constituency_parties_holder.append(candidate_data[2].title())
                    constituency_vote_percentages_holder.append(float(candidate_data[7]))
            
            jk_constituency.append(constituency_info_list[1].title())
            jk_candidates.append(constituency_candidates_holder)
            jk_parties.append(constituency_parties_holder)
            jk_evm_votes.append(constituency_evm_votes_holder)
            jk_migrant_votes.append(constituency_migrant_votes_holder)
            jk_postal_votes.append(constituency_postal_votes_holder)
            jk_total_votes.append(constituency_total_votes_holder)
            jk_vote_percentages.append(constituency_vote_percentages_holder)
            
            candidates.append(constituency_candidates_holder)
            parties.append(constituency_parties_holder)
            evm_votes.append(constituency_evm_votes_holder)
            postal_votes.append(constituency_postal_votes_holder)
            total_votes.append(constituency_total_votes_holder)
            vote_percentages.append(constituency_vote_percentages_holder)

            constituency_candidates_holder = []
            constituency_parties_holder = []
            constituency_evm_votes_holder = []
            constituency_migrant_votes_holder = []
            constituency_postal_votes_holder = []
            constituency_total_votes_holder = []
            constituency_vote_percentages_holder = []

            sleep(1)
            
        # Add one to constituency counter
        constituency_number += 1
        
# Exit the browser
driver.quit()

# PART 4: WRITE RESULTS TO CSV

data_folder = Path('output_data')

# Create general file with all constituency data
with open(data_folder/'election_data.csv', 'w', newline='') as general_file:
    writer = csv.writer(general_file)
    writer.writerow(['state', 'constituency', 'candidates', 'parties', 'evm_votes', 'postal_votes', 'total_votes', 'vote_percentages'])
    for i in range(len(state)):
        writer.writerow([state[i], constituency[i], candidates[i], parties[i], evm_votes[i], postal_votes[i], total_votes[i], vote_percentages[i]])

# J&K specific file with data for province of Jammu & Kashmir, which has the extra Migrant Votes field
with open(data_folder/'jk_data.csv', 'w', newline='') as jk_file:
    writer = csv.writer(jk_file)
    writer.writerow(['jk_constituency', 'jk_candidates', 'jk_parties', 'jk_evm_votes', 'jk_migrant_votes', 'jk_postal_votes', 'jk_total_votes', 'jk_vote_percentages'])
    for i in range(len(jk_constituency)):
        writer.writerow([jk_constituency[i], jk_candidates[i], jk_parties[i], jk_evm_votes[i], jk_migrant_votes[i], jk_postal_votes[i], jk_total_votes[i], jk_vote_percentages[i]])
        
# Now we will create another file with only the information about the winning candidate in each constituency (rather than about all of the candidates).
# Create fields to store desired information
winning_candidate = []
winning_party = []
winning_evm_votes = []
winning_postal_votes = []
winning_total_votes = []
winning_vote_percentage = []

# Save details for the winning candidate in each constituency based on the position of the candidate who got the most votes
for j in range(len(state)):
    max_votes = 0
    for k in range(len(candidates[j])):
        if total_votes[j][k] > max_votes:
            max_votes = total_votes[j][k]
            candidate_number = k
        else:
            pass
    print(candidate_number)
    winning_candidate.append(candidates[j][candidate_number])
    winning_party.append(parties[j][candidate_number])
    winning_evm_votes.append(evm_votes[j][candidate_number])
    winning_postal_votes.append(postal_votes[j][candidate_number])
    winning_total_votes.append(total_votes[j][candidate_number])
    winning_vote_percentage.append(vote_percentages[j][candidate_number])
    print(j)

# # Winning candidate data file
# with open(data_folder/'winning_candidate_data.csv', 'w', newline='') as general_file:
#     writer = csv.writer(general_file)
#     writer.writerow(['state', 'constituency', 'winning candidate', 'winning party', 'winning evm votes', 'winning postal votes', 'winning total votes', 'winning vote percentage'])
#     for i in range(len(state)):
#         writer.writerow([state[i], constituency[i], winning_candidate[i], winning_party[i], winning_evm_votes[i], winning_postal_votes[i], winning_total_votes[i], winning_vote_percentage[i]])
    
