import os
import requests
from flask import Flask, session, request, flash, render_template, redirect, url_for,jsonify
from passlib.hash import sha256_crypt
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

os.environ['DATABASE_URL'] = 'postgres://nkssorqemavpsn:02bdb2ff87baf1a3b9cfb409b3fe62bde2dac52d6bbda5ae88b860ab6d6d3f42@ec2-54-75-245-196.eu-west-1.compute.amazonaws.com:5432/d9vbvinbvc650v'
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
   
# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        userdata = db.execute("SELECT * FROM users where email=:username", {"username": username}).fetchone()
        print(f"{userdata}")
        if userdata is None:
            flash("username or password incorrect", "danger")
            return render_template("index.html")
        else:
            passwrd = str(password)
            print(f"{userdata.password}  and {sha256_crypt.encrypt(str(password))}")
            if sha256_crypt.verify(passwrd,userdata.password):
                session["user_id"] = userdata.id
                session["username"] = username
                return redirect(url_for('books'))
            else:
                flash("username or password incorrect", "danger")
                return render_template("index.html")
    # if session.get("comments") is None:
    #     session["comments"] = []
    # comment = "new Comment"
    # session["comments"].append(comment)
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST": 
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")
        if password == confirmPassword:
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            email = request.form.get("username")
            securePass = sha256_crypt.encrypt(str(password))
        #insert user details into the database
            db.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (:first_name, :last_name, :email, :password)",
                    {"first_name": first_name, "last_name": last_name, "email": email, "password": securePass})
            print(f"user {first_name} has been created successfully.")
            db.commit()
            flash("You are registered and can login","success")
            return redirect(url_for('index'))
        else:
        #go back to the registration page and tell the user the the password does not match
            response = 'Passwords does not match'
            flash("password does not match","danger")
            return render_template("register.html", response=response)
    return render_template("register.html")

@app.route("/books", methods=["POST", "GET"])
def books():
    if session.get("user_id") is None:
        return redirect(url_for('index'))
    else:
        if request.method == "POST":
            searchParam = request.form.get("searchWith")
            books = db.execute("SELECT * FROM books WHERE isbn LIKE :searchParam OR title LIKE :searchParam OR author LIKE :searchParam",
            {"searchParam": "%"+searchParam+"%"}).fetchall()
            print(f"books fetched {books} user is {session.get('user_id')}")
            if not books:
                searchResult = True
            else:    
                searchResult = False
            print(f"searchResult: {searchResult}")
            return render_template("books.html", books = books,searchResult=searchResult)
        return render_template("books.html")


@app.route("/book", methods=["POST"])
def book():
    if session.get("user_id") is None:
        return redirect(url_for('index'))
    else:
        usr_id = session.get("user_id")
        bookId = request.form.get("bookId")
        bookDetail = db.execute("SELECT * FROM books WHERE id =:book",
            {"book": bookId}).fetchone()
        print(f"isbn: {bookDetail.isbn}")
        bookReview = db.execute("SELECT * FROM reviews WHERE book_id =:book",
            {"book": bookId}).fetchall()
        if not bookReview:
            noReview = True
        else:    
            noReview = False
        isbn = {bookDetail.isbn}
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "453eA2NbCnFRJVG9Jw5EQ", "isbns": isbn})
        if res.status_code != 200:
            raise Exception("ERROR: request unsuccessful.")
        data = res.json()
        average_rating = data["books"][0]["average_rating"]
        ratings_count = data["books"][0]["ratings_count"]
        print(res.json())
        return render_template("book.html", noReview = noReview, bookDetail= bookDetail, userId= usr_id, average_rating=average_rating, ratings_count=ratings_count, bookReview = bookReview)


@app.route("/postReview", methods=["POST"])
def postReview():
    if session.get("user_id") is None:
        return redirect(url_for('index'))
    else:
        bookId = request.form.get("bookId")
        comment = request.form.get("comment")
        rate = request.form.get("rate")
        usr_id = session.get('user_id')
        bookReview = db.execute("SELECT * FROM reviews WHERE user_id =:userId AND book_id=:book_id",
            {"userId": usr_id, "book_id": bookId}).fetchone()
        print(f"bookReview: {bookReview}")
        if bookReview is None:
            db.execute("INSERT INTO reviews (comment, ratings, user_id, book_id) VALUES (:comment, :ratings, :userId, :book_id)",
                            {"comment": comment, "ratings": rate, "userId": usr_id, "book_id": bookId})
            db.commit()
            flash("review added succesfully","success")
            return redirect(url_for('books'))
        else:
            flash("you cannot submit multiple reviews for one book","danger")
            return redirect(url_for('books'))


@app.route("/api/<isbn>")
def bookApi(isbn):
    if session.get("user_id") is None:
        return redirect(url_for('index'))
    bookDetail = db.execute("SELECT * FROM books WHERE isbn =:isbn",
        {"isbn": isbn}).fetchone()
    print(f"isbn: {bookDetail.isbn}")
    if bookDetail is None:
        return jsonify({"error": "Invalid isbn"}), 422
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "453eA2NbCnFRJVG9Jw5EQ", "isbns": isbn})
    if res.status_code != 200:
        return jsonify({"error": "request unsuccessful"})
    data = res.json()
    print(f"{res}")
    average_rating = data["books"][0]["average_rating"]
    print(f"{average_rating}")
    reviews_count = data["books"][0]["reviews_count"]
    print(f"{reviews_count}")
    return jsonify({
            "title": bookDetail.title,
        "author": bookDetail.author,
        "year": bookDetail.publication_year,
        "isbn": bookDetail.isbn,
        "review_count": reviews_count,
        "average_score": average_rating
        })


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.secret_key = "1234567dailywebcoding"
    app.run(debug= True)