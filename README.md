# NotesVault — Notes Management System (Flask + MySQL)

A full-stack notes app with secure authentication, full CRUD, a realistic
3D-animated login/register experience, and animated 3D note cards.

## ✨ Features
- Register / Login / Logout / Forgot & Reset Password
- Password hashing with Werkzeug
- Full CRUD on notes, scoped per-user (private workspace)
- 3D animated login/register scene (rotating cube, pyramid, sphere, ring)
- Mouse-tilt (parallax) glassmorphism auth card
- Animated "Welcome to Notes" banner with confetti on login
- 3D hover-tilt note cards with view / edit / delete actions
- Delete confirmation modal
- Responsive Bootstrap 5 navbar, footer, and About/Admin page

## 🗂 Project Structure
```
notes_app/
├── app.py                  # Flask application & routes
├── schema.sql               # MySQL schema (users, notes)
├── requirements.txt
├── static/
│   ├── css/style.css        # All 3D / glass styling
│   └── js/
│       ├── script.js        # Flash-message auto-dismiss
│       ├── login3d.js       # Auth card tilt + parallax shapes
│       └── dashboard3d.js   # Confetti + note card tilt
└── templates/
    ├── base.html, navbar.html, footer.html
    ├── login.html, register.html
    ├── forgot_password.html, reset_password.html
    ├── dashboard.html, add_note.html, view_note.html, update_note.html
    └── about.html
```

## ⚙️ Setup

1. **Create a virtual environment & install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create the MySQL database**
   ```bash
   mysql -u root -p < schema.sql
   ```

3. **Configure database credentials & environment variables**
   Copy `.env.example` to `.env` and configure your database and email credentials:
   ```bash
   copy .env.example .env     # Windows
   cp .env.example .env       # Linux / macOS
   ```
   Or edit the environment variables in `.env`.

4. **Run the app locally**
   ```bash
   python app.py
   ```
   Visit **http://127.0.0.1:5000** in your browser.

## 🚀 Deployment (Netlify & Cloud)
For complete instructions on deploying to **Netlify** (via Netlify Functions and cloud MySQL) or **Render/Railway**, see [DEPLOYMENT.md](DEPLOYMENT.md).


## 🔐 Notes on the "Forgot Password" flow
For simplicity/demo purposes this project verifies identity using
**username + registered email** rather than sending a real email with a
reset link. If you want production-grade password recovery, wire in
**Flask-Mail** to send a tokenized reset link instead of the current
verify-then-reset flow — the route structure (`/forgot-password` →
`/reset-password`) is already set up to make that swap straightforward.

## 🧑‍💻 Route Map
| Feature       | Route                     | Method    |
|---------------|---------------------------|-----------|
| Register      | `/register`                | GET/POST |
| Login         | `/login`                   | GET/POST |
| Forgot Pass   | `/forgot-password`         | GET/POST |
| Reset Pass    | `/reset-password`          | GET/POST |
| Logout        | `/logout`                  | GET      |
| View all notes| `/dashboard` or `/viewall` | GET      |
| Add note      | `/addnote`                 | GET/POST |
| View one note | `/viewnotes/<id>`          | GET      |
| Update note   | `/updatenote/<id>`         | GET/POST |
| Delete note   | `/deletenote/<id>`         | GET      |
| About         | `/about`                   | GET      |

## 🎨 Customizing the theme
All colors and gradients live at the top of `static/css/style.css` inside
the `:root { ... }` block — change `--primary`, `--accent`, `--accent2`
etc. to restyle the entire app in one place.

Enjoy, and feel free to extend it (e.g. tags, search, note colors,
dark/light toggle, pagination) — the structure is intentionally modular.
