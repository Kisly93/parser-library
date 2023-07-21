from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server
from more_itertools import chunked
import os

def render_website():
    os.makedirs("pages", exist_ok=True)

    with open("media/all_books.json", "r") as all_books:
        books_json = all_books.read()

    books = json.loads(books_json)
    books_per_page = 10
    pages = list(chunked(books, books_per_page))

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    env.filters['chunked'] = chunked
    template = env.get_template('template.html')

    for _, page in enumerate(pages, start=1):
        rendered_page = template.render(books=page, current_page=_, total_pages=len(pages))

        page_filename = f'pages/index{_}.html'
        with open(page_filename, 'w', encoding="utf8") as file:
            file.write(rendered_page)

    print("Website rendered successfully!")

if __name__ == "__main__":
    render_website()

    server = Server()
    server.watch('template.html', render_website)
    server.serve(root='.')
