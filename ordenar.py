import pandas as pd

# Carga el archivo con ambas hojas
archivo = r"C:\Users\Juan\Downloads\Auditoria el 7 Auxiliares de Surtido.xlsx"
evaluados = pd.read_excel(archivo, sheet_name="Evaluados")
evaluadores = pd.read_excel(archivo, sheet_name="Evaluadores")

# Solo dejamos las columnas necesarias
evaluados = evaluados[['Tienda', 'Nomina']].rename(columns={'Nomina': 'Evaluado'})
evaluadores = evaluadores[['Tienda', 'Nomina']].rename(columns={'Nomina': 'Evaluador'})

# Paso nuevo: agregamos autoevaluaciones
autoevals = evaluados.copy()
autoevals = autoevals.rename(columns={'Evaluado': 'Evaluador'})
autoevals['Evaluado'] = autoevals['Evaluador']  # Evaluador y Evaluado son iguales

# Hacemos un merge cruzado por tienda
resultado = pd.merge(evaluados, evaluadores, on="Tienda", how="inner")

# Filtramos para evitar autoevaluaciones en el merge cruzado
resultado = resultado[resultado['Evaluado'] != resultado['Evaluador']]

# Unimos el resultado con las autoevaluaciones
resultado_final = pd.concat([resultado, autoevals], ignore_index=True)

# Guardamos el resultado
resultado_final.to_excel(r"C:\Users\Juan\Downloads\Auditoria el 7 Auxiliares de Surtido1.xlsx", index=False)
