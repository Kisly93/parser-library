import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup

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

def get_book_title(book_id):
    book_url = f"{base_url}{book_id}/"
    response = requests.get(book_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    title_text = title_tag.text.strip()
    split_title = title_text.split(" :: ")
    return split_title[0].strip()
def check_for_redirect(response, url):
    if response.url != url:
        raise requests.exceptions.HTTPError("An HTTP error occurred")
def main():
    for book_id in range(1, 11):
        try:
            book_title = get_book_title(book_id)
            filename = f"{book_id}.{book_title}"
            download_txt(f"{base_url}{book_id}/", filename)
            print(f"Книга '{book_title}' скачана успешно.")
        except requests.exceptions.HTTPError as error:
            url = f"{base_url}{book_id}/"
            print(f"На странице {url} книга не найдена.")


if __name__ == '__main__':
    main()
