import numpy as np
from common.constants import (
    X, Y, Z, VX, VY, VZ, ENERGIA,
    MASA_ELECTRON,
)


class Bunch:
    def __init__(self, datos=None, n_particulas=0):
        if datos is not None:
            self.datos = np.asarray(datos, dtype=float)
        else:
            self.datos = np.zeros((n_particulas, 7))

    @property
    def x(self): return self.datos[:, X]
    @property
    def y(self): return self.datos[:, Y]
    @property
    def z(self): return self.datos[:, Z]
    @property
    def vx(self): return self.datos[:, VX]
    @property
    def vy(self): return self.datos[:, VY]
    @property
    def vz(self): return self.datos[:, VZ]
    @property
    def energia(self): return self.datos[:, ENERGIA]

    @property
    def n_particulas(self):
        return self.datos.shape[0]

    def copia(self):
        return Bunch(self.datos.copy())

    def actualizar_energia(self):
        v2 = self.vx**2 + self.vy**2 + self.vz**2
        self.datos[:, ENERGIA] = 0.5 * MASA_ELECTRON * v2

    @classmethod
    def generar_inicial(cls, n_particulas=200, sigma_pos=5e-4, sigma_vel=5e5,
                        v0_axial=1e7, seed=None):
        if seed is not None:
            np.random.seed(seed)

        datos = np.zeros((n_particulas, 7))

        datos[:, X] = np.random.normal(0, sigma_pos, n_particulas)
        datos[:, Y] = np.random.normal(0, sigma_pos, n_particulas)
        datos[:, Z] = np.random.normal(0, sigma_pos * 2, n_particulas)

        datos[:, VX] = np.random.normal(0, sigma_vel, n_particulas)
        datos[:, VY] = np.random.normal(0, sigma_vel, n_particulas)
        datos[:, VZ] = np.random.normal(v0_axial, sigma_vel, n_particulas)

        v2 = datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2
        datos[:, ENERGIA] = 0.5 * MASA_ELECTRON * v2

        return cls(datos)
