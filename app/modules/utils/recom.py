import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
import implicit
from ast import literal_eval
from collections import Counter
from sklearn.preprocessing import LabelEncoder

class ImplicitRecommender:
    def __init__(self, factors=50, regularization=0.01, alpha=40):
        self.factors = factors
        self.regularization = regularization
        self.alpha = alpha
        self.le_apps = LabelEncoder()
        self.le_platforms = LabelEncoder()
        self.le_objectives = LabelEncoder()
        self.model = implicit.als.AlternatingLeastSquares(
            factors=factors,
            regularization=regularization,
            iterations=50,
            random_state=42
        )

    def prepare_data(self, df):
        # Convertir las listas string a listas reales
        df['lenguajes'] = df['lenguajes'].apply(literal_eval)
        df['frameworks'] = df['frameworks'].apply(literal_eval)
        df['librerias'] = df['librerias'].apply(literal_eval)

        # Codificar variables categóricas
        df['app_id'] = self.le_apps.fit_transform(df['tipo_aplicacion'])
        df['platform_id'] = self.le_platforms.fit_transform(df['plataforma'])
        df['objective_id'] = self.le_objectives.fit_transform(df['objetivos'])

        return df

    def create_interaction_matrix(self, df):
        """
        Crea una matriz de interacción sparse considerando la cantidad de tecnologías
        como señal de confianza implícita
        """
        n_apps = len(self.le_apps.classes_)
        n_contexts = len(self.le_platforms.classes_) * len(self.le_objectives.classes_)
        
        # Inicializar listas para crear matriz sparse
        rows = []
        cols = []
        data = []
        
        for _, row in df.iterrows():
            app_idx = row['app_id']
            platform_idx = row['platform_id']
            objective_idx = row['objective_id']
            
            # Crear índice combinado para plataforma y objetivo
            context_idx = platform_idx * len(self.le_objectives.classes_) + objective_idx
            
            # Calcular score basado en cantidad de tecnologías
            confidence = (len(row['lenguajes']) + 
                        len(row['frameworks']) + 
                        len(row['librerias'])) / 3.0
                        
            # Aplicar transformación alpha
            confidence = 1.0 + self.alpha * confidence
            
            rows.append(app_idx)
            cols.append(context_idx)
            data.append(confidence)
        
        # Crear matriz sparse
        matrix = csr_matrix((data, (rows, cols)), 
                          shape=(n_apps, n_contexts))
        
        return matrix

    def get_most_common_tech(self, df, tipo_app, plataforma, objetivo, column):
        """
        Obtiene las tecnologías más comunes para una combinación específica
        """
        mask = (
            (df['tipo_aplicacion'] == tipo_app) &
            (df['plataforma'] == plataforma) &
            (df['objetivos'] == objetivo)
        )
        
        filtered_df = df[mask]
        
        if filtered_df.empty:
            # Si no hay coincidencias exactas, buscar similares
            similar_mask = (
                (df['tipo_aplicacion'] == tipo_app) |
                (df['plataforma'] == plataforma) |
                (df['objetivos'] == objetivo)
            )
            filtered_df = df[similar_mask]
        
        # Contar frecuencias
        tech_counter = Counter()
        for techs in filtered_df[column]:
            tech_counter.update(techs)
            
        return tech_counter.most_common()

    def train(self, interaction_matrix):
        """
        Entrena el modelo ALS
        """
        # Convertir a formato COO para implicit
        interaction_matrix_coo = interaction_matrix.tocoo()
        
        # Entrenar modelo
        self.model.fit(interaction_matrix_coo)

    def get_recommendations(self, df, tipo_app, plataforma, objetivo, top_n=5):
        """
        Obtiene recomendaciones completas usando el modelo entrenado y la frecuencia
        de tecnologías
        """
        # Obtener IDs
        try:
            app_id = self.le_apps.transform([tipo_app])[0]
            platform_id = self.le_platforms.transform([plataforma])[0]
            objective_id = self.le_objectives.transform([objetivo])[0]
        except ValueError:
            # Si alguna categoría es nueva, usar las tecnologías más comunes generales
            return {
                'lenguajes': self.get_most_common_tech(df, tipo_app, plataforma, objetivo, 'lenguajes')[:top_n],
                'frameworks': self.get_most_common_tech(df, tipo_app, plataforma, objetivo, 'frameworks')[:top_n],
                'librerias': self.get_most_common_tech(df, tipo_app, plataforma, objetivo, 'librerias')[:top_n]
            }

        # Obtener recomendaciones basadas en tecnologías más comunes
        recommended_languages = self.get_most_common_tech(df, tipo_app, plataforma, objetivo, 'lenguajes')
        recommended_frameworks = self.get_most_common_tech(df, tipo_app, plataforma, objetivo, 'frameworks')
        recommended_libraries = self.get_most_common_tech(df, tipo_app, plataforma, objetivo, 'librerias')

        return {
            'lenguajes': [(lang, count) for lang, count in recommended_languages[:top_n]],
            'frameworks': [(framework, count) for framework, count in recommended_frameworks[:top_n]],
            'librerias': [(lib, count) for lib, count in recommended_libraries[:top_n]]
        }

def format_recommendations(recommendations):
    """
    Formatea las recomendaciones para una mejor visualización
    """
    output = []
    
    output.append("\nLenguajes de programación recomendados:")
    for lang, count in recommendations['lenguajes']:
        output.append(f"- {lang} (usado {count} veces)")
    
    output.append("\nFrameworks recomendados:")
    for framework, count in recommendations['frameworks']:
        output.append(f"- {framework} (usado {count} veces)")
    
    output.append("\nLibrerías recomendadas:")
    for lib, count in recommendations['librerias']:
        output.append(f"- {lib} (usado {count} veces)")
    
    return "\n".join(output)

def main():
    # Cargar datos
    df = pd.read_csv('libraries_frameworks_recommendation_dataset.csv')
    
    # Crear y entrenar recomendador
    recommender = ImplicitRecommender(factors=50, regularization=0.01, alpha=40)
    df_prepared = recommender.prepare_data(df)
    interaction_matrix = recommender.create_interaction_matrix(df_prepared)
    recommender.train(interaction_matrix)
    
    # Ejemplo de uso
    tipo_app = "web"
    plataforma = "pc"
    objetivo = "e-commerce"
    
    recommendations = recommender.get_recommendations(
        df_prepared,
        tipo_app=tipo_app,
        plataforma=plataforma,
        objetivo=objetivo,
        top_n=5
    )
    
    print(f"\nRecomendaciones para {tipo_app} en {plataforma} para {objetivo}:")
    print(format_recommendations(recommendations))

if __name__ == "__main__":
    main()