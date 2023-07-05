import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlsplit

base_url = "https://tululu.org/b"


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response, url)
    sanitized_filename = sanitize_filename(filename, platform='auto')
    filepath = os.path.join(folder, sanitized_filename + '.txt')
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(response.text)

    return filepath


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response, url)
    parsed_url = urlsplit(url)
    unquoted_filename = unquote(parsed_url.path.split('/')[-1])
    sanitized_filename = sanitize_filename(unquoted_filename, platform='auto')

    filepath = os.path.join(folder, sanitized_filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def get_book_title_and_img(book_id):
    book_url = f"{base_url}{book_id}/"
    response = requests.get(book_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    title_text = title_tag.text.strip()
    split_title = title_text.split(" :: ")
    img_container = soup.find('div', class_='bookimage')
    if img_container is None:
        return split_title[0].strip(), None
    relative_url = img_container.find('img')['src']
    url = "https://tululu.org/"
    img_url = urljoin(url, relative_url)
    return split_title[0].strip(), img_url


def check_for_redirect(response, url):
    if response.url != url:
        raise requests.exceptions.HTTPError("An HTTP error occurred")


def get_comments(book_id):
    book_url = f"{base_url}{book_id}/"
    response = requests.get(book_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    comments = soup.find_all('div', class_='texts')

    comment_texts = []
    for comment in comments:
        comment_text = comment.span.text.strip()
        comment_texts.append(comment_text)

    return comment_texts


def main():
    for book_id in range(1, 11):
        try:
            book_title, book_img = get_book_title_and_img(book_id)
            filename = f"{book_id}.{book_title}"
            download_txt(f"{base_url}{book_id}/", filename)
            download_image(book_img, filename)
            print(f"Книга '{book_title}' и обложка скачаны успешно.")

            comments = get_comments(book_id)
            if comments:
                print("Комментарии:")
                for comment in comments:
                    print(comment)
                print()
        except requests.exceptions.HTTPError as error:
            url = f"{base_url}{book_id}/"
            print(f"На странице {url} книга не найдена.")


if __name__ == '__main__':
    main()
