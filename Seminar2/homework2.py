from bs4 import BeautifulSoup
import requests
import json
from fake_useragent import UserAgent
from pprint import pprint

url = "http://books.toscrape.com/catalogue/" #domain
ua = UserAgent()
headers = {"User-Agent": ua.chrome} # ua.random 
params ={'page' : 1}
session = requests.session()

all_books = []

while True:
    response = session.get(url + f"page-{params['page']}.html") # пагинация
    print(response.status_code)
    if response.status_code != 200:
        break # выходим, если нет следующей страницы
    soup = BeautifulSoup(response.text, 'html.parser')
    books = soup.find_all('article', {'class':'product_pod'})
    
    if not books:
        break
        
    for book in books:
        book_info = {}
        # скрейпим название, цену, количество товара в наличии (In stock (19 available)) в формате integer, описание:
        # название
        name_info = book.find('img', {'class':'thumbnail'})
        book_info['name'] = name_info.get('alt')
        # цена
        price_info = book.find('p', {'class':'price_color'})
        book_info['price'] = float(price_info.getText()[2:])

        # "We need to go deeper" (c) Inception
        url_info = book.find('a', {'title':book_info['name']})
        book_url = url_info.get('href')
        book_response = session.get(url + book_url) # заходим на страничку описания
        if book_response.status_code == 200:
            book_details_soup = BeautifulSoup(book_response.text, 'html.parser')
            # количество товара в наличии
            available_info = int(str(book_details_soup.find('p', {'class': 'instock availability'})).split()[7][1:])
            book_info['available'] = available_info
            # описание
            desc_info = str(book_details_soup.find('p', {'class':None}))
            book_info['desc'] = desc_info

        all_books.append(book_info)
    print(f"обработана {params['page']} страница")
        
    params['page'] += 1

with open('books.json', 'w') as f:   
    print(json.dumps(all_books), file=f)
