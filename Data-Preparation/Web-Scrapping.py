# ============================================================================
# Getting financial data from yahoo finance using webscraping 
# =============================================================================

import requests
from bs4 import BeautifulSoup

income_statement = {}

url = "https://finance.yahoo.com/quote/AAPL/financials?p=AAPL"

headers = {"User-Agent" : "Chrome/96.0.4664.110"}
page = requests.get(url, headers=headers)
page_content = page.content
soup = BeautifulSoup(page_content,"html.parser")
tabl = soup.find_all("div" , {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
for t in tabl:
    rows = t.find_all("div" , {"class": "D(tbr) fi-row Bgc($hoverBgColor):h"})
    for row in rows:
        income_statement[row.get_text(separator="|").split("|")[0]] = row.get_text(separator="|").split("|")[1]

