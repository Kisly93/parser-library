import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlsplit
import argparse
import time
import json


def download_txt(book_url, filename, book_id, folder='books/'):
    params = {'id': book_id}
    response = requests.get(book_url, params=params)
    response.raise_for_status()
    sanitized_filename = sanitize_filename(filename, platform='auto')
    filepath = os.path.join(folder, f'{sanitized_filename}.txt')
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def download_image(book_img, folder='images/'):
    response = requests.get(book_img)
    response.raise_for_status()
    parsed_url = urlsplit(book_img)
    unquoted_filename = unquote(parsed_url.path.split('/')[-1])
    sanitized_filename = sanitize_filename(unquoted_filename, platform='auto')
    filepath = os.path.join(folder, sanitized_filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def check_for_redirect(response, book_properties_url):
    if response.url != book_properties_url:
        raise requests.exceptions.HTTPError("An HTTP error occurred")


def parse_book_page(content, book_properties_url):
    soup = BeautifulSoup(content, 'lxml')
    title_element = soup.select_one('h1')
    title_text = title_element.text.strip()
    title_parts = title_text.split(" :: ")
    title = title_parts[0].strip()
    author = title_parts[1].strip()

    book_properties = soup.select('table.d_book a')

    img = soup.select_one('table.d_book img')['src']

    genre_elements = soup.select('span.d_book a')
    genre_text = [genre.text.strip() for genre in genre_elements]

    comment_elements = soup.select('div.texts')
    comment_texts = [comment.span.text.strip() for comment in comment_elements]

    book = {
        'title': title,
        'author': author,
        'img_url': urljoin(book_properties_url, img),
        'genres': genre_text,
        'comments': comment_texts,
        'book_url': urljoin(book_properties_url, book_properties[-3]['href']),
    }

    return book


def main():
    parser = argparse.ArgumentParser(description='Скачать книги с сайта Tululu.org')
    parser.add_argument('start_id', type=int, nargs='?', default=1, help='ID начальной книги (по умолчанию: 1)')
    parser.add_argument('end_id', type=int, nargs='?', default=10, help='ID конечной книги (по умолчанию: 10)')
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id + 1):
        try:
            book_properties_url = f"https://tululu.org/b{book_id}/"

            response = requests.get(book_properties_url)
            response.raise_for_status()
            check_for_redirect(response, book_properties_url)

            book = parse_book_page(response.content, book_properties_url)
            book_title = book['title']
            book_img = book['img_url']
            book_url = book['book_url']
            filename = f"{book_id}.{book_title}"

            download_txt(book_url, filename, book_id)
            download_image(book_img)

            print(f"Книга '{book_title}' и обложка скачаны успешно.")
            print("Автор:", book['author'])
            print("Жанры:", book['genres'])
            print("Комментарии", book['comments'])
            print()

        except requests.exceptions.HTTPError as error:
            base_url = "https://tululu.org/b"
            url = f"{base_url}{book_id}/"
            print(f"На странице {url} книга не найдена.")
            print()
        except requests.exceptions.ConnectionError as error:
            print(f"Ошибка при установлении соединения: {error}")
            print("Пауза перед следующей попыткой...")
            time.sleep(5)


if __name__ == '__main__':
    main()
