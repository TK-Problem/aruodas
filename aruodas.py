import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import datetime


def get_vilnius_rental_data():
    """
    Reads all rent adds and saves as .csv file
    """
    df = read_all_pages()

    # drop duplicates
    df = df.drop_duplicates()

    fname = "Vilnius_RENT_" + datetime.datetime.now().strftime("%Y-%m-%d_%H_%M") + ".csv"

    df.to_csv(fname, encoding='utf-8')

    print(f"\n done {df.shape[0]} entries found")


def get_vilnius_flat_sale_data():
    """
    Reads all rent adds and saves as .csv file
    """
    df = read_all_pages(rent=False)

    # drop duplicates
    df = df.drop_duplicates()

    fname = "Vilnius_BUY_" + datetime.datetime.now().strftime("%Y-%m-%d_%H_%M") + ".csv"

    df.to_csv(fname, encoding='utf-8')

    print(f"\n done {df.shape[0]} entries found")



def check_if_add(info):
    """
    Input:
        info, bs4 element
    Output:
        returns True if row is not add
    """
    try:
        info.h3.a.get_text(strip=True, separator="-").split("-")
        return True
    except:
        return False


def read_rent_page(soup):
    """
    Input:
        soup: bs4 element, page source
    Output:
        list of list: region, adress, rent price, no of rooms, area (sq. meters), no of floors/total floors and URL
    """
    rows = soup.tbody.findAll("tr", {"class": "list-row"})

    _data = list()

    for row in rows:
        info = row.find("td", {"class": "list-adress"})

        if check_if_add(info):
            region, street = process_info(info)

            price_total = process_price(row)

            no_rooms = row.find("td", {"class": "list-RoomNum"}).text.replace("\n", "").replace(" ", "")
            area = row.find("td", {"class": "list-AreaOverall"}).text.replace("\n", "").replace(" ", "")
            no_floors = row.find("td", {"class": "list-Floors"}).text.replace("\n", "").replace(" ", "")

            url = info.h3.a["href"]

            _data.append([region, street, price_total, no_rooms, area, no_floors, url])

    return _data


def process_info(info):
    """
    Returns region and street.
    """
    address = info.h3.a.get_text(strip=True, separator="-").split("-")
    try:
        region = address[0]
        street = address[1]
        return region, street
    except:
        return np.nan, np.nan


def process_price(row):
    """
    Returns price
    """
    prices = row.find("div", {"class": "price"}).contents

    if len(prices) == 5:
        return prices[1].text[:-2].replace(" ", "")
    elif len(prices) == 7:
        return prices[3].text[:-2].replace(" ", "")
    else:
        return np.nan


def create_df(data):
    """
    Returns pandas DataFrame
    """
    return pd.DataFrame(data, columns=["Region", "Street", "Rent_Price", "No_Of_Rooms",
                                       "Size", "No_Of_Floors", "URL"])


def get_no_of_pages(soup):
    """
    Returns number of pages for rent adds
    """
    return int(soup.find("div", {"class": "pagination"}).findAll("a")[-2].text)


def read_all_pages(rent=True):
    if rent:
        url = "https://en.aruodas.lt/butu-nuoma/vilniuje/?FOrder=AddDate"
        _url = "https://en.aruodas.lt/butu-nuoma/vilniuje/puslapis/"
    else:
        url = "https://en.aruodas.lt/butai/vilniuje/?FOrder=AddDate"
        _url = "https://en.aruodas.lt/butai/vilniuje/puslapis/"

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    no_pages = get_no_of_pages(soup)+1

    _data = read_rent_page(soup)
    _len = len(_data)
    print(f"page {1} found {_len} entries. Total data {len(_data)}")

    for idx in range(2, no_pages):

        url = _url + str(idx) + "/?FOrder=AddDate"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        _ = read_rent_page(soup)
        _len = len(_)
        _data += _
        print(f"page {idx} found {_len} entries. Total data {len(_data)}")

    return create_df(_data)
