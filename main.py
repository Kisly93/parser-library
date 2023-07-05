import requests
import os


base_url = "https://tululu.org/txt.php?id="

def get_file_name(book_id):
    file_name = f"id{book_id}.txt"
    return file_name

def save_books(book_id):
    os.makedirs('books', exist_ok=True)
    url = base_url + str(book_id)
    response = requests.get(url)
    check_for_redirect(response, url)
    response.raise_for_status()
    filename = get_file_name(book_id)
    with open(f'books/{filename}', 'wb') as file:
        file.write(response.content)

def check_for_redirect(response, url):
    if response.url != url:
        raise requests.exceptions.HTTPError("An HTTP error occurred")

def main():
    for book_id in range(1, 11):
        try:
            save_books(book_id)
        except requests.exceptions.HTTPError as error:
            url = base_url + str(book_id)
            print(f"на странице {url} книга не найдена")

if __name__ == '__main__':
    main()