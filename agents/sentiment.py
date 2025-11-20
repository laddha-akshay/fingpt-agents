from textblob import TextBlob

def sentiment_score(text: str) -> float:
    t = TextBlob(text)
    return t.sentiment.polarity
