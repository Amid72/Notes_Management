# NotesVault — Deployment Guide

This guide walks you through deploying **NotesVault** to **Netlify** using Netlify Serverless Functions, configuring a free cloud MySQL database, and setting up environment variables.

---

## 🏗️ How NotesVault Runs on Netlify

Netlify is primarily a static and serverless platform. To run a Python Flask application with full CRUD and authentication:
1. **Frontend & Static Assets**: CSS, JavaScript, and fonts in `static/` are served with high speed directly from Netlify's global CDN.
2. **Backend**: Flask routes (`/login`, `/register`, `/dashboard`, etc.) run as a serverless AWS Lambda function via `serverless-wsgi` inside `netlify/functions/app.py`.
3. **Database**: Netlify cannot run a local MySQL server (`localhost`). You connect your Netlify site to a free cloud-hosted MySQL database (such as **TiDB Cloud** or **Aiven**).

---

## 📋 Step 1: Set Up a Free Cloud MySQL Database

Because `localhost` does not exist in the cloud, you need a cloud-hosted MySQL database.

### Recommended: TiDB Cloud Serverless (Free Forever, 100% MySQL Compatible)
1. Go to [https://tidbcloud.com/](https://tidbcloud.com/) and sign up for free (no credit card required).
2. Click **Create Cluster** and select **Serverless (Free)**.
3. Once the cluster is created, click **Connect**.
4. Choose **Connect with MySQL CLI / General Client**:
   - Note down the **Host**, **Port** (usually `4000`), **User**, and **Password**.
   - Note down or create a database named `notes_db` (or use the default database).

### Initialize Database Tables:
You can initialize the tables on your cloud database from your computer by either:
- **Option A (Easy Python Script)**:
  Run in your terminal:
  ```bash
  python init_db.py
  ```
  *(Make sure your `.env` contains your cloud database credentials)*
- **Option B (Web SQL Console)**:
  Copy and paste the contents of `schema.sql` directly into the SQL editor in the TiDB Cloud / Aiven dashboard and click **Run**.

---

## 🐙 Step 2: Push Your Project to GitHub

If you haven't already committed this repository to GitHub:

```bash
git init
git add .
git commit -m "Configure NotesVault for Netlify deployment"
git branch -M main
git remote add origin https://github.com/Amid72/Notes_Management.git
git push -u origin main
```

> [!NOTE]
> `.gitignore` is already set up to ensure your local `.env` and passwords are never pushed to GitHub.

---

## 🚀 Step 3: Deploy on Netlify

1. Go to [https://app.netlify.com/](https://app.netlify.com/) and log in.
2. Click **"Add new site"** → **"Import an existing project"**.
3. Select **GitHub** and choose your `notes_app` repository.
4. Netlify will automatically detect the `netlify.toml` file with:
   - **Build command**: `python -c "import shutil, os; os.makedirs('public', exist_ok=True); shutil.copytree('static', 'public/static', dirs_exist_ok=True)"`
   - **Publish directory**: `public`
   - **Functions directory**: `netlify/functions`

---

## 🔑 Step 4: Add Environment Variables in Netlify

Before deploying (or under **Site configuration** → **Environment variables**), add the following variables:

| Variable | Description | Example |
| :--- | :--- | :--- |
| `SECRET_KEY` | Random secret key for session cookies | `a8f93bc14298...` |
| `DB_HOST` | Cloud MySQL Host | `gateway01.us-east-1.prod.aws.tidbcloud.com` |
| `DB_PORT` | Cloud MySQL Port | `4000` (or `3306`) |
| `DB_USER` | Cloud MySQL Username | `xxxxxx.root` |
| `DB_PASSWORD`| Cloud MySQL Password | `your_db_password` |
| `DB_NAME` | Database name | `notes_db` |
| `MAIL_SERVER`| SMTP server for OTP | `smtp.gmail.com` |
| `MAIL_PORT`  | SMTP port | `587` |
| `MAIL_USE_TLS` | Use TLS | `True` |
| `MAIL_USERNAME`| Your Gmail address | `youremail@gmail.com` |
| `MAIL_PASSWORD`| Gmail App Password | `xxxx xxxx xxxx xxxx` |
| `MAIL_DEFAULT_SENDER`| Sender email address | `youremail@gmail.com` |

---

## 🌐 Step 5: Test Your Deployed App

Click **Deploy site**. Once the build finishes:
1. Open your Netlify URL (e.g. `https://your-site-name.netlify.app/`).
2. Test **Register**: Create a new account.
3. Test **Login**: Log into the newly created account.
4. Test **Notes CRUD**: Create, edit, and delete notes.
5. Test **Forgot Password**: Request an OTP to your email.

---

## 💡 Alternative Option: Deploy to Render or Railway

If you ever prefer running Flask as a persistent web server rather than serverless functions:
- **Render**: Connect your GitHub repository to [Render.com](https://render.com/), choose **Web Service**, Python runtime, and start command `gunicorn app:app`.
- **Railway**: Connect your repository to [Railway.app](https://railway.app/). Railway will automatically read the `Procfile` (`web: gunicorn app:app`) and can also provision a MySQL database for you with 1 click.
