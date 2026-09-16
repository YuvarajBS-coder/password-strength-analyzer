# Password Strength Analyzer — Complete College Project

## Objective
Develop a tool that evaluates the strength of user-entered passwords based on length, complexity, uniqueness and password-history reuse.

## Main features
- Password length analysis
- Lowercase, uppercase, number and special-character checks
- Common-password detection
- Repeated-character and obvious-sequence detection
- Strength rating and visual meter
- Suggestions to improve weak passwords
- Secure password generator using Python `secrets`
- SQLite password history
- User ID based reuse detection
- Salted PBKDF2-HMAC-SHA256 password-history storage
- No plaintext password is stored in the database

## Folder structure
```
Password_Strength_Analyzer_Complete/
├── app.py
├── requirements.txt
├── README.md
├── password_history.db   (created automatically on first run)
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## Run in VS Code
Open this folder in VS Code, then Terminal → New Terminal.

```powershell
pip install -r requirements.txt
python app.py
```

Open:
`http://127.0.0.1:5000`

## Demonstration
1. Enter User ID: `student01`
2. Test `123456`
3. Test `Hello123`
4. Test `R7!mQ2#vL9@xT4$p`
5. Click **Check & Save to History** for the strong password.
6. Enter the same password again. The analyzer will show a reuse warning.
7. Generate a new password with the generator.

## Technologies
- Python
- Flask
- HTML5
- CSS3
- JavaScript
- SQLite
- hashlib PBKDF2-HMAC-SHA256
- secrets module

## Important security note
This is an educational project. The analyzer does not replace a production password-strength library. For real authentication systems, use a dedicated password hashing algorithm such as Argon2id, scrypt or bcrypt and follow current security guidance.

## Viva short explanation
"The system has a web frontend and Flask backend. JavaScript sends the entered password to the Flask server. The backend checks length, character classes, common patterns and uniqueness, then returns a strength score. SQLite maintains password history. For reuse checking, the system stores a random salt and PBKDF2-HMAC-SHA256 hash rather than the plaintext password. A new password is compared against each stored history hash for that user. The generator uses Python's secrets module for security-oriented random generation."

## Future enhancements
- Larger breached-password dataset/API using privacy-preserving k-anonymity
- Entropy estimation
- Rate limiting and authentication
- Automated unit/integration tests
- Production deployment with a WSGI server
