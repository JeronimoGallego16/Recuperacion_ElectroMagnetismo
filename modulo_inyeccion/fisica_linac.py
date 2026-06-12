import numpy as np
from common.constants import (
    X, Y, Z, VX, VY, VZ, ENERGIA,
    MASA_ELECTRON, CARGA_ELECTRON, VELOCIDAD_LUZ,
)
from common.bunch import Bunch


class Linac:
    def __init__(self, E0=1e6, frecuencia=3e9, fase=np.pi / 4, longitud=1.0):
        self.E0 = E0
        self.frecuencia = frecuencia
        self.fase = fase
        self.longitud = longitud
        self.omega = 2 * np.pi * frecuencia
        self.k = self.omega / VELOCIDAD_LUZ

    def simular(self, bunch, dt=1e-12, pasos=2500):
        datos = bunch.datos.copy()
        historico = [Bunch(datos.copy())]

        for paso in range(pasos):
            t = paso * dt

            E_z = self.E0 * np.sin(self.omega * t - self.k * datos[:, Z] + self.fase)

            mascara = np.abs(datos[:, Z]) < self.longitud / 2
            a_z = np.where(mascara, CARGA_ELECTRON * E_z / MASA_ELECTRON, 0.0)

            datos[:, VZ] += a_z * dt
            datos[:, X] += datos[:, VX] * dt
            datos[:, Y] += datos[:, VY] * dt
            datos[:, Z] += datos[:, VZ] * dt

            v2 = datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2
            datos[:, ENERGIA] = 0.5 * MASA_ELECTRON * v2

            historico.append(Bunch(datos.copy()))

        return historico
