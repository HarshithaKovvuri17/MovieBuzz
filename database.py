"""
Database Management Module for MovieBuzz Application
Uses SQLite3 to store user credentials, movies, and user reviews.
Stores 'movie_name' directly in the reviews table for clean database querying.
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "movie_reviews.db")

def get_db_connection():
    """Returns a SQLite3 connection with Row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables, updates schema to include movie_name in reviews, and populates movies."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Movies Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_name TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            poster_url TEXT NOT NULL,
            description TEXT,
            genre TEXT,
            release_period TEXT NOT NULL,
            release_year INTEGER DEFAULT 2026
        )
    """)

    # Reviews Table (stores movie_name directly)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            movie_name TEXT NOT NULL DEFAULT '',
            review_text TEXT NOT NULL,
            sentiment TEXT NOT NULL CHECK(sentiment IN ('positive', 'negative')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
    """)
    conn.commit()

    # Ensure movie_name column exists in reviews table
    cursor.execute("PRAGMA table_info(reviews)")
    columns = [col["name"] for col in cursor.fetchall()]
    if "movie_name" not in columns:
        cursor.execute("ALTER TABLE reviews ADD COLUMN movie_name TEXT NOT NULL DEFAULT ''")
        conn.commit()

    # Backfill movie_name for existing reviews from movies table
    cursor.execute("""
        UPDATE reviews 
        SET movie_name = (SELECT title FROM movies WHERE movies.id = reviews.movie_id)
        WHERE movie_name IS NULL OR movie_name = ''
    """)
    conn.commit()

    # 1. Seed Regular User "DP" with Password "DP"
    cursor.execute("SELECT * FROM users WHERE username = ?", ("DP",))
    if not cursor.fetchone():
        dp_hash = generate_password_hash("DP")
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 0)",
            ("DP", dp_hash)
        )
        conn.commit()

    # 2. Seed Single Admin User "admin" with Password "admin"
    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        admin_hash = generate_password_hash("admin")
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
            ("admin", admin_hash)
        )
        conn.commit()

    # 3. User-specified Telugu Movie List (12 Movies)
    all_user_movies = [
        {
            "code_name": "Movie 1",
            "title": "Sathi Leelavathi",
            "poster_url": "/static/images/sathi_leelavathi.png",
            "description": "A hilarious comedy-romance starring Lavanya Tripathi and Dev Mohan.",
            "genre": "Comedy / Romance",
            "release_period": "May 8, 2026",
            "release_year": 2026
        },
        {
            "code_name": "Movie 2",
            "title": "Peddi",
            "poster_url": "/static/images/peddi.png",
            "description": "Directed by Buchi Babu Sana & starring Ram Charan, Janhvi Kapoor, and Shiva Rajkumar.",
            "genre": "Action / Rustic Drama",
            "release_period": "June 4, 2026",
            "release_year": 2026
        },
        {
            "code_name": "Movie 3",
            "title": "Kotha Malupu",
            "poster_url": "/static/images/kotha_malupu.png",
            "description": "Starring Akash Goparaju and Bhairavi Ardhya in a gripping romance mystery.",
            "genre": "Romance / Thriller",
            "release_period": "June 12, 2026",
            "release_year": 2026
        },
        {
            "code_name": "Movie 4",
            "title": "Police Complaint",
            "poster_url": "/static/images/police_complaint.png",
            "description": "Starring Varalaxmi Sarathkumar and Naveen Chandra in a gritty crime investigation thriller.",
            "genre": "Crime / Investigation Thriller",
            "release_period": "June 12, 2026",
            "release_year": 2026
        },
        {
            "code_name": "Movie 5",
            "title": "Sing Geetham",
            "poster_url": "/static/images/sing_geetham.png",
            "description": "A musical journey told through songs, directed by veteran filmmaker Singeetam Srinivasa Rao.",
            "genre": "Musical / Drama",
            "release_period": "June 12, 2026",
            "release_year": 2026
        },
        {
            "code_name": "Movie 6",
            "title": "Maa Inti Bangaaram",
            "poster_url": "/static/images/maa_inti_bangaaram.png",
            "description": "Created by Raj Nidimoru & directed by B. V. Nandini Reddy, starring Samantha and Gulshan Devaiah.",
            "genre": "Family Drama / Comedy",
            "release_period": "June 19, 2026",
            "release_year": 2026
        },
        {
            "code_name": "Movie 7",
            "title": "Nagabandham",
            "poster_url": "/static/images/nagabandham.png",
            "description": "An epic socio-fantasy mystery surrounding ancient snake-god treasures.",
            "genre": "Socio-Fantasy / Action",
            "release_period": "July 3, 2026",
            "release_year": 2026
        },
        {
            "code_name": "Movie 8",
            "title": "Rao Bahadur",
            "poster_url": "/static/images/rao_bahadur.png",
            "description": "Starring Satyadev, written & directed by Venkatesh Maha.",
            "genre": "Period Satire / Drama",
            "release_period": "July 3, 2026",
            "release_year": 2026
        },
        {
            "code_name": "Movie 9",
            "title": "Lenin",
            "poster_url": "/static/images/lenin.png",
            "description": "Action-drama starring Akhil Akkineni and Bhagyashri Borse.",
            "genre": "Action / Drama",
            "release_period": "July 10, 2026",
            "release_year": 2026
        },
        {
            "code_name": "Movie 10",
            "title": "Oh..! Sukumari",
            "poster_url": "/static/images/oh_sukumari.png",
            "description": "Starring Thiruveer and Aishwarya Rajesh in a romantic fantasy comedy.",
            "genre": "Romance / Fantasy Comedy",
            "release_period": "July 17, 2026",
            "release_year": 2026
        },
        {
            "code_name": "Movie 11",
            "title": "Chennai Love Story",
            "poster_url": "/static/images/chennai_love_story.png",
            "description": "Starring Sri Gouri Priya & Kiran Abbavaram; music by Mani Sharma.",
            "genre": "Romance / Musical Drama",
            "release_period": "July 25, 2026",
            "release_year": 2026
        },
        {
            "code_name": "Movie 12",
            "title": "Srinivasa Mangapuram",
            "poster_url": "/static/images/srinivasa_mangapuram.png",
            "description": "Starring Rasha Thadani and V.K. Naresh in a lighthearted family entertainer.",
            "genre": "Family Entertainer / Comedy",
            "release_period": "July 30, 2026",
            "release_year": 2026
        }
    ]

    for m in all_user_movies:
        cursor.execute("SELECT id FROM movies WHERE code_name = ? OR title = ?", (m["code_name"], m["title"]))
        row = cursor.fetchone()
        if not row:
            cursor.execute("""
                INSERT INTO movies (code_name, title, poster_url, description, genre, release_period, release_year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (m["code_name"], m["title"], m["poster_url"], m["description"], m["genre"], m["release_period"], m["release_year"]))
        else:
            cursor.execute("""
                UPDATE movies SET code_name=?, title=?, poster_url=?, description=?, genre=?, release_period=?, release_year=?
                WHERE id=?
            """, (m["code_name"], m["title"], m["poster_url"], m["description"], m["genre"], m["release_period"], m["release_year"], row["id"]))
    
    conn.commit()
    conn.close()

# User Auth Queries
def create_user(username, password, is_admin=0):
    """Registers a new user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        pw_hash = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)", (username, pw_hash, is_admin))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"id": user_id, "username": username, "is_admin": is_admin}, None
    except sqlite3.IntegrityError:
        conn.close()
        return None, "Username already exists. Please choose another or login."
    except Exception as e:
        conn.close()
        return None, str(e)

def verify_user(username, password):
    """Verifies username and password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row and check_password_hash(row["password_hash"], password):
        return {
            "id": row["id"],
            "username": row["username"],
            "is_admin": bool(row["is_admin"])
        }
    return None

# Movie Queries
def get_all_movies_with_stats():
    """Fetches all movies along with positive and negative review counts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            m.id, 
            m.code_name, 
            m.title, 
            m.poster_url, 
            m.description, 
            m.genre, 
            m.release_period,
            m.release_year,
            COUNT(CASE WHEN r.sentiment = 'positive' THEN 1 END) AS positive_count,
            COUNT(CASE WHEN r.sentiment = 'negative' THEN 1 END) AS negative_count,
            COUNT(r.id) AS total_reviews
        FROM movies m
        LEFT JOIN reviews r ON m.id = r.movie_id
        GROUP BY m.id
        ORDER BY m.id ASC
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "code_name": r["code_name"],
            "title": r["title"],
            "poster_url": r["poster_url"],
            "description": r["description"],
            "genre": r["genre"],
            "release_period": r["release_period"],
            "release_year": r["release_year"],
            "positive_count": r["positive_count"],
            "negative_count": r["negative_count"],
            "total_reviews": r["total_reviews"]
        })
    return result

def add_review(user_id, movie_id, review_text, sentiment):
    """Inserts a new review into database, storing movie_name directly in reviews table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get movie_name (title) for the given movie_id
    cursor.execute("SELECT title FROM movies WHERE id = ?", (movie_id,))
    row = cursor.fetchone()
    movie_name = row["title"] if row else f"Movie #{movie_id}"

    cursor.execute("""
        INSERT INTO reviews (user_id, movie_id, movie_name, review_text, sentiment)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, movie_id, movie_name, review_text, sentiment))
    conn.commit()
    review_id = cursor.lastrowid
    conn.close()
    return review_id

def get_movie_reviews(movie_id):
    """Fetches recent reviews for a given movie."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, r.movie_name, r.review_text, r.sentiment, r.created_at, u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.movie_id = ?
        ORDER BY r.created_at DESC
        LIMIT 10
    """, (movie_id,))
    rows = cursor.fetchall()
    conn.close()

    reviews = []
    for r in rows:
        reviews.append({
            "id": r["id"],
            "username": r["username"],
            "movie_name": r["movie_name"],
            "review_text": r["review_text"],
            "sentiment": r["sentiment"],
            "created_at": r["created_at"]
        })
    return reviews

# Admin Database Queries
def get_all_users_admin():
    """Fetches all registered users with their review count."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            u.id, 
            u.username, 
            u.is_admin, 
            u.created_at,
            COUNT(r.id) as review_count
        FROM users u
        LEFT JOIN reviews r ON u.id = r.user_id
        GROUP BY u.id
        ORDER BY u.id ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{
        "id": r["id"],
        "username": r["username"],
        "is_admin": bool(r["is_admin"]),
        "created_at": r["created_at"],
        "review_count": r["review_count"]
    } for r in rows]

def get_all_reviews_admin():
    """Fetches all reviews for the Admin Portal using movie_name stored in database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            r.id, 
            r.movie_name,
            r.review_text, 
            r.sentiment, 
            r.created_at,
            u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{
        "id": r["id"],
        "username": r["username"],
        "movie_title": r["movie_name"],
        "movie_code": r["movie_name"],
        "review_text": r["review_text"],
        "sentiment": r["sentiment"],
        "created_at": r["created_at"]
    } for r in rows]

def delete_review_admin(review_id):
    """Deletes a review by ID (Admin command)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()
    return True

def get_admin_stats():
    """Fetches overall system statistics for Admin Dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM movies")
    total_movies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews WHERE sentiment = 'positive'")
    total_positive = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews WHERE sentiment = 'negative'")
    total_negative = cursor.fetchone()[0]

    conn.close()
    return {
        "total_users": total_users,
        "total_movies": total_movies,
        "total_reviews": total_reviews,
        "total_positive": total_positive,
        "total_negative": total_negative
    }
