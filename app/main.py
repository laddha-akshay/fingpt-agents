from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from agents.scraper import load_sample_news
from agents.sentiment import sentiment_score
from agents.aggregator import aggregate_by_ticker
from agents.reporter import make_report
import os

app = FastAPI()
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount('/static', StaticFiles(directory=static_dir), name='static')

@app.get('/')
def root():
    return HTMLResponse(open(os.path.join(static_dir,'index.html')).read())

@app.get('/run')
def run_pipeline():
    news = load_sample_news()
    for n in news:
        n['sentiment'] = sentiment_score(n.get('text',''))
    agg = aggregate_by_ticker(news)
    top = agg[:5]
    headlines = [n.get('title') for n in news[:10]]
    report = make_report(top, headlines)
    return JSONResponse({'top': top, 'report': report, 'count': len(news)})
