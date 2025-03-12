# -*- coding: utf-8 -*-
"""Calcular Media y Desviación

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1hNXa_jv7AurE28EZPJgoDJqzGjOpvqe8
"""

import pandas as pd

# Cargar el archivo
file_path = "prueba0.txt"

# Leer el archivo, asumiendo que los valores están separados por tabulaciones
df = pd.read_csv(file_path, sep="\t")

# Calcular la media y la desviación estándar de la columna "Voltaje_V"
media = df["Voltaje_V"].mean()
desviacion_std = df["Voltaje_V"].std()

print(f"Media del voltaje: {media:.5f} V")
print(f"Desviación estándar del voltaje: {desviacion_std:.5f} V")