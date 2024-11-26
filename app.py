from flask import Flask, render_template, request

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

@app.route('/recomendar', methods=['POST'])
def recomendar():
    tipo_proyecto = request.form.get('tipo_proyecto')
    recomendaciones_proyecto = recomendaciones.get(tipo_proyecto, {})
    return render_template('result.html', tipo_proyecto=tipo_proyecto, recomendaciones=recomendaciones_proyecto)

if __name__ == '__main__':
    app.run(debug=True)