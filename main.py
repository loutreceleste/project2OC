import requests
from bs4 import BeautifulSoup
import csv
import os


# Retrieve all category links

def retrieve_category_books_links():
    req = requests.get('http://books.toscrape.com')
    if req.ok:
        links = []
        soup = BeautifulSoup(req.content, "html.parser")
        tag = soup.findAll('li')[1:][2:]  # En excluant la 1er et 2eme ligne.
        for li in tag:
            a = li.find('a')
            if a is not None:  # Pour choisir les 'a' avec un lien valable.
                link = a.get('href')
                if 'books' in link:
                    links.append(f'http://books.toscrape.com/{link}')
        return links


# Retrieve all url category

def retrieve_all_category_urls():
    category_books_urls = retrieve_category_books_links()
    updated_category_books_url = {}

    for url in category_books_urls:
        req = requests.get(url)
        if req.ok:
            category_name = url.split('/')[-2]
            soup = BeautifulSoup(req.content, "html.parser")
            updated_category_books_url[category_name] = [url]
            if soup.find('li', class_='current') is None:
                pass
            else:
                pagination = soup.find('li', class_='current').text
                cleaned_pagination = pagination.replace(' ', '').replace('\n', '')[-1]
                for index in range(2, int(cleaned_pagination) + 1):
                    updated_category_books_url[category_name] += [url.replace('index', f"page-{index}")]
    return updated_category_books_url


# Retrieve all book links by page

def retrieve_all_ulr_all_books():
    books_links = retrieve_all_category_urls()

    for categories, urls in books_links.items():
        new_urls = []
        for url in urls:
            req = requests.get(url)
            if req.ok:
                soup = BeautifulSoup(req.content, "html.parser")
            for tags in soup.find_all('h3'):
                for h3 in tags:
                    a = tags.find('a')
                    for href in a:
                        href = a['href'].replace('../../../', '')
                        new_url = f'http://books.toscrape.com/catalogue/{href}'
                        new_urls.append(new_url)
        books_links[categories] = new_urls
    return books_links


# Retrieve book informations


# Retrieve book url


def extract_product_page_url(soup):
    for link in soup.findAll('img'):
        src = link.get("src")[0]
        if src:
            src = requests.compat.urljoin(url, src)
    return f'{src}index.html'


# Retrieve book UPC


def extract_universal_product_code(soup):
    upc = soup.select_one('td')
    return upc.text


# Retrieve book title


def extract_title(soup):
    titles = soup.find_all('h1')[0]
    return titles.text


# Retrieve book price (incl.tax)


def extract_price_including_tax(soup):
    price = soup.select('td')[3]
    return price.text


# Retrieve book price (excl.tax)


def extract_price_excluding_tax(soup):
    cost = soup.select('td')[2]
    return cost.text


# Retrieve book availability


def extract_number_available(soup):
    all = soup.findAll('td')[5]
    dispo = (all.text[10:12])
    return dispo


# Retrieve book description


def extract_product_description(soup):
    desc = soup.findAll('p')[3]
    return desc.text


# Retrieve book category


def extract_group(soup):
    cat = soup.findAll('a')[3]
    return cat.text


# Retrieve book rate


def extract_ranking(soup):
    note = soup.findAll('p', class_='star-rating')[0]['class'][1]
    notes = {'One': '1', 'Two': '2', 'Three': '3', 'Four': '4', 'Five': '5'}
    return notes[note]


# Retrieve book image
def extract_picture(soup):
    for pic in soup.findAll('img', class_=()):
        image = pic.get("src")
        if image:
            image = requests.compat.urljoin(url, image)
            return image


# Retrieve all informations and create the csv fields

data_folder = 'data'
os.makedirs(data_folder)

fields = ['product_page_url', ' universal_ product_code (upc)', 'title', ' price_including_tax', 'price_excluding_tax',
          'number_available', 'product_description', 'category', 'review_rating', 'image_url']

data = retrieve_all_ulr_all_books()

for categories, urls in data.items():
    for category in categories:
        with open(os.path.join(data_folder, f'{categories}.csv'), 'w') as fichier_csv:
            writer = csv.writer(fichier_csv, delimiter=',')
            writer.writerow(fields)
            for url in urls:
                req = requests.get(url)
                if req.ok:
                    soup = BeautifulSoup(req.content, "html.parser")
                    product_page_url = extract_product_page_url(soup)
                    upc = extract_universal_product_code(soup)
                    title = extract_title(soup)
                    price_including_tax = extract_price_including_tax(soup)
                    price_excluding_tax = extract_price_excluding_tax(soup)
                    number_available = extract_number_available(soup)
                    product_description = extract_product_description(soup)
                    group = extract_group(soup)
                    review_rating = extract_ranking(soup)
                    image_url = extract_picture(soup)

                    writer.writerow([product_page_url, upc, title, price_including_tax, price_excluding_tax,
                                     number_available, product_description, group, review_rating, image_url])


# Retrieve and save all images in a folder


image_folder = 'images'
os.makedirs(image_folder)

for categories, urls in data.items():
    for url in urls:
        req = requests.get(url)
        if req.ok:
            soup = BeautifulSoup(req.content, "html.parser")
            image_urls = extract_picture(soup)
            filename = image_urls.split('/')[-1]  # Nom du fichier basé sur l'URL
            image_path = os.path.join(image_folder, filename)
            with open(image_path, 'wb') as img_file:
                img_file.write(requests.get(image_urls).content)
