# Working with currencies

## ETL procedure

### 1. Extraction

For data extraction time we use web scraping in order to avoid registration for API service. As an example we will be downloading data from [China Foreign Exchange Trade System](https://iftp.chinamoney.com.cn).  

Data is saved to [MySQL](https://www.mysql.com/) database via corresponding [connector pacakge](https://dev.mysql.com/doc/connector-python/en/).

Procedure is quite simple and provided below. 

> 🔌 **Note** For website manipulation [Selenium](https://www.selenium.dev/) package is used. This document will not include instructions on its installation as well as installation of the [Geckodriver](https://github.com/mozilla/geckodriver/releases) for Mozilla.

Data is saved in a simple table: 
| Field    | Type        | Null | Key | Default | Extra          |
|----------|-------------|------|-----|---------|----------------|
| ID       | int         | NO   | PRI | Null    | auto_increment |
| DATE     | date        | YES  | MUL | Null    |                |
| CURRENCY | varchar(20) | YES  |     | Null    |                |
| NOMINAL  | int         | YES  |     | Null    |                |
| VALUE    | float       | YES  |     | Null    |                |
| SOURCE   | varchar(20) | YES  |     | Null    |                |

SQL connection as well as recodr method is described in a separate file called **ConnectSQLdb.py** as follows:

```Python
import mysql.connector
from mysql.connector import errorcode

config = {'user': '  ', # User name should be provided
          'password': '  ', # Password for logging in
          'host': '127.0.0.1', # Here a localhost is specified
          'database': '  ', # DB name shouldb be provided
          'raise_on_warnings': True,
          'use_pure': False}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()


def record(SQLscript, data):
    try:
        cursor.execute(SQLscript, data)
    except mysql.connector.Error as err:
        if err.errno == 1062: # Checking for duplicate values
            print('DUPLICATE VALUE ' + data[0].strftime('%d %b %Y'))
```
Procedure is as follows:  

1.1. We should load the page and return **driver** object:
```Python
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
```
1.2. Page navigation is automated till the point of downloading the file (```def pick_data(driver)``` in **CNY.py**).

1.3. Data is read by **Pandas** and written to the database:

```Python
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
```