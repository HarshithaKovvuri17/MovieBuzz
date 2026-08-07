"""
IMDb Dataset Loader & SimpleRNN Sentiment Model Trainer

This script:
1. Fetches the IMDb dataset (50,000 movie reviews) using TensorFlow Keras.
2. Extracts and saves the IMDb word-to-index mapping dictionary as `imdb_word_index.pkl`.
3. Exports a readable sample CSV dataset (`imdb_sample_dataset.csv`) with decoded text and labels.
4. Preprocesses sequences with padding (maxlen=200).
5. Trains a SimpleRNN model for sentiment analysis.
6. Evaluates performance on the test set and saves the model as `rnn_imdb_model.h5`.
"""

import os
import csv
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import imdb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, SimpleRNN, Dense
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Configuration
VOCAB_SIZE = 10000
MAX_LEN = 200
EMBEDDING_DIM = 32
RNN_UNITS = 32
BATCH_SIZE = 64
EPOCHS = 3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'rnn_imdb_model.h5')
WORD_INDEX_PATH = os.path.join(BASE_DIR, 'imdb_word_index.pkl')
CSV_SAMPLE_PATH = os.path.join(BASE_DIR, 'imdb_sample_dataset.csv')


def load_and_export_imdb_data():
    """Loads IMDb dataset, saves word index dictionary and sample CSV dataset."""
    print("1. Fetching IMDb dataset from Keras...")
    (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=VOCAB_SIZE)
    
    print(f"   Loaded {len(x_train)} training reviews and {len(x_test)} test reviews.")

    # ── Save Word Index ────────────────────────────────────────────────────────
    print("2. Downloading & saving word index mapping...")
    raw_word_index = imdb.get_word_index()
    
    with open(WORD_INDEX_PATH, 'wb') as f:
        pickle.dump(raw_word_index, f)
    print(f"   Saved word index to: {WORD_INDEX_PATH}")

    # ── Export Readable Sample CSV ─────────────────────────────────────────────
    print("3. Generating readable sample CSV dataset (imdb_sample_dataset.csv)...")
    # Invert word index (integer -> word)
    index_to_word = {i + 3: w for w, i in raw_word_index.items()}
    index_to_word[0] = "<PAD>"
    index_to_word[1] = "<START>"
    index_to_word[2] = "<UNK>"

    sample_size = min(1000, len(x_train))
    with open(CSV_SAMPLE_PATH, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["review_id", "review_text", "sentiment"])
        for i in range(sample_size):
            decoded_text = " ".join([index_to_word.get(idx, "?") for idx in x_train[i] if idx > 2])
            sentiment_label = "positive" if y_train[i] == 1 else "negative"
            writer.writerow([i + 1, decoded_text, sentiment_label])

    print(f"   Saved 1,000 decoded sample reviews to: {CSV_SAMPLE_PATH}")

    return (x_train, y_train), (x_test, y_test)



def build_and_train_model(x_train, y_train, x_test, y_test):
    """Preprocesses input sequences, builds SimpleRNN model, trains & saves model."""
    print("\n4. Preprocessing sequence data (padding to length 200)...")
    x_train_padded = pad_sequences(x_train, maxlen=MAX_LEN)
    x_test_padded = pad_sequences(x_test, maxlen=MAX_LEN)

    print("\n5. Building SimpleRNN model architecture...")
    model = Sequential([
        Embedding(input_dim=VOCAB_SIZE, output_dim=EMBEDDING_DIM, input_length=MAX_LEN),
        SimpleRNN(units=RNN_UNITS),
        Dense(units=1, activation='sigmoid')
    ])

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    model.summary()

    print("\n6. Training SimpleRNN model...")
    history = model.fit(
        x_train_padded, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(x_test_padded, y_test)
    )

    print("\n7. Evaluating model performance on test dataset...")
    test_loss, test_acc = model.evaluate(x_test_padded, y_test, verbose=0)
    print(f"   --> Test Accuracy: {test_acc * 100:.2f}% | Test Loss: {test_loss:.4f}")

    print("\n8. Saving trained model weights...")
    model.save(MODEL_PATH)
    print(f"   Saved model to: {MODEL_PATH}")

    return model, test_acc


if __name__ == "__main__":
    print("=" * 60)
    print(" IMDb Sentiment Analysis Model Training Pipeline ")
    print("=" * 60)
    (x_train, y_train), (x_test, y_test) = load_and_export_imdb_data()
    build_and_train_model(x_train, y_train, x_test, y_test)
    print("\n Training complete! You can now run sentiment analysis or Flask app.")
