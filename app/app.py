from flask import Flask, session
from modules.user.user_routes import user_bp
from modules.utils.logger_config import setup_logger
from datetime import timedelta
import secrets

# Configuración inicial
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Genera una clave secreta segura
app.permanent_session_lifetime = timedelta(hours=24)

# Configurar logger
logger = setup_logger()

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')

# Configuración de sesión
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
)

# Middleware para logging de requests
@app.before_request
def log_request_info():
    logger.info(f'Request: {request.method} {request.path}')

# Manejo de errores
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f'Page not found: {request.url}')
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Server Error: {error}')
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)