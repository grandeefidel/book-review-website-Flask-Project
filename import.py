import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
os.environ['DATABASE_URL'] = 'postgres://nkssorqemavpsn:02bdb2ff87baf1a3b9cfb409b3fe62bde2dac52d6bbda5ae88b860ab6d6d3f42@ec2-54-75-245-196.eu-west-1.compute.amazonaws.com:5432/d9vbvinbvc650v'
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, publication_year) VALUES ( :isbn, :title, :author, :publication_year)",
                    {"isbn": isbn, "title": title, "author": author, "publication_year": year})
        print(f"Added books with title {title} and author {author}.")
    db.commit()

if __name__ == "__main__":
    main()