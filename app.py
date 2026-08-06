"""
Movie Review Web Application - Flask Backend Server
Handles authentication, 10+ Telugu movies, review submissions, and single-admin portal routes.
"""
import os
from flask import Flask, render_template, request, jsonify, session
from database import (
    init_db, create_user, verify_user, get_all_movies_with_stats, 
    add_review, get_movie_reviews, get_all_users_admin, 
    get_all_reviews_admin, delete_review_admin, get_admin_stats
)
from sentiment import analyze_sentiment

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-movie-review-key-12345")

# Initialize SQLite database schema and seed data
init_db()

def is_current_user_admin():
    """Helper to check if current session user is admin."""
    return session.get('is_admin', False)

@app.route("/")
def index():
    """Renders main single-page application for Movie Reviews."""
    return render_template("index.html")

@app.route("/login")
def login_page():
    """Renders standalone Login Page."""
    return render_template("login.html")

@app.route("/register")
@app.route("/signup")
def register_page():
    """Renders standalone Register/Signup Page."""
    return render_template("register.html")

@app.route('/api/me', methods=['GET'])
def get_current_user():
    """Returns currently authenticated user session info."""
    if 'user_id' in session:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": session['user_id'],
                "username": session['username'],
                "is_admin": session.get('is_admin', False)
            }
        })
    return jsonify({"authenticated": False, "user": None})

@app.route('/api/signup', methods=['POST'])
def signup():
    """Handles new user registration."""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400

    user, error = create_user(username, password, is_admin=0)
    if error:
        return jsonify({"success": False, "message": error}), 400

    session['user_id'] = user['id']
    session['username'] = user['username']
    session['is_admin'] = False

    return jsonify({
        "success": True,
        "message": f"Account created successfully! Welcome, {user['username']}.",
        "user": user
    })

@app.route('/api/login', methods=['POST'])
def login():
    """Handles user login."""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400

    user = verify_user(username, password)
    if not user:
        return jsonify({"success": False, "message": "Invalid username or password."}), 401

    session['user_id'] = user['id']
    session['username'] = user['username']
    session['is_admin'] = user['is_admin']

    return jsonify({
        "success": True,
        "message": f"Welcome back, {user['username']}! {'(Admin Mode)' if user['is_admin'] else ''}",
        "user": user
    })

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logs out current user."""
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route('/api/movies', methods=['GET'])
def list_movies():
    """Returns all 10+ Telugu movies with positive/negative review counts and recent reviews."""
    movies = get_all_movies_with_stats()
    for m in movies:
        m['reviews'] = get_movie_reviews(m['id'])
    return jsonify({"success": True, "movies": movies})

@app.route('/api/movies/<int:movie_id>/reviews', methods=['GET'])
def list_movie_reviews(movie_id):
    """Returns recent user reviews for a specific movie."""
    reviews = get_movie_reviews(movie_id)
    return jsonify({"success": True, "reviews": reviews})

@app.route('/api/reviews', methods=['POST'])
def submit_review():
    """Submits a new movie review, performs sentiment analysis, and saves to SQLite."""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "You must be logged in to submit a review."}), 401

    data = request.get_json() or {}
    movie_id = data.get('movie_id')
    review_text = data.get('review_text', '').strip()

    if not movie_id or not review_text:
        return jsonify({"success": False, "message": "Movie ID and review text are required."}), 400

    # Analyze sentiment (positive / negative)
    sentiment = analyze_sentiment(review_text)

    # Save to SQLite database
    review_id = add_review(session['user_id'], movie_id, review_text, sentiment)

    # Fetch updated movies list and stats
    movies = get_all_movies_with_stats()
    
    return jsonify({
        "success": True,
        "message": f"Review submitted! Sentiment detected: {sentiment.upper()}.",
        "sentiment": sentiment,
        "review_id": review_id,
        "movies": movies
    })

# --- Admin Portal Routes ---
@app.route('/api/admin/data', methods=['GET'])
def get_admin_dashboard_data():
    """Fetches all users, reviews, and system stats for single admin."""
    if not is_current_user_admin():
        return jsonify({"success": False, "message": "Unauthorized access. Admin privileges required."}), 403

    stats = get_admin_stats()
    users = get_all_users_admin()
    reviews = get_all_reviews_admin()

    return jsonify({
        "success": True,
        "stats": stats,
        "users": users,
        "reviews": reviews
    })

@app.route('/api/admin/reviews/<int:review_id>', methods=['DELETE'])
def delete_admin_review(review_id):
    """Deletes a review via Admin Portal."""
    if not is_current_user_admin():
        return jsonify({"success": False, "message": "Unauthorized access. Admin privileges required."}), 403

    delete_review_admin(review_id)
    return jsonify({"success": True, "message": f"Review #{review_id} has been deleted."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
