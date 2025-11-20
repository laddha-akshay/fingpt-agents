import os
try:
    import openai
except Exception:
    openai = None

OPENAI_KEY = os.getenv('OPENAI_API_KEY')
if openai and openai != "":
    openai.api_key = OPENAI_KEY

def make_report(top_signals, headlines):
    prompt = f"Produce a short market summary given signals: {top_signals}\\nHeadlines: {headlines}"
    if openai:
        try:
            resp = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[{'role':'user','content':prompt}],
                max_tokens=300
            )
            return resp['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f'OpenAI error: {e}'
    else:
        return "OpenAI key not set. Sample report: " + str(top_signals)
