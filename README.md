# MysteryMart — Unbox the Unexpected! 🎁✨

> An online shopping platform for curated surprise boxes inspired by Amazon & Flipkart. Customers select their category, pick a price tier, review guaranteed retail inclusions, and experience the thrill of the unexpected.

[![Live Deployment](https://img.shields.io/badge/Render-Live%20Demo-7C3AED?logo=render)](https://mysterymart1.onrender.com/)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-3.1.3-black?logo=flask)](https://flask.palletsprojects.com/)
[![SQL Database](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-336791?logo=postgresql)](https://www.postgresql.org/)
[![NoSQL Database](https://img.shields.io/badge/NoSQL-MongoDB%20Atlas-47A248?logo=mongodb)](https://www.mongodb.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-34%20Passed-success?logo=pytest)](https://pytest.org/)

---

## 🌐 Live Website & Reference Deployment

* **Reference Deployment (Visual & Deployment Standard):** [https://open-specimen.onrender.com/](https://open-specimen.onrender.com/)
* **MysteryMart Render URL:** [https://mysterymart1.onrender.com/](https://mysterymart1.onrender.com/) *(Automatically redirects directly to the live shop below)*
* **Direct Live Shop (Active Public URL):** [https://two-toes-shave.loca.lt/shop](https://two-toes-shave.loca.lt/shop)
  *(Tunnel password if prompted on first visit: `171.79.53.12`)*

---

## 📌 Features

### 🛒 E-Commerce & Mystery Box Shopping
* **Surprise Categories:** Gadget Mystery Box, Gaming Mystery Box, Stationery Mystery Box, Fashion Mystery Box, Beauty & Accessories Mystery Box, and Sovereign Premium VIP Box.
* **100% Value Transparency:** Every box details guaranteed inclusions before purchase. Zero deceptive lottery or fake prize claims.
* **Server-Side Recalculation:** Subtotals, delivery fees, and order amounts are strictly calculated on the server. Client-sent prices are never trusted.
* **Dynamic Cart Management:** Interactive AJAX line-item updates, stock bounds, and negative quantity prevention.
* **Free Delivery Calculation:** Automated threshold logic ($99.00+) with live progress notifications.
* **Simulated Checkout & Gateways:** Simulated Credit/Debit Card, Digital Wallet, and Cash on Delivery with full client-side address verification. Zero stored raw card details.

### 🤖 AI Customer Support Assistant (Floating Concierge)
* **Always Accessible:** Floating widget on every page, including custom error pages.
* **SQL FAQ Grounding:** Prioritizes verified answers retrieved from the SQL database before generating any AI response.
* **HTTP Error Diagnostician:** Explains error codes (400, 401, 403, 404, 429, 460, 500, 503) and provides actionable troubleshooting steps.
* **Clarifying Prompts:** Proactively asks clarifying questions when users provide brief or ambiguous inquiries.
* **Seamless Escalation:** Generates unique support tickets (`MM-TKT-XXXXXX`) directly in chat if a question cannot be resolved.
* **NoSQL Chat Logging & Feedback:** Saves chat conversations and 5-star customer ratings to MongoDB (with safe in-memory fallback).
* **Multi-Provider AI:** Configurable for offline rule/FAQ fallback mode (no API key needed), Google Gemini, or OpenAI.

### 🎫 Support Ticket & Verification System
* **Unique Ticket References:** Generates unique tracking codes formatted as `MM-TKT-XXXXXX`.
* **Automated Deduplication:** Prevents duplicate tickets when identical requests are submitted repeatedly within a 5-minute window.
* **Privacy Verification:** Ticket status tracking requires both the ticket number and the registered email address.

### ⛅ Third-Party Weather API Integration
* **Route Weather Intelligence:** Fetches real-time destination weather from the Open-Meteo API during checkout.
* **Logistics Advice:** Advises if rain, snow, or storm conditions apply, assuring customers of protective weatherproof seals.
* **Timeout & Fallback Guard:** Request timeout (4s) with caching (15 min) and graceful fallback if the external API is unreachable. Basic store checkout remains 100% operational.

### 🛡️ Production Security & Custom Error Handling
* **Security Headers & Logging:** Configured request performance logging (Timestamp, Method, Path, Status, Duration) while redacting passwords, session secrets, and payment data.
* **Custom HTTP Error Pages:** Dedicated, styled templates for `400`, `401`, `403`, `404`, `429`, `500`, and `503`.
* **Custom Code 460:** Application-specific error code for *Unboxing Concurrency Conflicts* (inventory race conditions).
* **Safe 500 Responses:** Full diagnostic traces logged on the server; public users receive friendly guidance with zero leaked credentials or paths.
* **Rate Limiting:** Protects `/login` and `/api/chat` against brute-force and spam.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Bootstrap 5.3, Bootstrap Icons, Animate.css, Google Fonts (*Plus Jakarta Sans*, *Outfit*, *Inter*) |
| **Backend** | Python 3.10+, Flask 3.1.3, Werkzeug 3.1.9, Jinja2 |
| **ORM / SQL Database** | Flask-SQLAlchemy 3.1.1, SQLite (Local Dev), PostgreSQL (Production Render via `psycopg2-binary`) |
| **NoSQL Database** | MongoDB Atlas via PyMongo (Chat logs & customer feedback) with safe in-memory fallback |
| **Third-Party APIs** | Open-Meteo Weather API (`requests` with timeout & caching) |
| **AI Provider** | Configurable: Offline Rule/SQL FAQ Engine (Default), Google Gemini, or OpenAI |
| **Testing** | pytest 9.1.1 (33 automated unit & integration tests) |
| **Deployment** | Render, Gunicorn WSGI Server, Procfile |

---

## 📸 Screenshots & Visual Tour

*(To add real screenshots to your GitHub repository, take screenshots of your running app and place the images in `docs/screenshots/`, then update the markdown links below.)*

```markdown
![MysteryMart Homepage](docs/screenshots/home.png)
*Homepage with Hero Banner, Categories, and Floating Assistant Widget*

![Shop Catalog](docs/screenshots/shop.png)
*Shop Catalog with Category Filters, Price Sliders, and Sort Options*

![Product Details](docs/screenshots/product.png)
*Product Details showing Guaranteed Inclusions and Surprise Disclosure*

![Floating AI Assistant](docs/screenshots/assistant.png)
*Floating AI Concierge answering FAQ queries and explaining HTTP codes*
```

---

## ⚙️ Local Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/mysterymart.git
cd mysterymart
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to customize settings:
```ini
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secure-random-secret-key-here
DATABASE_URL=sqlite:///mysterymart.db
MONGODB_URI=
AI_PROVIDER=fallback
PORT=5000
```

### 5. Initialize & Seed Database
The database tables and seed data auto-initialize on first run. To manually seed:
```bash
python seed.py
```
*Creates demo user (`demouser` / `MysteryMart2026!`), demo admin (`admin` / `AdminSecret2026!`), 8 mystery box products across 6 categories, and 12 comprehensive FAQs.*

### 6. Run the Application
```bash
python app.py
```
Open your browser at: **[http://localhost:5000](http://localhost:5000)**

---

## 🧪 Running Automated Tests

Run the complete 33-test suite using pytest:
```bash
python -m pytest tests/ -v
```

All 33 tests run against in-memory SQLite and mocked external APIs:
* `tests/test_routes.py`: Verifies all main routes, cart, auth, and health check.
* `tests/test_faq.py`: Verifies >=10 SQL FAQs, search engine scoring, and category filters.
* `tests/test_cart.py`: Verifies server recalculation, stock caps, and negative quantity prevention.
* `tests/test_errors.py`: Verifies custom 404, controlled 500 without stack trace leaks, and custom 460 code.
* `tests/test_tickets.py`: Verifies ticket format (`MM-TKT-XXXXXX`), deduplication, and privacy lookup.
* `tests/test_assistant.py`: Verifies FAQ grounding, HTTP code explanations, clarification, and feedback.
* `tests/test_weather.py`: Verifies timeout handling, connection error fallback, and mock responses.

---

## 🚀 Render Deployment Instructions

Follow these steps to deploy MysteryMart on **Render**:

### Step 1: Create a PostgreSQL Database on Render
1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** &rarr; **PostgreSQL**.
3. Name your database (e.g., `mysterymart-db`).
4. Select the Free tier and click **Create Database**.
5. Once created, copy the **Internal Database URL** (or External Database URL).

### Step 2: Create a Web Service on Render
1. In the Render Dashboard, click **New +** &rarr; **Web Service**.
2. Connect your GitHub repository (`mysterymart`).
3. Set the following configuration:
   * **Name:** `mysterymart`
   * **Region:** Oregon (US West) or closest region
   * **Branch:** `main`
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `gunicorn app:app` *(or Render will detect the included `Procfile`)*

### Step 3: Configure Environment Variables in Render
In the **Environment** tab of your Render Web Service, add:

| Key | Value | Note |
| :--- | :--- | :--- |
| `FLASK_ENV` | `production` | Enables production security & secure cookies |
| `SECRET_KEY` | *(Generate a 32+ char random string)* | Used for session signing |
| `DATABASE_URL` | *(Paste Render PostgreSQL URL)* | App automatically handles `postgres://` &rarr; `postgresql://` |
| `MONGODB_URI` | *(Optional: MongoDB Atlas URI)* | Leave blank for automatic safe in-memory fallback |
| `AI_PROVIDER` | `fallback` | Set to `gemini` if providing `GEMINI_API_KEY` |
| `GEMINI_API_KEY` | *(Optional Google Gemini Key)* | Unlocks AI augmentation |
| `WEATHER_API_TIMEOUT` | `4` | Seconds before weather fallback triggers |

### Step 4: Health Check & Persistent Storage Notes
* **Health Check Path:** Configure Render's health check path to `/health`.
* **Database Migrations & Persistence:** Render's free web service containers use ephemeral filesystems. SQLite databases reset on restarts; therefore, the configured **PostgreSQL** database must be used for persistent SQL orders, users, and tickets in production.
* Click **Deploy Web Service**. Your app will be live at `https://mysterymart.onrender.com`!

---

## 📤 GitHub Publishing Instructions

Follow these steps to push your local MysteryMart project to GitHub:

### 1. Initialize Git in the Project Directory
```bash
cd d:\mysterymart
git init
```

### 2. Verify `.gitignore` Exclusions
Ensure sensitive files (`.env`, `*.db`, `__pycache__`) are never tracked:
```bash
git status
```
*(Confirm that `.env` and `mysterymart.db` do not appear in the untracked files list).*

### 3. Stage and Commit Files
```bash
git add .
git commit -m "Initial commit: MysteryMart production-ready web application"
```

### 4. Create Repository on GitHub & Push
1. Create a new repository named `mysterymart` on your GitHub account.
2. Link your local repository and push:
```bash
git remote add origin https://github.com/your-username/mysterymart.git
git branch -M main
git push -u origin main
```

---

## 🩺 Health Check & System Monitoring

Access the `/health` endpoint anytime:
```bash
curl http://localhost:5000/health
```

Example Healthy Response (HTTP 200):
```json
{
  "app": "MysteryMart",
  "environment": "development",
  "response_time_ms": 2.15,
  "services": {
    "ai_assistant": {
      "mode": "fallback",
      "status": "ready"
    },
    "nosql_storage": {
      "active": true,
      "mode": "In-Memory Fallback",
      "status": "standby_fallback"
    },
    "sql_database": {
      "faqs_count": 12,
      "products_count": 8,
      "status": "up",
      "type": "SQLite"
    },
    "weather_api": {
      "provider": "Open-Meteo Forecast API",
      "status": "available",
      "timeout_seconds": 4
    }
  },
  "status": "healthy",
  "timestamp": "2026-10-27T16:00:00Z",
  "version": "1.0.0"
}
```

---

## 🔒 Security Summary

1. **Zero Raw Card Details:** No raw payment credit/debit card numbers are ever stored in cookies, sessions, databases, or logs.
2. **Server-Side Validation:** All prices, stock limits, and quantities are re-validated and recalculated on the server.
3. **Database Concurrency Protection:** Stock allocation uses transactional row locking; inventory depletion triggers documented custom code `460`.
4. **Log Sanitization:** Request middleware explicitly strips password, token, key, and secret parameters from access logs.
5. **Rate Limiting:** Sliding-window rate limiter guards `/login` and `/api/chat` against brute-force and DDoS attempts.
6. **No Leaked Stack Traces:** 500 error handlers display safe user-facing alerts while logging diagnostics internally on the server.

---

## 🔮 Proposed Future Improvement

* **Interactive 3D Three.js Virtual Box Opener:** Implement a WebGL 3D unboxing animation where customers can click to slice open virtual delivery tape and view 3D models of their guaranteed inclusions before doorstep dispatch.

---

## 📄 License
This project is licensed under the MIT License — feel free to explore, customize, and unbox!
