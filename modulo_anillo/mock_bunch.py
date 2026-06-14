"""
modulo_anillo/mock_bunch.py — Datos mock para el Integrante 3


PROPÓSITO: Permitir que el Integrante 3 (Ring) desarrolle su módulo
sin esperar a que los Integrantes 1 y 2 terminen.

CÓMO USAR (en el código del Integrante 3):
   from modulo_anillo import generar_bunch_post_booster
   bunch = generar_bunch_post_booster(200)
   bunch ya es un Bunch con forma (N, 7) listo para usar

NOTA: Una vez que los otros módulos estén listos, esto ya no se
usa en el pipeline principal. Queda como respaldo para pruebas aisladas.
"""

from common.bunch import Bunch
import numpy as np


def generar_bunch_post_booster(n_particulas=200, seed=42):
    """Genera un Bunch simulando la SALIDA del Booster.

    Simula electrones que ya completaron la órbita del Booster:
      - Distribuidos en un círculo de radio 1.0 m (órbita del booster)
      - Alta velocidad tangencial (v ~ 2e8 m/s ≈ 0.67c)
      - Pequeña dispersión gaussiana alrededor de la órbita ideal
      - Velocidades principalmente en el plano xy (tangenciales)

    Returns
    -------
    Bunch
        con forma (n_particulas, 7)
    """
    if seed is not None:
        np.random.seed(seed)

    datos = np.zeros((n_particulas, 7))

    # Posiciones: distribuidas en un círculo de radio 1.0 m
    radio = 1.0
    angulos = np.random.uniform(0, 2 * np.pi, n_particulas)
    datos[:, 0] = radio * np.cos(angulos) + np.random.normal(0, 2e-3, n_particulas)  # x
    datos[:, 1] = radio * np.sin(angulos) + np.random.normal(0, 2e-3, n_particulas)  # y
    datos[:, 2] = np.random.normal(0, 1e-3, n_particulas)   # z (pequeña dispersión)

    # Velocidades: tangenciales al círculo (perpendiculares al radio)
    v_avg = 2e8  # ~0.67c
    datos[:, 3] = -v_avg * np.sin(angulos) + np.random.normal(0, 1e5, n_particulas)  # vx
    datos[:, 4] = v_avg * np.cos(angulos) + np.random.normal(0, 1e5, n_particulas)   # vy
    datos[:, 5] = np.random.normal(0, 1e5, n_particulas)    # vz

    # Energía cinética: E = 0.5 * m_e * v²
    v2 = datos[:, 3]**2 + datos[:, 4]**2 + datos[:, 5]**2
    datos[:, 6] = 0.5 * 9.10938356e-31 * v2

    return Bunch(datos)
