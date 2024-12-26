from flask import Flask, session, request, jsonify, render_template, url_for, redirect, flash
from modules.user.user_routes import user_bp
from modules.utils.logger_config import setup_logger
from datetime import timedelta
import secrets
from modules.utils.keywords_extractor import KeywordsExtractor
from modules.utils.recom import ImplicitRecommender
import pandas as pd
from functools import wraps
from modules.utils.project_processor import get_proyectos

# Configuración inicial
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(hours=24)

# Configurar logger
logger = setup_logger()

# Inicializar el recomendador globalmente
try:
    df = pd.read_csv('libraries_frameworks_recommendation_dataset.csv')
    recommender = ImplicitRecommender(factors=50, regularization=0.01, alpha=40)
    df_prepared = recommender.prepare_data(df)
    interaction_matrix = recommender.create_interaction_matrix(df_prepared)
    recommender.train(interaction_matrix)
    logger.info("Recommendation system initialized successfully")
except Exception as e:
    logger.error(f"Error initializing recommendation system: {str(e)}")
    recommender = None
    df_prepared = None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if 'user_id' not in session:
                logger.warning(f"Unauthorized access attempt to {request.path}")
                flash('Por favor inicie sesión para acceder a esta página')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in auth middleware: {str(e)}")
            return redirect(url_for('index'))
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/proyectos')
def proyectos():
    try:
        proyectos_csv = get_proyectos()
        proyectos = proyectos_csv if proyectos_csv is not None else {
            'fácil': [],
            'intermedio': [],
            'avanzado': []
        }
        return render_template('proyectos.html', proyectos=proyectos)
    except Exception as e:
        logger.error(f"Error loading projects: {str(e)}")
        return render_template('proyectos.html', error="Error al cargar los proyectos")

@app.route('/consultas', methods=['GET'])
def consultas():
    return render_template('consultas.html')

@app.route('/consultar', methods=['POST'])
def consultar():
    try:
        if recommender is None or df_prepared is None:
            return render_template('consultas.html', 
                                error="Sistema de recomendación no disponible")

        descripcion = request.form.get('descripcion')
        if not descripcion:
            return render_template('consultas.html', 
                                error="Por favor ingresa una descripción")
            
        # Extraer palabras clave
        extractor = KeywordsExtractor()
        keywords = extractor.extract_keywords(descripcion)
        confidence_scores = extractor.get_confidence_scores(descripcion)
        
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
        
        return render_template(
            'consultas.html', 
            resultado=resultado, 
            keywords=keywords,
            confidence_scores=confidence_scores
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return render_template('consultas.html', 
                             error=f"Error al procesar la consulta: {str(e)}")

@app.route('/historial')
def historial():
    return render_template('historial.html')

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')

# Configuración de sesión
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
)

# Middleware para logging
@app.before_request
def log_request_info():
    logger.info(f'Request: {request.method} {request.path}')

# Manejo de errores
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f'Page not found: {request.url}')
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)