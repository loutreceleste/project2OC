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
        tag = soup.findAll('li')[1:][2:]  # Excluding the first and second line.
        for li in tag:
            a = li.find('a')
            if a is not None:  # Choosing with an available link in 'a'.
                link = a.get('href')
                if 'books' in link:
                    links.append(f'http://books.toscrape.com/{link}')
        return links


# Retrieve all url category

def retrieve_all_category_urls():
    category_books_urls = retrieve_category_books_links()
    updated_category_books_url = {}  # Making a dict

    for url in category_books_urls:
        req = requests.get(url)
        if req.ok:
            category_name = url.split('/')[-2]  # Creating the keys names.
            soup = BeautifulSoup(req.content, "html.parser")
            updated_category_books_url[category_name] = [url]
            if soup.find('li', class_='current') is None:
                pass
            else:
                pagination = soup.find('li', class_='current').text
                cleaned_pagination = pagination.replace(' ', '').replace('\n', '')[-1]  # Extracting the number of pages.
                for index in range(2, int(cleaned_pagination) + 1):  # Starting at the second page.
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
                        new_url = f'http://books.toscrape.com/catalogue/{href}'  # Making all links.
                        new_urls.append(new_url)
        books_links[categories] = new_urls  # Replacing all links in dict.
    return books_links


# Retrieve book informations


# Retrieve book url


def extract_product_page_url(soup):
    for link in soup.findAll('img'):
        src = link.get("src")[0]
        if src:
            src = requests.compat.urljoin(url, src)  # Recreating the urls from each book.
    return f'{src}index.html'


# Retrieve book UPC


def extract_universal_product_code(soup):
    upc = soup.select_one('td')
    return upc.text


# Retrieve book title


def extract_title(soup):
    titles = soup.find_all('h1')[0]  # Taking only the first 'h1'.
    return titles.text


# Retrieve book price (incl.tax)


def extract_price_including_tax(soup):
    price = soup.select('td')[3]  # Only taking the 4 one in 'td'.
    return price.text


# Retrieve book price (excl.tax)


def extract_price_excluding_tax(soup):
    cost = soup.select('td')[2]  # Only taking the 3 one in 'td'.
    return cost.text


# Retrieve book availability


def extract_number_available(soup):
    all = soup.findAll('td')[5]  # Only taking the 6 'td'.
    dispo = (all.text[10:12])
    return dispo


# Retrieve book description


def extract_product_description(soup):
    desc = soup.findAll('p')[3]  # Only taking the 2 one in 'p'.
    return desc.text


# Retrieve book category


def extract_group(soup):
    cat = soup.findAll('a')[3]  # Only taking the 4 one ini 'a'.
    return cat.text


# Retrieve book rate


def extract_ranking(soup):
    note = soup.findAll('p', class_='star-rating')[0]['class'][1]  # Taking only the 2 part of the text.
    notes = {'One': '1', 'Two': '2', 'Three': '3', 'Four': '4', 'Five': '5'}
    return notes[note]


# Retrieve book image
def extract_picture(soup):
    for pic in soup.findAll('img', class_=()):
        image = pic.get("src")
        if image:
            image = requests.compat.urljoin(url, image)  # Reconstitution of the url with requests.compat.urljoin.
            return image


# Retrieve all informations and create the csv fields

data_folder = 'data'
if os.path.isdir('data'):
    print('Directory data is already created. skipping...')  # Searching if directory already exist.
else:
    os.makedirs(data_folder)  # Creating the folder

fields = ['product_page_url', ' universal_ product_code (upc)', 'title', ' price_including_tax', 'price_excluding_tax',
          'number_available', 'product_description', 'category', 'review_rating', 'image_url']

data = retrieve_all_ulr_all_books()

for categories, urls in data.items():
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
if os.path.isdir('images'):
    print('Directory images is already created. skipping...')  # Searching if directory already exist.
else:
    os.makedirs(image_folder)

for categories, urls in data.items():
    for url in urls:
        req = requests.get(url)
        if req.ok:
            soup = BeautifulSoup(req.content, "html.parser")
            image_urls = extract_picture(soup)
            filename = image_urls.split('/')[-1]  # Create the images names.
            image_path = os.path.join(image_folder, filename)
            with open(image_path, 'wb') as img_file:
                img_file.write(requests.get(image_urls).content)
