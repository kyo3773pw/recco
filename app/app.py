from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Diccionario de recomendaciones basado en reglas
recomendaciones = {
    "aplicacion_web": {
        "lenguajes": ["JavaScript", "Python"],
        "frameworks": ["React", "Django", "Flask"],
        "librerias": ["Axios", "Express"]
    },
    "reconocimiento_imagenes": {
        "lenguajes": ["Python"],
        "frameworks": ["TensorFlow", "PyTorch"],
        "librerias": ["OpenCV", "scikit-image"]
    }
}

@app.route('/')
def index():
    return render_template('index.html')

# Ruta para mostrar el dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Ruta para manejar el Login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    # Aquí agregas la lógica para validar al usuario
    return redirect(url_for('dashboard'))

# Ruta para manejar el Registro
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    # Aquí agregas la lógica para registrar al usuario
    return redirect(url_for('dashboard'))

# Página principal de consultas
@app.route('/consultas', methods=['GET'])
def consultas():
    return render_template('consultas.html')

# Procesar la consulta y devolver la recomendación
@app.route('/consultar', methods=['POST'])
def consultar():
    # Recibir la descripción del proyecto desde el formulario
    descripcion = request.form.get('descripcion')
    
    # Lógica de recomendación (aquí puede integrarse tu modelo de Machine Learning o lógica personalizada)
    if "gestión de inventarios" in descripcion.lower():
        lenguaje = "Python"
        framework = "Django"
        librerias = "Pandas, Django Rest Framework, SQLAlchemy"
    elif "chatbot" in descripcion.lower():
        lenguaje = "Python"
        framework = "Flask"
        librerias = "TensorFlow, NLTK, Flask-SocketIO"
    else:
        lenguaje = "JavaScript"
        framework = "React"
        librerias = "Axios, Redux, Bootstrap"
    
    # Enviar la respuesta
    return render_template('consultas.html', resultado={
        "lenguaje": lenguaje,
        "framework": framework,
        "librerias": librerias
    })

# Datos simulados
consultas = [
    {"descripcion": "Aplicación móvil para red social", "fecha": "2024-12-10"},
    {"descripcion": "Plataforma de e-commerce", "fecha": "2024-12-11"},
]

proyectos_guardados = [
    {"proyecto": "Chatbot Application", "fecha": "2024-12-09"},
    {"proyecto": "E-commerce Application", "fecha": "2024-12-10"},
]

# Ruta para el historial
@app.route('/historial')
def historial():
    return render_template('historial.html')

# API para cargar consultas
@app.route('/api/consultas')
def get_consultas():
    return jsonify(consultas)

# API para cargar proyectos guardados
@app.route('/api/guardados')
def get_guardados():
    return jsonify(proyectos_guardados)


# Datos simulados de proyectos
proyectos = {
    'fácil': [
        {"nombre": "Chess Game con JS", "nivel": "Fácil"},
        {"nombre": "Todo List App", "nivel": "Fácil"},
    ],
    'intermedio': [
        {"nombre": "Chatbot Application", "nivel": "Intermedio"},
        {"nombre": "Weather App", "nivel": "Intermedio"},
    ],
    'avanzado': [
        {"nombre": "E-commerce Application", "nivel": "Avanzado"},
        {"nombre": "AI Image Recognition", "nivel": "Avanzado"},
    ]
}

# Ruta para mostrar los proyectos
@app.route('/proyectos')
def proyectos_view():
    return render_template('proyectos.html', proyectos=proyectos)

if __name__ == '__main__':
    app.run(debug=True)