import json, os, time
from flask import Flask, request, jsonify, send_from_directory
from gemini_client import parse_invoice, summarize
from paypal_client import create_order, capture_order

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "payments.json")

def load():
    try:
        return json.load(open(DB))
    except Exception:
        return []

def save(items):
    json.dump(items, open(DB, "w"), indent=2)

@app.route("/")
def home():
    return send_from_directory(BASE, "index.html")

@app.route("/payments")
def payments():
    return jsonify(load())

@app.route("/chat", methods=["POST"])
def chat():
    text = (request.get_json(silent=True) or {}).get("message", "").strip()
    if not text:
        return jsonify(error="Empty message"), 400
    try:
        info = parse_invoice(text)
    except Exception:
        return jsonify(error="AI could not read the message"), 502
    try:
        amount = float(info.get("amount"))
    except Exception:
        amount = 0
    if info.get("intent") != "create_invoice" or amount <= 0 or amount > 10000:
        return jsonify(error="I could not find a valid invoice request"), 400
    who = info.get("recipient") or "Customer"
    desc = info.get("description") or "Invoice"
    try:
        order_id, link = create_order(amount, desc + " (for " + who + ")")
    except Exception:
        return jsonify(error="PayPal order failed"), 502
    items = load()
    items.append({"order_id": order_id, "recipient": who,
                  "description": desc, "amount": amount,
                  "currency": "USD", "status": "CREATED",
                  "time": time.strftime("%Y-%m-%d %H:%M")})
    save(items)
    return jsonify(order_id=order_id, approve_link=link,
                   recipient=who, description=desc, amount=amount)

@app.route("/capture", methods=["POST"])
def capture():
    oid = (request.get_json(silent=True) or {}).get("order_id", "")
    items = load()
    rec = next((i for i in items if i["order_id"] == oid), None)
    if rec is None:
        return jsonify(error="Unknown order"), 404
    code, data = capture_order(oid)
    issues = [d.get("issue") for d in data.get("details", [])] if isinstance(data, dict) else []
    done = data.get("status") == "COMPLETED" or "ORDER_ALREADY_CAPTURED" in issues
    if done:
        rec["status"] = "COMPLETED"
        save(items)
        return jsonify(status="COMPLETED", order_id=oid)
    return jsonify(error="Payment not completed. Approve it in PayPal first.",
                   code=code), 400

@app.route("/summary")
def summary():
    items = load()
    if not items:
        return jsonify(summary="No payments yet.")
    try:
        return jsonify(summary=summarize(items))
    except Exception:
        return jsonify(error="AI summary failed"), 502

@app.route("/return")
def paypal_return():
    oid = request.args.get("token", "")
    items = load()
    rec = next((i for i in items if i["order_id"] == oid), None)
    if rec is None:
        return "Unknown order", 404
    code, data = capture_order(oid)
    issues = [d.get("issue") for d in data.get("details", [])] if isinstance(data, dict) else []
    done = data.get("status") == "COMPLETED" or "ORDER_ALREADY_CAPTURED" in issues
    if done:
        rec["status"] = "COMPLETED"
        save(items)
        title = "Payment completed"
    else:
        title = "Payment not completed"
    return ("<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<h2>" + title + "</h2><a href='/'>Back to chat</a>")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
