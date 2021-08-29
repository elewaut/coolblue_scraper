# -*- coding: utf-8 -*-
"""
@author: elewaut
"""

import pandas as pd
from tqdm import tqdm
from datetime import datetime
from selenium import webdriver
from selenium.common import exceptions
from time import sleep
from random import randint


def get_driver(URL):
    options = webdriver.ChromeOptions()
    options.headless = False
    DRIVER_PATH = r'C:PATH/chromedriver.exe'
    driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
    driver.get(URL)
    return driver
    
def accept_cookie(driver):
     driver.implicitly_wait(10)
     driver.find_element_by_xpath('//*[@aria-label="Accepteer onze cookies"]').click()
     return driver


def get_product_categories(driver, searched_category):
    parent_elem = driver.find_element_by_xpath('.//li[contains(@data-category-group, "{}")]'.format(searched_category))
    child_elements = parent_elem.find_elements_by_xpath('.//div/div/ul/li/span/a')
    product_category_titles = []
    for child in child_elements:
        product_category_titles.append(child.get_attribute('href'))
    if product_category_titles:
        return product_category_titles
    else:
        pass 

def get_amount_of_pages(driver):
    if driver.find_elements_by_xpath('//a[contains(@aria-label, "Ga naar de volgende pagina")]'):
        amount_of_pages = driver.find_elements_by_xpath('//a[contains(@aria-label, "Ga naar pagina")]')[-1].text.strip()
    else:
        return 1
    try:
        return int(amount_of_pages)
    except ValueError:
        return amount_of_pages

def get_product_cards(driver):
    product_cards = driver.find_elements_by_xpath('//div[contains(@class, "product-card__details product-card__custom-breakpoint js-product-details")]')
    return product_cards

def product_card_unfold(product_card, product_category):
    product_name = product_card.find_element_by_xpath('.//div/a').text.strip()
    product_category = product_category
    try:
        price = product_card.find_element_by_xpath('.//div/span/strong').text.strip()
    except exceptions.NoSuchElementException:
        price = ""
    try:
        temp = product_card.find_element_by_xpath('.//meter[contains(@class, "review-rating__score-meter")]')
        rating = temp.get_attribute('value')
    except exceptions.NoSuchElementException:
        rating = ""
    try:
        review_amount = product_card.find_element_by_xpath('.//span[contains(@class, "review-rating__reviews text--truncate")]').text.strip()
    except exceptions.NoSuchElementException:
        review_amount = ""
    return product_name, price, rating, review_amount, product_category

def sleep_for_random_interval():
    return sleep(randint(1,5))

def dataframe_to_excel(dataframe):
    dataframe.to_excel(r'PATH/{}_coolblue_raw_data_{}.xlsx'.format(datetime.now().strftime("%Y%m%d"), searched_category_file_name.lower()), index=False, header=True)

def run_script(general_url_website, searched_category):
    dataframe = pd.DataFrame()
    driver = get_driver(general_url_website)
    for url in get_product_categories(driver, searched_category):
        product_category = url.split("/", 3)[-1]
        print(product_category)
        driver_category = get_driver(url+"/filter")
        if driver_category.find_element_by_xpath('.//div[contains(@class, "cookie-notification__header")]'):
            accept_cookie(driver_category)
        for page in tqdm(range(0, get_amount_of_pages(driver_category))):
            driver_category.get(url+"/filter/?pagina={}".format(page))
            product_cards = get_product_cards(driver_category)
            for product_card in product_cards:
                temporary_product = product_card_unfold(product_card, product_category)
                product_card_temporary = pd.DataFrame(temporary_product).transpose().reset_index(drop=True)
                dataframe = pd.concat([dataframe, product_card_temporary], axis=0)
            sleep_for_random_interval()
                  
    driver.quit()

        
    dataframe = dataframe.rename(columns={0: "product_description", 1: "price", 2: "rating", 3: "amount_reviews", 4: "product_category"})
    dataframe["product_class"] = searched_category.lower()
    dataframe["date_of_scrape"] = datetime.now()
    dataframe_to_excel(dataframe)

    
if __name__ == '__main__':
    categories_to_search = ["Computers & tablets", "Beeld & geluid"]
    for category in categories_to_search:
        searched_category = category
        searched_category_file_name = category.replace(" ", "")
        run_script('https://www.coolblue.nl/?pagina={}', searched_category)

