import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlsplit
import argparse


def download_txt(book_url, filename, folder='books/'):
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response, book_url)
    sanitized_filename = sanitize_filename(filename, platform='auto')
    filepath = os.path.join(folder, sanitized_filename + '.txt')
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(response.text)
    print(filepath)
    return filepath


def download_image(book_url, folder='images/'):
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response, book_url)
    parsed_url = urlsplit(book_url)
    unquoted_filename = unquote(parsed_url.path.split('/')[-1])
    sanitized_filename = sanitize_filename(unquoted_filename, platform='auto')

    filepath = os.path.join(folder, sanitized_filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def check_for_redirect(response, book_url):
    if response.url != book_url:
        raise requests.exceptions.HTTPError("An HTTP error occurred")


def parse_book_page(content):
    soup = BeautifulSoup(content, 'lxml')
    title_element = soup.find('h1')
    title_text = title_element.text.strip()
    title_parts = title_text.split(" :: ")
    title = title_parts[0].strip()
    author = title_parts[1].strip()

    book_image_container = soup.find('div', class_='bookimage')
    if book_image_container is None:
        img_url = None
    else:
        img_relative_url = book_image_container.find('img')['src']
        url = "https://tululu.org/"
        img_url = urljoin(url, img_relative_url)

    genre_elements = soup.find('span', class_='d_book').find_all('a')
    genre_text = [genre.text.strip() for genre in genre_elements]

    comment_elements = soup.find_all('div', class_='texts')
    comment_texts = [comment.span.text.strip() for comment in comment_elements]

    book_information = {
        'title': title,
        'author': author,
        'img_url': img_url,
        'genres': genre_text,
        'comments': comment_texts
    }

    return book_information


def main():
    url_properties = "https://tululu.org/b"
    base_url = "https://tululu.org/txt.php?id="
    parser = argparse.ArgumentParser(description='Скачать книги с сайта Tululu.org')
    parser.add_argument('start_id', type=int, nargs='?', default=1, help='ID начальной книги (по умолчанию: 1)')
    parser.add_argument('end_id', type=int, nargs='?', default=10, help='ID конечной книги (по умолчанию: 10)')
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id + 1):
        try:
            book_url_properties = f"{url_properties}{book_id}/"
            book_url = f"{base_url}{book_id}/"
            response = requests.get(book_url_properties)
            response.raise_for_status()
            check_for_redirect(response, book_url_properties)
            book_information = parse_book_page(response.content)
            print(book_information)
            book_title = book_information['title']
            book_img = book_information['img_url']
            filename = f"{book_id}.{book_title}"
            download_txt(book_url, filename)
            download_image(book_img)
            print(f"Книга '{book_title}' и обложка скачаны успешно.")
            print("Автор:", book_information['author'])
            print("Жанры:", book_information['genres'])
            print("Коментарии", book_information['comments'])
            print()

        except requests.exceptions.HTTPError as error:
            book_url = f"{base_url}{book_id}/"
            print(f"На странице {book_url} книга не найдена.")


if __name__ == '__main__':
    main()
