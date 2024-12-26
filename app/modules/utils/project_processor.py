import pandas as pd

def clasificar_dificultad(row):
    """
    Clasifica la dificultad del proyecto basado en sus características
    """
    # Contamos la cantidad de tecnologías usadas
    num_lenguajes = len(str(row['lenguajes']).split(',')) if pd.notna(row['lenguajes']) else 0
    num_frameworks = len(str(row['frameworks']).split(',')) if pd.notna(row['frameworks']) else 0
    num_librerias = len(str(row['librerias']).split(',')) if pd.notna(row['librerias']) else 0
    
    total_tech = num_lenguajes + num_frameworks + num_librerias
    
    if total_tech <= 3:
        return 'fácil'
    elif total_tech <= 6:
        return 'intermedio'
    else:
        return 'avanzado'

def get_proyectos():
    """
    Lee y procesa los proyectos desde el CSV
    """
    try:
        # Leer el CSV con las columnas específicas
        df = pd.read_csv('libraries_frameworks_recommendation_dataset.csv')
        
        # Verificar que las columnas necesarias existen
        required_columns = ['tipo_aplicacion', 'plataforma', 'objetivos', 'lenguajes', 'frameworks', 'librerias']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("El CSV no tiene todas las columnas requeridas")
        
        # Clasificar cada proyecto por dificultad
        df['nivel'] = df.apply(clasificar_dificultad, axis=1)
        
        # Crear diccionario de proyectos por nivel
        proyectos = {
            'fácil': [],
            'intermedio': [],
            'avanzado': []
        }
        
        # Procesar cada fila
        for _, row in df.iterrows():
            proyecto = {
                'nombre': f"{row['tipo_aplicacion']} para {row['plataforma']}",
                'descripcion': row['objetivos'],
                'framework': row['frameworks'] if pd.notna(row['frameworks']) else 'Ninguno',
                'librerias': row['librerias'] if pd.notna(row['librerias']) else 'none'
            }
            proyectos[row['nivel']].append(proyecto)
        
        return proyectos
    except Exception as e:
        print(f"Error al procesar el CSV: {str(e)}")
        return None