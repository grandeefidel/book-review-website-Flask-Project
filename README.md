# Project 1

Web Programming with Python and JavaScript

This is a book review website

application.py has most of the business logic and all the methods that mediates between the templates and database/API.

import.py was used to export the content of books.csv in the database

includes directory contains _message.html file that is used for notifiction using flash package which was installed and imported in application.py

_layout.html file is the layout template of all the pages except index.html and register.html which has layout.html as there layout template.

book.html displays the details of a book

books.html is the page where user can search for books using title, isbn or author of the book.

Index.html is the first page where user is prompted to login or navigate to registration page (register.html) if not registered yet.

User make a GET request to /api/<isbn> route to find JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score.

Static directory contains all my static files.


