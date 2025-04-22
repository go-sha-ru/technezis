import sqlite3
import os
import logging
import re
import pandas as pd
from pyquery_xpath import PyQuery as pq

from dotenv import load_dotenv

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


load_dotenv()
DB_NAME = os.getenv("DB_NAME")


def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('''
CREATE TABLE IF NOT EXISTS Data (
id INTEGER PRIMARY KEY,
title TEXT NOT NULL,
url TEXT NOT NULL,
xpath TEXT NOT NULL,
price REAL NULL
)                    
                   '''
                   )
    connection.commit()
    connection.close()


def save_data(data: pd.DataFrame, with_price=False):
    if with_price:        
        data['price'] = pd.Series(dtype='float')
        try:
            for index, row in data.iterrows():
                document = pq(url=row['url'])
                price = document.xpath(row['xpath']).text()
                price = price.replace(",", ".")
                price = re.sub(r"[^\.0-9]", "", price)
                price = "".join(price.split())
                data.iloc[[index], [3]] = float(price)
        except Exception as e:
            logger.error(f'Error: {e}')
            print(e)

    connection = sqlite3.connect(DB_NAME)
    data.to_sql('Data', connection, if_exists='replace', index=False)
    connection.commit()
    connection.close()