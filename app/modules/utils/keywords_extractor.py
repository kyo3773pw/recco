import re
from collections import defaultdict

class KeywordsExtractor:
    def __init__(self):
        # Definir palabras clave para cada categoría
        self.tipo_app_keywords = {
            'web': ['web', 'sitio', 'página', 'website', 'portal'],
            'mobile': ['móvil', 'mobile', 'android', 'ios', 'app', 'aplicación móvil'],
            'desktop': ['escritorio', 'desktop', 'windows', 'mac', 'aplicación de escritorio']
        }
        
        self.plataforma_keywords = {
            'pc': ['pc', 'windows', 'mac', 'desktop', 'escritorio'],
            'web': ['navegador', 'web', 'online', 'internet'],
            'mobile': ['android', 'ios', 'móvil', 'smartphone', 'teléfono']
        }
        
        self.objetivo_keywords = {
            'e-commerce': ['tienda', 'comercio', 'venta', 'e-commerce', 'ecommerce', 'productos'],
            'educacion': ['educación', 'aprendizaje', 'curso', 'enseñanza'],
            'entretenimiento': ['juego', 'entretenimiento', 'multimedia'],
            'productividad': ['gestión', 'administración', 'productividad', 'organización']
        }

    def extract_keywords(self, texto):
        texto = texto.lower()
        resultados = {
            'tipo_app': 'web',  # valor por defecto
            'plataforma': 'pc',  # valor por defecto
            'objetivo': 'productividad'  # valor por defecto
        }
        
        # Contar coincidencias para cada categoría
        for categoria, keywords_dict in [
            ('tipo_app', self.tipo_app_keywords),
            ('plataforma', self.plataforma_keywords),
            ('objetivo', self.objetivo_keywords)
        ]:
            max_coincidencias = 0
            mejor_match = None
            
            for tipo, keywords in keywords_dict.items():
                coincidencias = sum(1 for keyword in keywords if keyword in texto)
                if coincidencias > max_coincidencias:
                    max_coincidencias = coincidencias
                    mejor_match = tipo
            
            if mejor_match:
                resultados[categoria] = mejor_match
        
        return resultados