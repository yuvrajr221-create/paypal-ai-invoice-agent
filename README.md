# paypal-ai-invoice-agent

An AI chat assistant that creates and pays PayPal sandbox invoices.
Type a message like "Send Rahul a bill for 7 for logo design". Gemini understands it, the app creates a PayPal order, you approve it as the buyer, and the AI can summarize your payments.

## Features
- Chat message to structured invoice (recipient, amount, description) using Gemini
- PayPal Orders v2 API (sandbox): create order, buyer approval, capture
- Payment records saved locally (payments.json)
- AI spending summary of past payments

## AI and tools used
- Gemini API (model: gemini-3.5-flash-lite) for understanding chat messages and summarizing payments
- PayPal Orders v2 REST API (sandbox)
- Python, Flask, requests, plain HTML/JS
- Built and run entirely on an Android phone using Termux
- AI assistance (Claude) was used to help write and debug the code

## Requirements
- Python 3.10+
- A PayPal Developer account (sandbox) with a Business and a Personal sandbox account. Use a US Personal buyer account: India-to-India sandbox payments are rejected by PayPal.
- A free Gemini API key from Google AI Studio

## Setup (Termux or any Linux/macOS shell)

    git clone https://github.com/yuvrajr221-create/paypal-ai-invoice-agent
    cd paypal-ai-invoice-agent
    pip install -r requirements.txt

Create a file named .env in the project folder with these three lines (use your own keys, never commit this file):

    PAYPAL_CLIENT_ID=your_sandbox_client_id
    PAYPAL_SECRET=your_sandbox_secret
    GEMINI_API_KEY=your_gemini_key

- PayPal keys: developer.paypal.com > Apps and Credentials > Sandbox > Default Application.
- Gemini key: aistudio.google.com > Get API key (free tier, no card needed).

## Run

    python app.py

Open http://127.0.0.1:5000 in a browser.

## How to use
1. Type: Send Rahul a bill for 7 for logo design, then press Send.
2. Click "Pay with PayPal (sandbox)" and log in with your sandbox Personal (buyer) account. Approve the payment.
3. After the example.com page appears, go back and click "I have paid".
4. The payment shows as COMPLETED. Click "AI spending summary" for an AI summary of your payments.

Amounts are in USD. These are sandbox test payments only, no real money moves.

## License
MIT
