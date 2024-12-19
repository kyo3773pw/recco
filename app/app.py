from flask import Flask, session, request, jsonify, render_template, url_for, redirect
from modules.user.user_routes import user_bp
from modules.utils.logger_config import setup_logger
from datetime import timedelta
import secrets
from modules.utils.keywords_extractor import KeywordsExtractor
from modules.utils.recom import BibliotecasRecommender
import pandas as pd
from functools import wraps

# Configuración inicial
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(hours=24)

# Configurar logger
logger = setup_logger()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/proyectos')
def proyectos():
    # Crear diccionario de proyectos organizados por dificultad
    proyectos = {
        'fácil': [
            {
                'nombre': 'Chess Game - JS',
                'descripcion': 'Un juego de ajedrez interactivo desarrollado en JavaScript.',
                'framework': 'JavaScript puro',
                'librerias': 'none',
                'imagen': 'chess.png'
            }
        ],
        'intermedio': [
            {
                'nombre': 'Chatbot Application',
                'descripcion': 'Una aplicación de chatbot utilizando IA para responder preguntas comunes.',
                'framework': 'React',
                'librerias': 'TensorFlow.js, Dialogflow',
                'imagen': 'chatbot.png'
            }
        ],
        'avanzado': [
            {
                'nombre': 'E-Commerce Application',
                'descripcion': 'Una completa aplicación de comercio electrónico.',
                'framework': 'Vue.js, Node.js',
                'librerias': 'Vuex, Axios, Express, Stripe API',
                'imagen': 'e-commerce.png'
            }
        ]
    }
    
    return render_template('proyectos.html', proyectos=proyectos)

@app.route('/consultas', methods=['GET'])
def consultas():
    return render_template('consultas.html')

@app.route('/consultar', methods=['POST'])
def consultar():
    try:
        descripcion = request.form.get('descripcion')
        if not descripcion:
            return render_template('consultas.html', error="Por favor ingresa una descripción")
            
        # Crear instancia del extractor de palabras clave
        extractor = KeywordsExtractor()
        keywords = extractor.extract_keywords(descripcion)
        
        # Cargar el dataset y crear el recomendador
        df = pd.read_csv('libraries_frameworks_recommendation_dataset.csv')
        recommender = BibliotecasRecommender()
        df_prepared = recommender.prepare_data(df)
        
        # Obtener recomendaciones
        recommendations = recommender.get_recommendations(
            df_prepared,
            tipo_app=keywords['tipo_app'],
            plataforma=keywords['plataforma'],
            objetivo=keywords['objetivo']
        )
        
        # Formatear resultado
        resultado = {
            'lenguaje': ", ".join([lang for lang, _ in recommendations['lenguajes'][:3]]),
            'framework': ", ".join([frame for frame, _ in recommendations['frameworks'][:3]]),
            'librerias': ", ".join([lib for lib, _ in recommendations['librerias'][:3]])
        }
        
        return render_template('consultas.html', resultado=resultado, keywords=keywords)
        
    except Exception as e:
        return render_template('consultas.html', error=f"Error al procesar la consulta: {str(e)}")

@app.route('/historial')
def historial():
    return render_template('historial.html')

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')

# Configurar logger
logger = setup_logger()

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
    app.run(host='0.0.0.0', port=5000)