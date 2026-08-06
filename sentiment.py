"""
Sentiment Analysis Engine using TensorFlow Keras SimpleRNN trained on IMDb dataset.
Architecture:
  - Embedding(10000, 32, input_length=200)
  - SimpleRNN(32)
  - Dense(1, activation='sigmoid')

Strategy:
  - Short reviews (< 15 words): lexicon-first, then RNN as tie-breaker if no signal.
  - Long reviews  (>= 15 words): RNN-first, then lexicon fallback.
  This prevents the RNN (trained on long IMDb essays) from misclassifying
  short phrases like "It is a super movie" that get 195 zero-padding tokens.
"""
import os
import re
import pickle

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ── Expanded positive lexicon ──────────────────────────────────────────────────
POSITIVE_WORDS = {
    # Core praise
    'amazing', 'excellent', 'great', 'awesome', 'fantastic', 'good', 'superb',
    'outstanding', 'phenomenal', 'brilliant', 'masterpiece', 'wonderful', 'perfect',
    'spectacular', 'incredible', 'top', 'best', 'flawless', 'extraordinary',
    # Enjoyment
    'love', 'loved', 'like', 'liked', 'enjoy', 'enjoyed', 'adore', 'adored',
    'fun', 'entertaining', 'thrilling', 'exciting', 'engaging', 'captivating',
    'fascinating', 'gripping', 'riveting', 'absorbing', 'immersive',
    # Quality
    'solid', 'impressive', 'polished', 'refined', 'well-made', 'well-written',
    'well-acted', 'well-directed', 'strong', 'powerful', 'moving', 'touching',
    'emotional', 'heartfelt', 'beautiful', 'stunning', 'gorgeous', 'visual',
    # Casual positives  ← "super" was MISSING — now added
    'super', 'nice', 'cool', 'fine', 'neat', 'decent', 'pleasing', 'satisfying',
    'charming', 'delightful', 'lovely', 'sweet', 'warm', 'heartwarming',
    # Superlatives / recommending
    'favorite', 'recommend', 'recommended', 'must-watch', 'gem', 'classic',
    'masterwork', 'highlight', 'mind-blowing', 'jaw-dropping', 'unforgettable',
    'memorable', 'iconic', 'timeless', 'compelling', 'magic', 'magical',
    # Performances
    'talented', 'gifted', 'natural', 'convincing', 'believable',
    # Story / direction
    'creative', 'original', 'fresh', 'innovative', 'unique', 'clever', 'smart',
    'witty', 'humorous', 'funny', 'hilarious', 'entertaining', 'engaging',
    # Positive interjections often used
    'wow', 'brilliant', 'superstar', 'blockbuster',
}

# ── Expanded negative lexicon ──────────────────────────────────────────────────
NEGATIVE_WORDS = {
    # Core criticism
    'bad', 'terrible', 'horrible', 'awful', 'worst', 'poor', 'dreadful',
    'atrocious', 'abysmal', 'pathetic', 'appalling', 'dismal', 'mediocre',
    'inferior', 'subpar', 'inadequate', 'unacceptable', 'disgusting',
    # Emotional disappointment
    'hate', 'hated', 'dislike', 'disliked', 'despise', 'despised',
    'disappointed', 'disappointing', 'disappointment', 'regret', 'regretted',
    # Boredom / pacing
    'boring', 'bored', 'dull', 'tedious', 'monotonous', 'bland', 'flat',
    'slow', 'dragging', 'dragged', 'sluggish', 'repetitive', 'predictable',
    # Waste / value
    'waste', 'wasted', 'pointless', 'useless', 'worthless', 'meaningless',
    'hollow', 'empty', 'shallow', 'senseless', 'aimless',
    # Quality failures
    'trash', 'crap', 'garbage', 'rubbish', 'junk', 'mess', 'disaster',
    'flawed', 'broken', 'incoherent', 'confusing', 'messy', 'chaotic',
    'sloppy', 'amateurish', 'cheap', 'tacky',
    # Performances
    'overacting', 'wooden', 'stiff', 'unconvincing', 'unbelievable',
    # Common casual negatives
    'lame', 'sucks', 'sucked', 'annoying', 'irritating', 'cringe', 'cringeworthy',
    'overrated', 'unimpressive', 'forgettable', 'unwatchable', 'unbearable',
    'insufferable', 'torture', 'fail', 'failure', 'flop', 'bomb',
}

NEGATION_WORDS = {
    'not', "n't", 'never', 'no', 'hardly', 'barely', 'scarcely',
    'without', 'neither', 'nor', 'nothing', 'nowhere', 'nobody',
}

# ── Model cache ────────────────────────────────────────────────────────────────
_RNN_MODEL = None
_WORD_INDEX = None

def load_rnn_model():
    """Loads trained TensorFlow Keras SimpleRNN model and IMDb word index."""
    global _RNN_MODEL, _WORD_INDEX
    if _RNN_MODEL is not None and _WORD_INDEX is not None:
        return _RNN_MODEL, _WORD_INDEX

    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'rnn_imdb_model.h5')
    word_index_path = os.path.join(base_dir, 'imdb_word_index.pkl')

    if os.path.exists(model_path) and os.path.exists(word_index_path):
        try:
            import tensorflow as tf
            _RNN_MODEL = tf.keras.models.load_model(model_path)
            with open(word_index_path, 'rb') as f:
                _WORD_INDEX = pickle.load(f)
            return _RNN_MODEL, _WORD_INDEX
        except Exception as e:
            print(f"[Warning] Failed to load RNN model: {e}")
            _RNN_MODEL, _WORD_INDEX = None, None

    return None, None


def predict_rnn_sentiment(review_text):
    """
    SimpleRNN prediction.
    Returns ('positive'/'negative', score) or (None, None) on failure.
    """
    model, word_index = load_rnn_model()
    if model is None or word_index is None:
        return None, None

    try:
        # pyrefly: ignore [missing-import]
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        max_length = 200
        words = review_text.lower().split()
        sequence = []
        for word in words:
            clean_w = re.sub(r'^\W+|\W+$', '', word)
            if clean_w in word_index and word_index[clean_w] + 3 < 10000:
                sequence.append(word_index[clean_w] + 3)
            else:
                sequence.append(word_index.get(clean_w, 2))
        sequence = pad_sequences([sequence], maxlen=max_length)
        prediction = model.predict(sequence, verbose=0)
        score = float(prediction[0][0])
        return ('positive' if score >= 0.5 else 'negative'), score
    except Exception as e:
        print(f"[Warning] RNN prediction failed: {e}")
        return None, None


def lexicon_sentiment(text):
    """
    Rule-based lexicon sentiment analysis.
    Returns ('positive'/'negative', pos_score, neg_score).
    """
    words = re.findall(r"\b[\w']+\b", text.lower())
    pos_score = 0.0
    neg_score = 0.0

    for i, word in enumerate(words):
        negated = (i > 0 and words[i - 1] in NEGATION_WORDS) or \
                  (i > 1 and words[i - 2] in NEGATION_WORDS)
        if word in POSITIVE_WORDS:
            if negated:
                neg_score += 1.5
            else:
                pos_score += 1.0
        elif word in NEGATIVE_WORDS:
            if negated:
                pos_score += 1.5
            else:
                neg_score += 1.0

    sentiment = 'positive' if pos_score >= neg_score else 'negative'
    return sentiment, pos_score, neg_score


def analyze_sentiment(text):
    """
    Hybrid sentiment engine:

    SHORT reviews (< 15 words):
      The RNN was trained on long IMDb essays (~200 words). Feeding a 5-word
      phrase produces ~195 zero-padding tokens which confuse the model heavily.
      → Use lexicon FIRST. Only call RNN as a tie-breaker when lexicon finds
        zero signal (no positive or negative words at all).

    LONG reviews (>= 15 words):
      The RNN is reliable in this range.
      → Use RNN FIRST, then fall back to lexicon.
    """
    if not text or not text.strip():
        return 'positive'

    word_count = len(text.split())

    if word_count < 15:
        # ── Short review: lexicon-first ────────────────────────────────────
        lex_sent, pos_s, neg_s = lexicon_sentiment(text)

        if pos_s > 0 or neg_s > 0:
            # Lexicon found a clear signal — trust it
            return lex_sent

        # No signal in lexicon → try RNN as last resort
        rnn_sent, _ = predict_rnn_sentiment(text)
        if rnn_sent is not None:
            return rnn_sent

        # Absolute fallback: default positive for neutral/unknown short phrases
        return 'positive'

    else:
        # ── Long review: RNN-first ────────────────────────────────────────
        rnn_sent, _ = predict_rnn_sentiment(text)
        if rnn_sent is not None:
            return rnn_sent

        # Lexicon fallback for long reviews
        lex_sent, _, _ = lexicon_sentiment(text)
        return lex_sent
