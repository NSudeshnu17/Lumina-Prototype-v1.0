"""Lumina RFID — Flask Application Entry Point."""
from flask import Flask
from flask_cors import CORS
from config import SECRET_KEY
from database.init_db import init_db, seed_db
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.salesperson_routes import sp_bp
from routes.billing_routes import billing_bp
from routes.manager_routes import manager_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(sp_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(manager_bp)

@app.route('/api/health')
def health():
    return {"status": "ok", "app": "Lumina RFID"}

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
