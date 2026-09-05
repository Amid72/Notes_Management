# NotesVault — Deployment Guide (SQLite)

This guide walks you through deploying **NotesVault** to **Netlify** using **SQLite**.

---

## ⚡ Why SQLite is so easy
- **Zero Database Setup**: No need to register for TiDB, MySQL, or any external database service!
- **Auto-Initialization**: The app automatically creates the database and the `users` and `notes` tables on startup.
- **Built into Python**: Uses Python's native `sqlite3` engine.

---

## 🚀 Step 1: Commit and Push Changes to GitHub

In your project folder terminal, push the SQLite update:

```bash
git add .
git commit -m "Switch database to SQLite for zero-config deployment"
git push origin main
```

---

## 🌐 Step 2: Deploy on Netlify

1. Go to **[https://app.netlify.com/](https://app.netlify.com/)** and log in.
2. Click **"Add new site"** → **"Import an existing project"**.
3. Choose **GitHub** and select your repository: **`Amid72/Notes_Management`**.
4. Netlify will automatically detect your configuration from `netlify.toml`:
   - **Build command**: `python -c "import shutil, os; os.makedirs('public', exist_ok=True); shutil.copytree('static', 'public/static', dirs_exist_ok=True)"`
   - **Publish directory**: `public`
   - **Functions directory**: `netlify/functions`
5. *(Optional)* In **Site configuration** → **Environment variables**, you can set:
   - `SECRET_KEY`: `notesvault-secret-key-2026`
   - `MAIL_USERNAME` / `MAIL_PASSWORD` (if you want OTP password reset emails)
6. Click **"Deploy site"**.

---

## 🧪 Step 3: Test Your App
1. Open your published Netlify URL (e.g., `https://your-site-name.netlify.app`).
2. Click **Register** to create a user account.
3. Log in, create notes, and test editing or deleting!

---

> [!NOTE]
> **Serverless Storage Note:**
> In Netlify's serverless environment, SQLite files are stored in the `/tmp` temporary volume. Files in `/tmp` persist during active browsing, but may reset periodically if the site goes completely idle. If you need permanent, non-resetting storage for free, you can also deploy to **Render.com** (Web Service with persistent disk) or **Railway.app**.
