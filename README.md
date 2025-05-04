Thought for a couple of seconds


## Medistics – MDCAT Learning Platform

A Flask-based web application providing MDCAT practice questions, performance tracking, and AI-powered generative tests. Free users draw from a local Excel question bank; paid “Iconic” subscribers unlock on-demand GPT-3.5 question generation. Includes user signup, login, profile settings, subscription management, SQLite persistence, and Pakistan-friendly payment gateway stubs.

---

## Features

* **User Authentication**

  * Email/password signup → choose username → profile setup
  * Login/logout with session management

* **Dashboard & Performance**

  * Tracks correct/total per subject (Biology, Chemistry, Physics, English, Logical Reasoning)
  * Displays career score and detailed breakdown

* **Practice Questions**

  * Free & Gold users draw from a local Excel (`questions.xlsx`) with MCQs
  * Random sampling by subject and question count

* **Generative Test**

  * Iconic subscribers provide an OpenAI API key
  * GPT-3.5 Turbo generates JSON-formatted MCQs on demand

* **Account Settings**

  * Update OpenAI key, view subscription history, days since signup
  * Cancel subscriptions, file disputes, delete account

* **Subscription & Payments**

  * Three plans: Basic (free), Gold (₨150/mo), Iconic (₨300/mo)
  * Payment records stored in SQLite
  * Stub routes for JazzCash/EasyPaisa integration

* **Issue Reporting**

  * Submit support tickets with category and ≥70-character description

---

## Tech Stack

* **Backend**: Python 3.9+, Flask
* **Database**: SQLite via `sqlite3` (wrapped in `database.py`)
* **Templating**: Jinja2 (`/templates/*.html`)
* **Frontend**: Vanilla HTML/CSS/JS, Boxicons, Google Fonts
* **AI**: OpenAI GPT-3.5 Turbo (for paid plan)
* **Data**: `questions.xlsx` Excel spreadsheet (Pandas + openpyxl)

---

## Repository Structure

```
medistics_app/
├─ app.py
├─ database.py
├─ requirements.txt
├─ questions.xlsx
├─ medistics.db
├─ templates/
│   ├─ main.html
│   ├─ index.html
│   ├─ signup.html
│   ├─ chooseusername.html
│   ├─ userinfo.html
│   ├─ userinfo2.html
│   ├─ userinfo3.html
│   ├─ login.html
│   ├─ account.html
│   ├─ accsettings.html
│   ├─ pricing.html
│   ├─ testsettings.html
│   ├─ testpage.html
│   ├─ reportissue.html
│   ├─ thanksforreport.html
│   ├─ changepassword.html
│   ├─ dlmode.html
│   └─ ...
└─ static/
    ├─ css/
    ├─ js/
    └─ images/
```

---

## Prerequisites

* Python 3.9 or higher
* [pipenv](https://pipenv.pypa.io/) or `virtualenv` (recommended)
* An OpenAI API key (for Iconic plan)
* Optional: Merchant credentials for JazzCash/EasyPaisa

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/medistics_app.git
   cd medistics_app
   ```

2. **Create & activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Linux/macOS
   venv\Scripts\activate.bat     # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Place your question bank**

   * Rename your Excel file to `questions.xlsx`
   * Ensure columns:
     `subject, question_text, option1, option2, option3, option4, correct_option, explanation`

---

## Configuration

Copy `env.example` to `.env` (or set env vars directly):

```ini
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# OpenAI (Iconic plan)
OPENAI_API_KEY=

# JazzCash (sandbox/test)
JC_MERCHANT_ID=
JC_INTEGRITY_SALT=

# EasyPaisa (sandbox/test)
EP_MERCHANT_ID=
EP_INTEGRITY_KEY=
```

Flask will load these automatically (via `python-dotenv`).

---

## Database Setup

On first run, the app auto-creates `medistics.db` and required tables:

* **users**
* **questions** (not used if you supply `questions.xlsx`)
* **issues**
* **payments**

If you ever need to reset:

```bash
rm medistics.db
flask run
```

---

## Running the App

```bash
flask run
```

* Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)
* Sign up → choose username → set profile → log in
* Navigate through Dashboard, Pricing, Test Settings, etc.

---

## Payment Gateway Integration

By default, payment endpoints are stubs. To enable real transactions:

1. Implement `pay_jazzcash` & `jazzcash_callback` in `app.py` (see comments).
2. Create `jazzcash_redirect.html` under `templates/` that auto-submits to JazzCash sandbox/live URL.
3. Mirror similar flow for EasyPaisa.
4. Store transaction records in the built-in **payments** table.

---

## Contributing

1. Fork the repo
2. Create a new branch (`git checkout -b feature/xyz`)
3. Commit your changes & push (`git push origin feature/xyz`)
4. Open a Pull Request

Please follow [PEP8](https://www.python.org/dev/peps/pep-0008/) and write tests for new features.

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
