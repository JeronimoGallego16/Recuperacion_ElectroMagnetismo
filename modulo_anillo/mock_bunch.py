from common.bunch import Bunch
import numpy as np


def generar_bunch_post_booster(n_particulas=200, seed=42):
    if seed is not None:
        np.random.seed(seed)

    datos = np.zeros((n_particulas, 7))

    radio = 1.0
    angulos = np.random.uniform(0, 2 * np.pi, n_particulas)
    datos[:, 0] = radio * np.cos(angulos) + np.random.normal(0, 2e-3, n_particulas)
    datos[:, 1] = radio * np.sin(angulos) + np.random.normal(0, 2e-3, n_particulas)
    datos[:, 2] = np.random.normal(0, 1e-3, n_particulas)

    v_avg = 2e8
    datos[:, 3] = -v_avg * np.sin(angulos) + np.random.normal(0, 1e5, n_particulas)
    datos[:, 4] = v_avg * np.cos(angulos) + np.random.normal(0, 1e5, n_particulas)
    datos[:, 5] = np.random.normal(0, 1e5, n_particulas)

    v2 = datos[:, 3]**2 + datos[:, 4]**2 + datos[:, 5]**2
    datos[:, 6] = 0.5 * 9.10938356e-31 * v2

    return Bunch(datos)
