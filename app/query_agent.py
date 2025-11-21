def explain_incidents(results: list[dict], query: str):
    """Simple explanation for retrieved context: top highlights and confidence."""
    highlights = []
    for r in results[:5]:
        ticker = r.get("ticker", "UNKNOWN")
        title = r.get("title") or (r.get("text", "")[:80] + ("..." if len(r.get("text", "")) > 80 else ""))
        highlights.append(f"{ticker}: {title}")

    scores = [abs(r.get("score", 0.0)) for r in results]
    conf = 0.0 if not scores else min(0.99, sum(scores) / max(1, len(scores)))
    return {"query": query, "highlights": highlights, "confidence": round(conf, 2)}


def financial_answer(results: list[dict], query: str):
    """Return structured financial Q&A with risks, opportunities, summary, and confidence."""
    text_blobs = []
    for r in results:
        t = r.get("text") or r.get("title") or ""
        text_blobs.append(t)

    # naive keyword heuristics
    risk_words = [
        "risk", "concern", "challenge", "decline", "recall", "regulatory",
        "lawsuit", "shortfall", "headwind", "weak", "delay", "reduce"
    ]
    opp_words = [
        "growth", "strong", "increase", "beat", "expansion", "incentive",
        "tailwind", "demand", "ramp", "improve", "gain"
    ]

    risks = []
    opportunities = []
    for t in text_blobs:
        low = t.lower()
        if any(w in low for w in risk_words):
            risks.append(t[:160] + ("..." if len(t) > 160 else ""))
        if any(w in low for w in opp_words):
            opportunities.append(t[:160] + ("..." if len(t) > 160 else ""))

    # summary: top tickers and brief trend
    tickers = [r.get("ticker", "UNKNOWN") for r in results]
    unique_tickers = [t for i, t in enumerate(tickers) if t not in tickers[:i]]
    summary = {
        "question": query,
        "top_tickers": unique_tickers[:5],
        "context_items": len(results),
    }

    scores = [abs(r.get("score", 0.0)) for r in results]
    conf = 0.0 if not scores else min(0.99, sum(scores) / max(1, len(scores)))

    # return context snippets for transparency
    context = []
    for r in results[:5]:
        txt_full = r.get("text", "")
        sent = sentiment_score(txt_full or (r.get("title") or ""))
        context.append({
            "ticker": r.get("ticker", "UNKNOWN"),
            "title": r.get("title", ""),
            "text": (r.get("text", "")[:220] + ("..." if len(r.get("text", "")) > 220 else "")),
            "score": r.get("score", 0.0),
            "sentiment": round(float(sent), 3),
        })

    return {
        "summary": summary,
        "risks": risks[:5],
        "opportunities": opportunities[:5],
        "confidence": round(conf, 2),
        "context": context,
    }
from agents.sentiment import sentiment_score