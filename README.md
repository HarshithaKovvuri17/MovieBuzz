# MovieBuzz 🎬

A real-time Telugu movie review web application with **RNN-based sentiment analysis**, SQLite3 review storage, and a single-admin management dashboard.

---

## 📌 Features

- 🎥 **12 Featured Telugu Movies** (May–July 2026 releases) with official poster artwork
- 🤖 **AI Sentiment Analysis** using a TensorFlow Keras SimpleRNN model trained on the IMDb dataset
- 🌗 **Light / Dark Theme Toggle** — switch instantly via the ☀️ / 🌙 symbol in the navbar
- 🔒 **User Authentication** — Register, Login, and Logout with session-based auth
- 🖼️ **Split-Screen Movie Detail Modal** — Poster on the left, review submission form and all community reviews on the right
- 📊 **Community Sentiment Stats** — Live positive/negative review counts per movie
- 🛡️ **Admin Portal** — Single admin account to manage users and delete reviews
- 💾 **SQLite3 Database** — All reviews stored locally with `movie_name` directly in the reviews table

---

## 🗂️ Project Structure

```
MovieReview/
├── app.py                  # Flask application & API routes
├── database.py             # SQLite3 schema, seeding & queries
├── sentiment.py            # RNN + lexicon sentiment engine
├── train_model.py          # IMDb dataset downloader & model trainer
├── imdb_sample_dataset.csv # 1,000 decoded sample IMDb reviews (CSV format)
├── rnn_imdb_model.h5       # Trained SimpleRNN model weights
├── imdb_word_index.pkl     # IMDb word-to-index mapping
├── requirements.txt        # Python dependencies
├── movie_reviews.db        # SQLite3 database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css       # Full dark/light theme design system
│   ├── js/
│   │   └── app.js          # Frontend logic (auth, modals, theme toggle)
│   └── images/             # Official movie poster images
└── templates/
    ├── index.html          # Main portal page
    ├── login.html          # Login page
    └── register.html       # Registration page
```

---

## 🤖 Sentiment Model & IMDb Dataset Training

The sentiment engine uses a **TensorFlow Keras SimpleRNN** trained on the IMDb dataset:

```python
model = Sequential([
    Embedding(10000, 32, input_length=200),
    SimpleRNN(32),
    Dense(1, activation='sigmoid')
])
```

- **Dataset**: IMDb 50K movie reviews
- **Vocab Size**: 10,000 words
- **Max Sequence Length**: 200 tokens
- **Training**: 3 epochs, batch size 64
- **Test Accuracy**: ~80.3%

### Re-training on the IMDb Dataset
You can re-train the model or regenerate the dataset mapping at any time by running:

```bash
python train_model.py
```

This script automatically downloads the IMDb 50,000 review dataset, builds `imdb_word_index.pkl`, exports a readable sample CSV (`imdb_sample_dataset.csv`), trains the `SimpleRNN` model, and saves the trained weights into `rnn_imdb_model.h5`.


---

## 🛠️ Tech Stack

| Layer       | Technology                     |
|-------------|-------------------------------|
| Backend     | Python, Flask                  |
| Database    | SQLite3                        |
| AI/ML       | TensorFlow Keras (SimpleRNN)   |
| Frontend    | HTML, Vanilla CSS, JavaScript  |
| Auth        | Flask Sessions, Werkzeug       |

---

## 🌗 Theme Toggle

Click the **☀️ Sun** icon (top-right navbar) to switch to **Light Mode**.  
Click the **🌙 Moon** icon to switch back to **Dark Mode**.  
Your preference is saved automatically in browser localStorage.

---

## 📋 Database Schema

### `reviews` table
| Column       | Type      | Description                          |
|--------------|-----------|--------------------------------------|
| `id`         | INTEGER   | Primary key                          |
| `user_id`    | INTEGER   | FK → users.id                        |
| `movie_id`   | INTEGER   | FK → movies.id                       |
| `movie_name` | TEXT      | Movie title stored directly          |
| `review_text`| TEXT      | User's review content                |
| `sentiment`  | TEXT      | `positive` or `negative`             |
| `created_at` | TIMESTAMP | Auto-generated timestamp             |

---

## Author
**Kovvuri Harshitha**
- Github Url: https://github.com/HarshithaKovvuri17/MovieBuzz.git