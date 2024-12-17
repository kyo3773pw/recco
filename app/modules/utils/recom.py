import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
from sklearn.preprocessing import LabelEncoder
from ast import literal_eval
from collections import Counter

class BibliotecasRecommender:
    def __init__(self):
        self.le_apps = LabelEncoder()
        self.le_platforms = LabelEncoder()
        self.le_objectives = LabelEncoder()

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
        # Crear matriz de interacción basada en coincidencias de tecnologías
        n_apps = len(self.le_apps.classes_)
        n_platforms = len(self.le_platforms.classes_)
        n_objectives = len(self.le_objectives.classes_)

        interaction_matrix = np.zeros((n_apps, n_platforms * n_objectives))

        for _, row in df.iterrows():
            app_idx = row['app_id']
            platform_idx = row['platform_id']
            objective_idx = row['objective_id']

            # Combinar plataforma y objetivo como un único índice
            combined_idx = platform_idx * n_objectives + objective_idx

            # Aumentar la interacción basada en el número de tecnologías usadas
            interaction_score = (len(row['lenguajes']) +
                              len(row['frameworks']) +
                              len(row['librerias'])) / 3.0

            interaction_matrix[app_idx, combined_idx] = interaction_score

        return interaction_matrix

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
            similar_mask = (
                (df['tipo_aplicacion'] == tipo_app) |
                (df['plataforma'] == plataforma) |
                (df['objetivos'] == objetivo)
            )
            filtered_df = df[similar_mask]

        # Contar frecuencias de tecnologías
        tech_counter = Counter()
        for techs in filtered_df[column]:
            tech_counter.update(techs)

        return tech_counter.most_common()

    def train(self, interaction_matrix):
        # Calcular el número óptimo de factores
        min_dim = min(interaction_matrix.shape)
        n_factors = min(3, min_dim - 1)

        # Aplicar SVD
        U, sigma, Vt = svds(interaction_matrix, k=n_factors)

        # Convertir sigma a matriz diagonal
        sigma = np.diag(sigma)

        # Guardar las matrices factorizadas
        self.U = U
        self.sigma = sigma
        self.Vt = Vt

    def get_recommendations(self, df, tipo_app, plataforma, objetivo, top_n=5):
        """
        Obtiene recomendaciones completas incluyendo lenguajes, frameworks y librerías
        """
        # Obtener tecnologías recomendadas
        recommended_languages = self.get_most_common_tech(df, tipo_app, plataforma, objetivo, 'lenguajes')
        recommended_frameworks = self.get_most_common_tech(df, tipo_app, plataforma, objetivo, 'frameworks')
        recommended_libraries = self.get_most_common_tech(df, tipo_app, plataforma, objetivo, 'librerias')

        recommendations = {
            'lenguajes': [(lang, count) for lang, count in recommended_languages[:top_n]],
            'frameworks': [(framework, count) for framework, count in recommended_frameworks[:top_n]],
            'librerias': [(lib, count) for lib, count in recommended_libraries[:top_n]]
        }

        return recommendations

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
    df = pd.read_csv('libraries_frameworks_recommendation_dataset.csv')
    recommender = BibliotecasRecommender()
    df_prepared = recommender.prepare_data(df)
    interaction_matrix = recommender.create_interaction_matrix(df_prepared)
    recommender.train(interaction_matrix)
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