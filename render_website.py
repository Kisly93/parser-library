from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server

def render_website():
    with open("downloads/all_books.json", "r") as all_books:
        books_json = all_books.read()

    books = json.loads(books_json)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )

    template = env.get_template('template.html')
    rendered_page = template.render(books=books)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

if __name__ == "__main__":
    render_website()

    server = Server()
    server.watch('template.html', render_website)
    server.serve(root='.')
