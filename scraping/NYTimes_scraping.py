#!/Users/andreaborsani/opt/anaconda3/bin/python
# Scraping libraries
# ### SELENIUM ###
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# ### BEAUTIFUL SOUP ###
from bs4 import BeautifulSoup as bs
import requests as re
# General purpose
import os
import pandas as pd
from pprint import pprint
import json
from datetime import date
from datetime import datetime, timedelta
from time import sleep
# Per poter salvare gli ouput in file di log.
import logging
# import coloredlogs
import shutil
import os
from time import time
# Per caricare il file di configurazione
from yaml import safe_load


def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
        'may':5,
        'jun':6,
        'jul':7,
        'aug':8,
        'sep':9,
        'oct':10,
        'nov':11,
        'dec':12
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')

def press_more_button(driver = None, times_button_pressed = 10, SLEEP_TIME = 3):
    for i in range(times_button_pressed):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        # Prendo un singolo elemento che fa Show More

        more_button = driver.find_element_by_xpath("//*/button[@data-testid='search-show-more-button']")
        # Controllo che becco il pulsante giusto (non si sa mai)
        if more_button.text.strip() != "SHOW MORE":
            logging.warning("SOME PROBLEM OCCURD")
            break
#        Print progress for the button
        logging.info("Progress Show More Button: "+str(i+1)+"/"+str(times_button_pressed))
        sleep(SLEEP_TIME)
        more_button.click()

# This functions scrapes the search page and produces a
# dictionary with:
# - Title
# - Date
# - Links
# - Summary
# - Authors
# - Category

def find_category(article = None):
    try:
        return(article.find_element_by_xpath("./div/div[2]/div/p").text.strip())
    except:
        logging.warning("Could not find article category")
        return("")

def find_authors(article = None):
    try:
        authors = article.find_element_by_xpath("./div/div[2]/div/a/p[2]").text.strip()#
    except:
        try:
            logging.warning("Trying to find Authors in Summary place")
            authors = article.find_element_by_xpath("./div/div/div/a/p").text.strip()
        except:
            logging.warning("Could not find article authors")
            authors = ""

# Eliminate by only if present
    if authors[:2] == "By":
        authors = authors[3:]
#        Do this cleaning only if there is more than 1 author
    if len(authors.split('and')) != 1:
#        Eliminate the By only if present
#            Split along the coma
        authors = authors.split(',')
#            Split aling the and
        for aut in authors[-1].split('and'):
            authors.append(aut)
        _ = authors.pop(-3)
    return authors

def find_summary(article = None):
    try:
        return(article.find_element_by_xpath("./div/div[2]/div/a/p").text.strip())
    except:
        logging.warning("Could not find article summary")
        return("")

def find_links(article = None):
    try:
        return(article.find_element_by_xpath("./div/div[2]/div/a").get_attribute("href").strip())
    except:
        logging.warning("Could not find article links")
        return("")

def find_date(article = None):
# Vai a fare direttamente qua dentro le regex
# per pulire le date
    try:
        article_date = article.find_element_by_xpath("./div/div").get_attribute("aria-label").strip()
    except:
        logging.warning("Could not find article date")
        return("")

    # Dividi lungo gli spazzi bianchi
    article_date = article_date.split(" ")
    # Se la lunghezza è 2, significa che l'anno è il presente (2020)
    if len(article_date) == 2:
        month = month_string_to_number(article_date[0])
        day = int(article_date[1])
        year = 2020
    #     Se la lunghezza è 3, significa che si ha l'anno nella data
    elif len(article_date) == 3:
        if article_date[1] == 'minutes':
            return(datetime.now().strftime("%Y-%m-%d"))
        elif article_date[1] == 'hour' or article_date[1] == 'hours':
            return(datetime.now().strftime("%Y-%m-%d"))
        else:
            month = month_string_to_number(article_date[0])
            day = int(article_date[1][:-1])
            year = int(article_date[2])
    #     Se falliscono entrambi, booh
    else:
        logging.warning("Some error in the date occured")
        return("")
    #     I dati vengono salvati usando il formato datetime
    return(date(year, month, day).__str__())


def find_title(article = None):
    try:
        return(article.find_element_by_xpath("./div/div[2]/div/a/h4").text.strip())
    except:
        logging.warning("Could not find article title")
        return("")

def scrape_search_page_result(articles_list = None):
    df_results = pd.DataFrame()

    df_results["Title"] = [find_title(article = article)
                           for article in articles_list]
#
#   !!! PULIRE LE DATE !!!
#
    df_results["Date"] = [find_date(article = article)
                           for article in articles_list]

    df_results["Links"] = [find_links(article = article)
                           for article in articles_list]

    df_results["Summary"] = [find_summary(article = article)
                           for article in articles_list]

    df_results["Category"] = [find_category(article = article)
                            for article in articles_list]
#
#    !!! Questo è provvisorio: bisogna fare una regex per separare gli autori !!!
#
    df_results["Authors"] = [find_authors(article = article)
                            for article in articles_list]
    return df_results


def scrape_article_paragraphs(link = None):
    # Andiamo a scaricare, con la funzione `re.get`, le varie pagine dell'articolo
    #     Usiamo re perché `re.get` perché ti scarica tutto l'html
    html_page = re.get(link)
#     Passo la pagina html dentro BeautifulSoup in maniera tale da poter
#     cercare elementi
    soup = bs(html_page.text, 'html.parser')
#     Cerco i vari box dei paragrafi
    story_bodies = soup.find_all('div', {"class": 'StoryBodyCompanionColumn'})
    pars = []
    pars_tits = []
    for story_body in story_bodies:
#         Cerco tutti i paragrafi in questa story
        paragraphs = story_body.find_all('p', {"class": 'css-158dogj evys1bk0'})
        for paraghraph in paragraphs:
            pars.append(paraghraph.text.strip())
#       Qua cerca i titoletti dei paragrafi
#         Mettiamo try perché potrebbe non trovare nessun titoletto nella story
#         e quindi darebbe errore.
        try:
            paragraphs_titles = story_body.find_all('div')
            for paragraphs_title in paragraphs_titles:
                pars_tits.append(paragraphs_title.find_next('h2').text.strip())
        except:
            logging.warning("No paragraph title in this story body")
    return (pars, pars_tits)


def scrape_articles(df_results = None):
    final_results_dicts = []
    TIME = 0
    for i, link in enumerate(df_results["Links"]):
        try:
            START = time()
            paragraphs, paragraphs_titles = scrape_article_paragraphs(link = link)

            final_results_dicts.append({
                "Title": df_results.iloc[i]["Title"],
                "Date": df_results.iloc[i]["Date"],
                "Link": df_results.iloc[i]["Links"],
                "Summary": df_results.iloc[i]["Summary"],
                "Authors": df_results.iloc[i]["Authors"],
                "Category": df_results.iloc[i]["Category"],
                "Paragraphs": paragraphs,
                "Paragraphs Title": paragraphs_titles
            })
            END = time()
            TIME = ((END - START)/60 + TIME*(i))/(i+1)
            ETA = TIME * (len(df_results["Links"]) - i)
            if ETA < 1:
                logging.info("Article "+str(i)+"/"+str(len(df_results["Links"]))+". ETA: "+"{:.2f}".format(ETA*60)+" sec.")
            else:
                logging.info("Article "+str(i)+"/"+str(len(df_results["Links"]))+". ETA: "+"{:.2f}".format(ETA)+" min.")
        except:
            logging.warning("Some error occurd on article "+str(i)+". It will be skipped.")
    return(final_results_dicts)

def search_page_results(search_url = None, driver = None, times_button_pressed = 100, SLEEP_TIME = 2, remote = True):

    driver.get(search_url)
    logging.info("Opening Search Page")
    while driver.execute_script("return document.readyState") != 'complete':
        pass
    # Togliamo il robo della privacy
    # Tanto siamo dei piratiii 🏴‍☠️
    if not remote:
        logging.info("Pressing cookies button")
        cookie_button = driver.find_element_by_xpath("""
        //*/button[@aria-label='Button to collapse the message']
                                            """)
        cookie_button.click()
        logging.info("Cookies button pressed")

    try:
        press_more_button(driver = driver,
                        times_button_pressed = times_button_pressed,
                        SLEEP_TIME = SLEEP_TIME)
    except:
        logging.warning("I can't press the <SHOW MORE> button. Maybe there is cookie in the way.")
        logging.info("Pressing cookies button")
        cookie_button = driver.find_element_by_xpath("""
        //*/button[@aria-label='Button to collapse the message']
                                            """)
        cookie_button.click()
        logging.info("Cookies button pressed")
        press_more_button(driver = driver,
                        times_button_pressed = times_button_pressed,
                        SLEEP_TIME = SLEEP_TIME)

    # Prendo la posizione del risultato di ricerca. Questo box contiene tutti i risultati che cerco
    search_result_position = driver.find_element_by_xpath("//*[@data-testid='search-results']")

    # Vado a prendere la posizione dei box che contengono gli articoli
    # La parentesi quadra [] nel xpath indica che prendi l'elementi che ha tag `li`
    # ma con una certa caratteristica. L'@ ti dice il nome della caratteristica che vuoi specificare
    articles = search_result_position.find_elements_by_xpath("./li[@data-testid='search-bodega-result']")
    # Da ogni box singolo io vado a prendere i vari elementi che mi servono, tipo titolo
    logging.info("Scraping search results")

    df_results = scrape_search_page_result(articles_list = articles)
    logging.info("Appending preliminary scraped data.")
    with open("./scraping_data_preliminary/NYTimes_cannon_prel.csv", 'a') as file:
        df_results.to_csv(file, header=False)
    return(df_results)


def main():
    # coloredlogs.install()
    logging.basicConfig(filename='./logs/log_NYTimes_cannon.log', level=logging.INFO)
    logging.info("\n\n")
    with open("./config.yml", 'r') as file:
        config_var = safe_load(file)["nytimes_cannon"]
     # Start Chrome
    chrome_options = Options()
    # Questa opzione fa sì che non vada ad aprirsi fisicamente il browser
    # Ti consiglio di scommenterla solamente una volta cher hai fatto
    # bene il codice e non ti serve più vedere.
    # Se metti l'opzione ti aiuta a risparmiare un pochettino di tempo, ma non tanto
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--lang=en-us')
    driver = webdriver.Chrome(executable_path=os.path.abspath("./chromedriver"),
                              options=chrome_options)
    logging.info("Webdriver loaded")
    # Ingrandisci la schermata
    driver.maximize_window()
    logging.info("Maximing window")

    df_results = pd.DataFrame({"Title": "dummy",
                    "Date": config_var['end_date'],
                    "Links": "dummy",
                    "Summary": "dummy",
                    "Category": "dummy",
                    "Authors": "dummy"}, index=[0])

    error_count = 0
    while(int(datetime.strptime(str(df_results["Date"].iloc[-1]), "%Y-%m-%d").strftime("%Y%m%d")) > int(config_var["start_date"])):
        prev_search = df_results["Date"].iloc[-1]
        logging.info("Scraping now with end date: "+str(prev_search))
        # Sometimes in crashes for some reason.
        # Using a try, will try to avoid said problem.
        try:
            df_results = df_results.append(search_page_results(search_url = config_var["search_url_first_part"]+
                                                                datetime.strptime(str(df_results["Date"].iloc[-1]), "%Y-%m-%d").strftime("%Y%m%d")+
                                                                config_var["search_url_second_part"]+
                                                                str(config_var["start_date"])+
                                                                config_var["search_url_third_part"],
                                                driver = driver,
                                                times_button_pressed = config_var["time_button_pressed"],
                                                SLEEP_TIME = config_var["sleep_time"],
                                                remote = config_var["remote"]))
        except:
            error_count += 1
            logging.error("Some problem occurd on this date. Will try again.")
        # If the last date in the page is the same as the previous page
        # it will change the date by one day.
        if str(df_results["Date"].iloc[-1]) == str(prev_search):
            logging.warning("Changing manually date.")
            df_results["Date"].iloc[-1] = (datetime.strptime(str(df_results["Date"].iloc[-1]), "%Y-%m-%d") - timedelta(days = 1)).strftime("%Y-%m-%d")

    logging.info("Saving search results to csv")
    #Salva il Dataframe in un csv
    with open("scraping_data_without_paragraphs/"+str(config_var['filename'])+".csv", 'w') as file:
        df_results.to_csv(file)

    logging.info("Scraping article text")
    final_results_dicts = scrape_articles(df_results = df_results)

    logging.info("Saving final results to json file")


    with open("scraping_data/"+str(config_var['filename'])+".json", 'w') as file:
        json_output = json.dumps(final_results_dicts)
        file.write(json_output)

    driver.quit()
    logging.info("Program Completed")

if __name__ == "__main__":
    main()
