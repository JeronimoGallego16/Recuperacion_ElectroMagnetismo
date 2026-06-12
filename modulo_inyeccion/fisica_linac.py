import numpy as np
from common.constants import (
    X, Y, Z, VX, VY, VZ, ENERGIA,
    MASA_ELECTRON, CARGA_ELECTRON, VELOCIDAD_LUZ,
)


def simular_linac(bunch, dt=1e-12, pasos=2500, E0=1e6, frecuencia=3e9,
                  fase=np.pi / 4, longitud=1.0):
    bunch = bunch.copy()
    omega = 2 * np.pi * frecuencia
    k = omega / VELOCIDAD_LUZ

    historico = [bunch.copy()]

    for paso in range(pasos):
        t = paso * dt

        E_z = E0 * np.sin(omega * t - k * bunch[:, Z] + fase)

        mascara = np.abs(bunch[:, Z]) < longitud / 2
        a_z = np.where(mascara, CARGA_ELECTRON * E_z / MASA_ELECTRON, 0.0)

        bunch[:, VZ] += a_z * dt
        bunch[:, X] += bunch[:, VX] * dt
        bunch[:, Y] += bunch[:, VY] * dt
        bunch[:, Z] += bunch[:, VZ] * dt

        v2 = bunch[:, VX]**2 + bunch[:, VY]**2 + bunch[:, VZ]**2
        bunch[:, ENERGIA] = 0.5 * MASA_ELECTRON * v2

        historico.append(bunch.copy())

    return historico
