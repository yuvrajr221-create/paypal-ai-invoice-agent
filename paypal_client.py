import os, requests

BASE = "https://api-m.sandbox.paypal.com"


def load_env(path=".env"):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env()


def _token():
    r = requests.post(
        BASE + "/v1/oauth2/token",
        auth=(os.environ["PAYPAL_CLIENT_ID"], os.environ["PAYPAL_SECRET"]),
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def _headers():
    return {"Authorization": "Bearer " + _token(), "Content-Type": "application/json"}


def create_order(amount, description="Invoice", currency="USD"):
    body = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "description": description[:120],
            "amount": {"currency_code": currency, "value": f"{float(amount):.2f}"},
        }],
        "application_context": {
            "return_url": "https://example.com/return",
            "cancel_url": "https://example.com/cancel",
        },
    }
    r = requests.post(BASE + "/v2/checkout/orders", headers=_headers(), json=body, timeout=30)
    r.raise_for_status()
    d = r.json()
    link = next(l["href"] for l in d["links"] if l["rel"] in ("approve", "payer-action"))
    return d["id"], link


def capture_order(order_id):
    r = requests.post(
        BASE + f"/v2/checkout/orders/{order_id}/capture",
        headers=_headers(), json={}, timeout=30,
    )
    return r.status_code, r.json()
