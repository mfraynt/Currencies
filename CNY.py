from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import Select
import os
import pandas as pd
from datetime import datetime as dt, timedelta as td
import ConnectSQLdb
from ConnectSQLdb import cnx, cursor, record
import time

def load_webpage(url):
    try:
        options = Options()
        options.binary_location = r'C:\Users\Fraynt\AppData\Local\Mozilla Firefox\firefox.exe'

        driver = webdriver.Firefox(options=options)
        driver.get(url)
        return driver
    except Exception as e:
        print(e)
        driver.quit()
        raise SystemExit

def pick_data(driver):
    #Dates from 01.01 till today
    start_date = driver.find_element(By.ID, 'ccpr-his-start-date-day')
    end_date = end_date = driver.find_element(By.ID, 'ccpr-his-end-date-day')

    
    s_script = "arguments[0].value = '01 Jan 2022'"

    #Check dates in DB
    get_date = ("SELECT MAX(DATE) FROM CURRENCIES "
                    "WHERE SOURCE = 'CFETS'")
    cursor.execute(get_date)
    try:
        max_date = cursor.fetchall()[0][0].strftime('%d %b %Y')
        s_script = f"arguments[0].value = '{max_date}'"
    except:
        pass
        
    e_script = f"arguments[0].value = '{dt.today().strftime('%d %b %Y')}'"
    driver.execute_script(s_script, start_date)
    driver.execute_script(e_script, end_date)

    #Currencies
    driver.find_element(By.ID, 'ccpr-curr-day').click()
    driver.find_element(By.XPATH,"//label[text()='USD/CNY']").click()
    driver.find_element(By.XPATH,"//label[text()='CNY/RUB']").click()

    #Search
    driver.find_element(By.XPATH,"//a[text()='Search']").click()

    #Download
    driver.execute_script("downLoadHis_day();")

def get_file_path():
    downloads = r"C:/Users/Fraynt/Downloads"
    files = os.listdir(downloads)
    for f in range(0, len(files)):
        files[f] = downloads + "/" + files[f]

    files.sort(key = lambda x: os.path.getmtime(x))
    return(files[len(files)-1])

def record_CNY(file):
    add_curr = ("INSERT IGNORE INTO CURRENCIES "
            "(DATE, CURRENCY, NOMINAL, VALUE, SOURCE) "
            "VALUES (%s, %s, %s, %s, %s)")
    
    df = pd.read_excel(file, engine='openpyxl')
    df = df[0:len(df)-2]
    df.Date = pd.to_datetime(df.Date).dt.date
    for i in range(len(df)):
        print(i)
        row = df.iloc[i]
        DATE = row.Date
        CURRENCY = 'USD/CNY'
        NOMINAL = 1
        VALUE = row[CURRENCY]
        SOURCE = 'CFETS'
        entry = (DATE, CURRENCY, NOMINAL, VALUE, SOURCE)
        record(add_curr, entry)
            
            
        CURRENCY = 'CNY/RUB'
        VALUE = row[CURRENCY]
        entry = (DATE, CURRENCY, NOMINAL, VALUE, SOURCE)
        record(add_curr, entry)

    cnx.commit()    

 
if (__name__ == "__main__"):
    China_url = 'https://iftp.chinamoney.com.cn/english/bmkcpr/index.html?tab=2'
    driver = load_webpage(China_url)
    pick_data(driver)   
    record_CNY(get_file_path())
    driver.quit()
    
