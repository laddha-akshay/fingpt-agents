from collections import defaultdict

def aggregate_by_ticker(news_items):
    scores = defaultdict(list)
    for it in news_items:
        ticker = it.get('ticker','UNKNOWN')
        scores[ticker].append(it.get('sentiment', 0.0))
    agg = []
    for t, vals in scores.items():
        agg.append({'ticker': t, 'count': len(vals), 'avg_sentiment': sum(vals)/len(vals)})
    agg.sort(key=lambda x: x['avg_sentiment'])
    return agg
