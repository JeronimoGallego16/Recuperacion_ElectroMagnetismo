"""
common/constants.py — Constantes físicas e índices de la matriz bunch

Este archivo lo usan TODOS los integrantes del equipo. No modificar sin
consultar al equipo completo.

MATRIZ BUNCH (acuerdo del equipo):
   Cada fila = un electrón
   Columnas: [x, y, z, vx, vy, vz, energia]
   Índices:   0  1  2   3   4   5     6
"""

import numpy as np


# Constantes físicas fundamentales (SI)
MASA_ELECTRON = 9.10938356e-31      # kg
CARGA_ELECTRON = 1.602176634e-19    # C (valor absoluto)
VELOCIDAD_LUZ = 2.99792458e8        # m/s
ENERGIA_REPOSO_EV = 511e3           # 511 keV = energía en reposo del electrón

"""
 Índices de columnas de la matriz bunch (N, 7)
 Usar:  bunch[:, X]  en lugar de  bunch[:, 0]  para que el código sea legible
 """
X = 0       # Posición x (m)
Y = 1       # Posición y (m)
Z = 2       # Posición z (m) — eje longitudinal del acelerador
VX = 3      # Velocidad x (m/s)
VY = 4      # Velocidad y (m/s)
VZ = 5      # Velocidad z (m/s)
ENERGIA = 6 # Energía cinética (J)
