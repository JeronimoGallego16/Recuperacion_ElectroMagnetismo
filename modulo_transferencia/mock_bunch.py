# =============================================================================
# modulo_transferencia/mock_bunch.py — Datos mock para el Integrante 2
# =============================================================================
#
# PROPÓSITO: Permitir que el Integrante 2 (Booster) desarrolle su módulo
# sin esperar a que el Integrante 1 termine el Linac.
#
# CÓMO USAR (en el código del Integrante 2):
#   from modulo_transferencia import generar_bunch_post_linac
#   bunch = generar_bunch_post_linac(200)
#   # bunch ya es un Bunch con forma (N, 7) listo para usar
#
# NOTA: Una vez que el Integrante 1 termine su módulo, esto ya no se
# usa en el pipeline principal. Queda como respaldo para pruebas aisladas.
# =============================================================================

from common.bunch import Bunch
import numpy as np


def generar_bunch_post_linac(n_particulas=200, seed=42):
    """Genera un Bunch simulando la SALIDA del Linac.

    Las macropartículas siguen una distribución normal (gaussiana) tanto
    en posición como en velocidad. La dispersión transversal (σ_x) y
    longitudinal (σ_z) están ajustadas para que el bunch se vea como un
    paquete compacto y ovalado ('frijolito' de energía), con centro denso
    y extremos difusos.

    Returns
    -------
    Bunch
        con forma (n_particulas, 7)
    """
    if seed is not None:
        np.random.seed(seed)

    datos = np.zeros((n_particulas, 7))

    # Posiciones: distribución elíptica (ovalada)
    # σ_x = 0.05 m  (eje corto, dispersión transversal)
    # σ_z = 0.15 m  (eje largo, dispersión longitudinal a lo largo de la órbita)
    datos[:, 0] = np.random.normal(0, 0.05, n_particulas)      # x
    datos[:, 1] = np.random.normal(0, 1e-4, n_particulas)      # y (vertical, se mantiene apretada)
    datos[:, 2] = np.random.normal(0.5, 0.15, n_particulas)    # z

    # Velocidades: muy poca dispersión para que el bunch no se desfleque
    v_avg = 1e8  # ~0.33c
    datos[:, 3] = np.random.normal(0, 1e3, n_particulas)       # vx
    datos[:, 4] = np.random.normal(0, 1e3, n_particulas)       # vy
    datos[:, 5] = np.random.normal(v_avg, 1e3, n_particulas)   # vz

    # Energía cinética: E = 0.5 * m_e * v²
    v2 = datos[:, 3]**2 + datos[:, 4]**2 + datos[:, 5]**2
    datos[:, 6] = 0.5 * 9.10938356e-31 * v2

    return Bunch(datos)
