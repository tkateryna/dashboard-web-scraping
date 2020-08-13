# Import packages for ...
## pulling data from XML and HTML files
from bs4 import BeautifulSoup

## automating web browser interaction
from selenium import webdriver # module containing implementations of browser drivers
from webdriver_manager.chrome import ChromeDriverManager # Chrome driver
from selenium.webdriver.support import expected_conditions as EC # method for writing code that waits until conditions are met
from selenium.webdriver.support.ui import WebDriverWait # method for writing code that implements implicit or explicit waits
from selenium.webdriver.common.by import By # method for locating elements by their attributes
from selenium.webdriver import ActionChains # module for implementing browser interactions

## data manipulation
import pandas as pd
from datetime import datetime
import numpy as np
import time
import os

filters = {"Fiscal Year":0,"Ciruit":1,"State":2,"District":3,"Race":4,
          "Gender":5,"Age":6,"Citizenship":7,"Education":8,"Crime Type":9,
          "Category":10}

race = ["White", "Black", "Hispanic", "Other"]

crime_type = ["Administration of Justice", "Antitrust","Arson","Assault","Bribery/Corruption",
              "Burglary/Trespass","Child Pornography","Commercialized Vice","Drug Possession",
              "Drug Trafficking","Environmental","Extortion/Racketeering","Firearms",
              "Food and Drug","Forgery/Counter/Copyright","Fraud/Theft/Embezzlement","Immigration",
              "Individual Rights","Kidnapping","Manslaughter","Money Laundering","Murder",
              "National Defense","Obscenity/Other Sex Offenses","Prison Offenses","Robbery","Sexual Abuse",
              "Stalking/Harassing","Tax","Other"]
state = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware",
         "District Of Columbia","Florida","Georgia","Guam","Hawaii","Idaho","Illinois","Indiana","Iowa",
         "Kansas","Kentucky","Louisiana","Maine","Mariana Islands","Maryland","Massachusetts","Michigan",
         "Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey",
         "New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
         "Puerto Rico","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont",
         "Virgin Islands","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]

# Navitagion to Sentencing Outcomes page
def nav_to_sentencingoutcomes(driver, tab):
    """
    drive: driver
    tab: "Plea Status", "Sentence Type", "Sentence Length", "Fine/Restitution Amounts"
    """
    sentence_outcome_b = driver.find_element_by_xpath("//div[@title='Sentencing Outcomes']")
    sentence_outcome_b.click()
    sentence_length_b = driver.find_element_by_xpath("//div[@title='" + tab + "']")
    sentence_length_b.click()

# Navitagion to Major Crime Types page
def nav_to_majorcrimetypes(driver, tab):
    """
    drive: driver
    tab: "Drugs", "Immigration", "Firearms", "Economic Crime"
    """
    sentence_outcome_b = driver.find_element_by_xpath("//div[@title='Major Crime Types']")
    sentence_outcome_b.click()
    sentence_length_b = driver.find_element_by_xpath("//div[@title='" + tab + "']")
    sentence_length_b.click()

## Returns DF for Plea Status
def plea_status(driver, race):
    time.sleep(5)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    data = []
    # Find the table containing Sentence Type by Type of Crime
    table = soup.find('td', attrs={'class':'PTChildPivotTable'})
    # Append the body only
    table_body = table.find('tbody')

    # Spin through every row extracting information
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols]) # Do not get rid of empty values

    sentence_type_columns = ['Race', 'Crime', 'Plea N', 'Plea %', 'Trial N', 'Trial %']

    df = pd.DataFrame(data[8::2],columns=sentence_type_columns)
    df['Race'] = race

    return df


## Returns DF for Sentence Type
def sentence_type(driver, race):
    time.sleep(5)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    data = []
    # Find the table containing Sentence Type by Type of Crime
    table = soup.find('td', attrs={'class':'PTChildPivotTable'})
    # Append the body only
    table_body = table.find('tbody')

    # Spin through every row extracting information
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols]) # Do not get rid of empty values

    sentence_type_columns = ['Race', 'Crime', 'Total N', 'Total %', 'Fine Only N', 'Fine Only %',
         'Prison Only N', 'Prison Only %', 'Prison and Alternatives N',
         'Prison and Alternatives %', 'Probation Only N', 'Probation Only %',
         'Probation and Alternatives N', 'Probation and Alternatives %']

    df = pd.DataFrame(data[16::2],columns=sentence_type_columns)
    df['Race'] = race

    return df


## Returns DF for Sentence Length
def sentence_length(driver, race, crime_type):
    """
    This function retrieves information from the Sentence Length page.
    df has to be defined before running this function
    """
    time.sleep(5)
    page_source = driver.page_source # page source gathered each time
    soup = BeautifulSoup(page_source, 'lxml')
    data = []

    # Spin through all the graphs to extract information
    piechart_t = ["Distribution of Sentence Length", "Distribution of Imprisonment Length"]
    barchart_title = ["Average and Median Sentence Length", "Average and Median Imprisonment Length", "Average and Median Supervised Release"]

    for n in piechart_t:
        # find the td that contains the name of the table you are interested in
        sl = soup.find('td', attrs={'title':n})
        # go up two parent levels, so that we can drill back
        parent_sl = sl.findParent('table').findParent('table')
        # find all occurences with text
        parent_slt = parent_sl.findAll('text')
        # gather all text in a list
        cols = [ele.text.strip() for ele in parent_slt]
        # get name of the chart + sentence length, split text that contains
        # name plus percentage
        # eg 120 Months or More   19.3%
        # and get the decription element
        for i in cols:
            # data is parsed back in three ways
            if "   " in i:
                # eg. 60 to 119 Months   13.5%
                # append separately the title and then the value
                data.append([n + " " + i.split("  ")[:-1][0]])
                data.append([i.split("   ")[-1]])
                # do the normal split
            elif "%" not in i:
                # eg. 120 Months or More
                # append the name
                data.append([n + " " + i])
            elif "%" in i:
                if len(i) > 7:
                    # eg. 60 to 119 Months 17.5%
                    data.append([n + " " + i.rsplit(' ', 1)[0]])
                    data.append([i.rsplit(' ', 1)[-1]])
                else:
                    # eg.    24.7%
                    # append the percentage value
                    data.append([i])
    for n in barchart_title:
        # find the td that contains the name of the table you are interested in
        sl = soup.find('td', attrs={'title':n})
        # go up two parent levels, so that we can drill back
        parent_sl = sl.findParent('table').findParent('table')
        # find all occurences with text
        parent_slt = parent_sl.findAll('text')
        # gather all text in a list
        cols = [ele.text.strip() for ele in parent_slt]
        # all even element in the list contain description
        data.append([ele for ele in cols[:2]]) # append the title
        # all odd elements in the list contain value
        data.append([ele for ele in cols[-2:]]) # append the result
    #print(data)
    # get all column names extracted from the nested list
    column_data = [item for sublist in data[::2] for item in sublist]
    #print(column_data)
    #print("\n")
    # get all data values extracted from the nested list
    row_data = [item for sublist in data[1::2] for item in sublist]
    #print(row_data)

    df = pd.DataFrame([row_data],columns=column_data)
    df['Race'] = race
    df['Crime Type'] = crime_type
    print('DF has been generated for race {}, crime type {}'.format(race, crime_type))
    return df

## Expands the table so that all rows are visible, sometime
def expand_list(driver):
    """
    Expand the list so that all crimes are visible, sometimes needs to run twice
    """
    driver.find_element_by_xpath("//img[contains(@src,'/analytics/res/v-*xNdJt5L9yA/s_blafp/viewui/pivot/showallrows_ena.png')]").click()

# Run the following once so that the dropdown with checkboxes opens up
# Opens/Closes the drop down list
def toggle_dropdown(driver, category):
    """
    This function opens a dropdown for the required category.
    Once the dropdown is open, select required checkboxes with another function.
    """
    num=filters.get(category)
    driver.find_elements_by_xpath("//img[@src='/bicustom/res/s_IDA/master/selectdropdown_ena.png']")[num].click()
    print("Dropdown has been toggled")

# Select all or unselect elements in the dropdown
def select_all(driver, checkbox_list):
    """
    This functions selects all checkboxes in the drop down.
    Before running this function make sure the drop down list is open.
    checkbox_list: list of checkbox elements in a particular filter category eg crime_type, race
    """
    for i in checkbox_list:
        parent_elem = driver.find_element_by_xpath("//div[@title='" + i + "']")
        child_elements = parent_elem.find_element_by_xpath(".//*").find_element_by_xpath(".//*")

        if child_elements.get_attribute("type") == 'checkbox':
            if child_elements.get_attribute("checked") == 'true':
                #print("Checkbox already on: {}".format(i))
                pass
            else:
                child_elements.click()
                #print("Checkbox toggled to on: {}".format(i))
        else:
            print("Element is not a checkbox")

    print("All checkboxes toggled to on")
    # Click out so that the page can reload
    driver.find_element_by_xpath("//body").click()

# Unselect all or unselect elements in the dropdown
def unselect_all(driver, checkbox_list, category):
    """
    This functions selects/unselects all checkboxes in the drop down.
    Before running this function make sure the drop down list is open.
    checkbox_list: list of checkbox elements in a particular filter category eg crime_type, race
    """
    num=filters.get(category)
    dropdown = driver.find_elements_by_xpath("//img[@src='/bicustom/res/s_IDA/master/selectdropdown_ena.png']")[num]
    dropdown.click()
    time.sleep(5)
    for i in checkbox_list:
        parent_elem = driver.find_element_by_xpath("//div[@title='" + i + "']")
        child_elements = parent_elem.find_element_by_xpath(".//*").find_element_by_xpath(".//*")

        if child_elements.get_attribute("type") == 'checkbox':
            if child_elements.get_attribute("checked") == 'true':
                child_elements.click()
                #print("Checkbox toggled to off: {}".format(i))
            else:
                #print("Checkbox already off: {}".format(i))
                pass
        else:
            print("Element is not a checkbox")

    print("All checkboxes toggled to off")
    # Click out so that the page can reload
    driver.find_element_by_xpath("//body").click()

# Open a dropdown of a particular category, toggle a dropdown for a known value and update the dashboard
def one_checkbox(driver, checkbox_value, check_status, category, val=1):
    """
    checkbox_value: "White", "Black", "Hispanic", "Other"
    checked_status: "true" or "None"
    category: "Race", "Crime Type"
    val: for "Other" the val is either 1 or 0
    """

    num=filters.get(category)
    dropdown = driver.find_elements_by_xpath("//img[@src='/bicustom/res/s_IDA/master/selectdropdown_ena.png']")[num]
    dropdown.click()
    time.sleep(2)

    if checkbox_value == "Other":
        if category == "Race":
            parent_elem = driver.find_elements_by_xpath("//div[@title='" + checkbox_value + "']")[val]
        elif category == "Crime Type":
            parent_elem = driver.find_elements_by_xpath("//div[@title='" + checkbox_value + "']")[val]
    else:
        parent_elem = driver.find_element_by_xpath("//div[@title='" + checkbox_value + "']")

    child_elements = parent_elem.find_element_by_xpath(".//*").find_element_by_xpath(".//*")

    if child_elements.get_attribute("type") == 'checkbox':
        print("Element is a checkbox")

        if check_status == child_elements.get_attribute("checked"):
            print("Checkbox status as expected: {}".format(checkbox_value))
        else:
            # Select the checkbox
            child_elements.click()
            # Click out so that the page can reload
            driver.find_element_by_xpath("//body").click()
            print("Checkbox updated: {}".format(checkbox_value))

    else:
        print("Element is not a checkbox")
    time.sleep(2)
    #num=filters.get(category)
    #dropdown = driver.find_elements_by_xpath("//img[@src='/bicustom/res/s_IDA/master/selectdropdown_ena.png']")[num].click()
