import re
from collections import defaultdict
from typing import Dict

class KeywordsExtractor:
    def __init__(self):
        # Palabras clave actualizadas y expandidas para cada categoría
        self.tipo_app_keywords = {
            'web': ['web', 'sitio', 'página', 'website', 'portal', 'webapp', 'aplicación web', 'spa', 'pwa'],
            'mobile': ['móvil', 'mobile', 'android', 'ios', 'app', 'aplicación móvil', 'smartphone', 'tablet', 'celular'],
            'desktop': ['escritorio', 'desktop', 'windows', 'mac', 'linux', 'aplicación de escritorio', 'programa', 'software']
        }
        
        self.plataforma_keywords = {
            'pc': ['pc', 'windows', 'mac', 'linux', 'desktop', 'escritorio', 'computadora', 'ordenador'],
            'web': ['navegador', 'web', 'online', 'internet', 'chrome', 'firefox', 'safari', 'edge'],
            'mobile': ['android', 'ios', 'móvil', 'smartphone', 'teléfono', 'tablet', 'ipad', 'app store', 'play store']
        }
        
        self.objetivo_keywords = {
            'e-commerce': ['tienda', 'comercio', 'venta', 'e-commerce', 'ecommerce', 'productos', 'carrito', 'pago', 'marketplace'],
            'educacion': ['educación', 'aprendizaje', 'curso', 'enseñanza', 'academia', 'escuela', 'universidad', 'lms'],
            'entretenimiento': ['juego', 'entretenimiento', 'multimedia', 'video', 'música', 'streaming', 'social'],
            'productividad': ['gestión', 'administración', 'productividad', 'organización', 'workflow', 'dashboard', 'análisis']
        }

    def preprocess_text(self, texto: str) -> str:
        """
        Preprocesa el texto para mejorar la extracción de palabras clave
        """
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Remover caracteres especiales manteniendo espacios
        texto = re.sub(r'[^\w\s]', ' ', texto)
        
        # Remover espacios múltiples
        texto = re.sub(r'\s+', ' ', texto)
        
        return texto.strip()

    def calculate_category_score(self, texto: str, keywords_dict: Dict[str, list]) -> Dict[str, float]:
        """
        Calcula un score ponderado para cada categoría basado en la presencia de palabras clave
        """
        scores = defaultdict(float)
        words = set(texto.split())
        
        for category, keywords in keywords_dict.items():
            # Calcular coincidencias exactas
            exact_matches = sum(1 for keyword in keywords if keyword in texto)
            
            # Calcular coincidencias parciales (palabras individuales)
            partial_matches = sum(1 for word in words for keyword in keywords 
                                if word in keyword.split() or keyword in word)
            
            # Combinar scores con diferentes pesos
            scores[category] = exact_matches * 1.0 + partial_matches * 0.5
            
        return scores

    def extract_keywords(self, texto: str) -> Dict[str, str]:
        """
        Extrae y clasifica el texto en las diferentes categorías
        """
        # Preprocesar texto
        processed_texto = self.preprocess_text(texto)
        
        # Calcular scores para cada categoría
        tipo_app_scores = self.calculate_category_score(processed_texto, self.tipo_app_keywords)
        plataforma_scores = self.calculate_category_score(processed_texto, self.plataforma_keywords)
        objetivo_scores = self.calculate_category_score(processed_texto, self.objetivo_keywords)
        
        # Seleccionar la mejor categoría para cada tipo
        resultados = {
            'tipo_app': max(tipo_app_scores.items(), key=lambda x: x[1])[0] if tipo_app_scores else 'web',
            'plataforma': max(plataforma_scores.items(), key=lambda x: x[1])[0] if plataforma_scores else 'pc',
            'objetivo': max(objetivo_scores.items(), key=lambda x: x[1])[0] if objetivo_scores else 'productividad'
        }
        
        return resultados

    def get_confidence_scores(self, texto: str) -> Dict[str, Dict[str, float]]:
        """
        Retorna los scores de confianza para cada categoría
        """
        processed_texto = self.preprocess_text(texto)
        
        return {
            'tipo_app': dict(self.calculate_category_score(processed_texto, self.tipo_app_keywords)),
            'plataforma': dict(self.calculate_category_score(processed_texto, self.plataforma_keywords)),
            'objetivo': dict(self.calculate_category_score(processed_texto, self.objetivo_keywords))
        }