from common.bunch import Bunch
import numpy as np


def generar_bunch_post_linac(n_particulas=200, seed=42):
    if seed is not None:
        np.random.seed(seed)

    datos = np.zeros((n_particulas, 7))

    datos[:, 0] = np.random.normal(0, 1e-4, n_particulas)
    datos[:, 1] = np.random.normal(0, 1e-4, n_particulas)
    datos[:, 2] = np.random.normal(0.5, 1e-4, n_particulas)

    v_avg = 1e8
    datos[:, 3] = np.random.normal(0, 1e5, n_particulas)
    datos[:, 4] = np.random.normal(0, 1e5, n_particulas)
    datos[:, 5] = np.random.normal(v_avg, 1e5, n_particulas)

    v2 = datos[:, 3]**2 + datos[:, 4]**2 + datos[:, 5]**2
    datos[:, 6] = 0.5 * 9.10938356e-31 * v2

    return Bunch(datos)
