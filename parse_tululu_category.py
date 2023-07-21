import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from parser import parse_book_page, download_txt, download_image, check_for_redirect
import argparse
import time
import json


def parse_book_tag(content, url):
    soup = BeautifulSoup(content, 'lxml')
    books_urls = []
    books_tag = soup.select('table.d_book')
    for book_tag in books_tag:
        book_reference = book_tag.select_one('a')['href']
        book_url = urljoin(url, book_reference)
        books_urls.append(book_url)
    return books_urls


def main():
    parser = argparse.ArgumentParser(description='Скачать книги с сайта Tululu.org')
    parser.add_argument('--start_page', type=int, nargs='?', default=1, help='Начальная страница (по умолчанию: 1)')
    parser.add_argument('--end_page', type=int, nargs='?', default=2, help='Конечная страница')
    parser.add_argument('--dest_folder', type=str, default='media', help='Путь к каталогу с результатами парсинга')
    parser.add_argument('--skip_imgs', action='store_true', help='Не скачивать картинки')
    parser.add_argument('--skip_txt', action='store_true', help='Не скачивать книги')
    args = parser.parse_args()

    os.makedirs(args.dest_folder, exist_ok=True)
    book_descriptions = []

    for page_num in range(args.start_page, args.end_page + 1):
        try:
            url = f"https://tululu.org/l55/{page_num}/"
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response, url)
        except requests.exceptions.HTTPError as error:
            print(f"Cтраница {url} не найдена.")
            print()
        except requests.exceptions.ConnectionError as error:
            print(f"Ошибка при установлении соединения: {error}")
            print("Пауза перед следующей попыткой...")
            time.sleep(5)
        for url in parse_book_tag(response.content, url):
            try:
                response = requests.get(url)
                response.raise_for_status()
                check_for_redirect(response, url)
                book_id = url.split("b")[-1].split("/")[0]
                book = parse_book_page(response.content, url, book_id)
                book_title = book['title']
                book_img = book['img_url']
                book_url = book['book_url']
                filename = f"{book_id}.{book_title}"
                if not args.skip_txt:
                    download_txt(book_url, filename, book_id)

                if not args.skip_imgs:
                    download_image(book_img)

                book_descriptions.append(book)

            except requests.exceptions.HTTPError as error:
                print(f'Книга {book_title} отсутствует')
                print()
            except requests.exceptions.ConnectionError as error:
                print(f"Ошибка при установлении соединения: {error}")
                print("Пауза перед следующей попыткой...")
                time.sleep(5)

    with open(os.path.join(args.dest_folder, 'all_books.json'), 'w') as file:
        json.dump(book_descriptions, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
