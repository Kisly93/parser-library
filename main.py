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
    title_tag = soup.find('h1')
    title_text = title_tag.text.strip()
    split_title = title_text.split(" :: ")
    title = split_title[0].strip()
    author = split_title[1].strip()

    img_container = soup.find('div', class_='bookimage')
    if img_container is None:
        img_url = None
    else:
        relative_url = img_container.find('img')['src']
        url = "https://tululu.org/"
        img_url = urljoin(url, relative_url)

    genres = soup.find('span', class_='d_book').find_all('a')
    genre_text = [genre.text.strip() for genre in genres]

    comments = soup.find_all('div', class_='texts')
    comment_texts = [comment.span.text.strip() for comment in comments]

    book_data = {
        'title': title,
        'author': author,
        'img_url': img_url,
        'genres': genre_text,
        'comments': comment_texts
    }

    return book_data


def main():
    base_url = "https://tululu.org/b"
    parser = argparse.ArgumentParser(description='Download books from Tululu.org')
    parser.add_argument('start_id', type=int, help='Starting book ID')
    parser.add_argument('end_id', type=int, help='Ending book ID')
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id + 1):
        try:
            book_url = f"{base_url}{book_id}/"
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response, book_url)
            book_data = parse_book_page(response.content)
            print(book_data)
            book_title = book_data['title']
            book_img = book_data['img_url']
            filename = f"{book_id}.{book_title}"
            download_txt(book_url, filename)
            download_image(book_img)
            print(f"Книга '{book_title}' и обложка скачаны успешно.")
            print("Автор:", book_data['author'])
            print("Жанры:", book_data['genres'])
            print("Коментарии", book_data['comments'])
            print()

        except requests.exceptions.HTTPError as error:
            url = f"{base_url}{book_id}/"
            print(f"На странице {url} книга не найдена.")


if __name__ == '__main__':
    main()
