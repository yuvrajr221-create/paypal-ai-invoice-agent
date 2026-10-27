import os, json, requests

MODEL = "gemini-3.5-flash-lite"

PROMPT = (
    "You read a chat message about sending an invoice. "
    "Reply with JSON only, with keys: "
    "intent (create_invoice or other), recipient (string), "
    "amount (number), description (string). "
    "Use null for anything missing. Amount must be exactly the number written, never multiplied. Message: "
)

def _env(name):
    v = os.environ.get(name)
    if v:
        return v
    path = os.path.join(os.path.dirname(__file__), ".env")
    for line in open(path):
        line = line.strip()
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def parse_invoice(text):
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           + MODEL + ":generateContent")
    body = {
        "contents": [{"parts": [{"text": PROMPT + text}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    r = requests.post(url, headers={"x-goog-api-key": _env("GEMINI_API_KEY")},
                      json=body, timeout=30)
    r.raise_for_status()
    out = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(out)

def summarize(items):
    rows = [{"to": i["recipient"], "for": i["description"],
             "usd": i["amount"], "status": i["status"]} for i in items]
    prompt = ("Summarize these payments in 2-3 short sentences for a user. "
              "Mention total paid (COMPLETED only) and pending (CREATED) amounts in USD. "
              "Plain text only. Data: " + json.dumps(rows))
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           + MODEL + ":generateContent")
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, headers={"x-goog-api-key": _env("GEMINI_API_KEY")},
                      json=body, timeout=30)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
