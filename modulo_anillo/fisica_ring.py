"""
modulo_anillo/fisica_ring.py

Módulo del Storage Ring.

Este módulo recibe el bunch que sale del Booster y simula tres efectos:

1. Cuadrupolos:
   Enfocan el haz en un eje y lo desenfocan en otro.

2. Sextupolos:
   Corrigen de forma simplificada las diferencias de energía entre partículas.

3. Undulator:
   Hace oscilar el haz y genera una señal proporcional de fotones.
"""

import numpy as np

from common.bunch import Bunch
from common.constants import (
    X, Y, Z, VX, VY, VZ, ENERGIA,
    MASA_ELECTRON,
    VELOCIDAD_LUZ,
)


class Ring:
    def __init__(
        self,
        longitud=3.0,
        pasos=600,
        dt=2e-11,
        k_cuadrupolo=2.5e7,
        k_sextupolo=1.0e10,
        amplitud_undulator=0.015,
        longitud_onda_undulator=0.35,
    ):
        self.longitud = longitud
        self.pasos = pasos
        self.dt = dt
        self.k_cuadrupolo = k_cuadrupolo
        self.k_sextupolo = k_sextupolo
        self.amplitud_undulator = amplitud_undulator
        self.longitud_onda_undulator = longitud_onda_undulator

    def simular(self, bunch_inicial):
        datos = bunch_inicial.datos.copy()

        # Recentramos el bunch para que entre al anillo como una sección recta.
        datos[:, X] -= np.mean(datos[:, X])
        datos[:, Y] -= np.mean(datos[:, Y])
        datos[:, Z] -= np.mean(datos[:, Z])

        # Hacemos que avance principalmente en z.
        rapidez = np.sqrt(datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2)
        datos[:, VX] *= 0.05
        datos[:, VY] *= 0.05
        datos[:, VZ] = rapidez

        historico = []

        for paso in range(self.pasos):
            z_media = np.mean(datos[:, Z])

            # ------------------------------------------------------------
            # 1. Cuadrupolos
            # ------------------------------------------------------------
            # Modelo simplificado:
            # ax enfoca hacia x = 0
            # ay enfoca hacia y = 0
            #
            # En un acelerador real un cuadrupolo enfoca un eje y desenfoca
            # el otro, pero aquí usamos una versión estable para visualización.
            ax_quad = -self.k_cuadrupolo * datos[:, X]
            ay_quad = -self.k_cuadrupolo * datos[:, Y]

            datos[:, VX] += ax_quad * self.dt
            datos[:, VY] += ay_quad * self.dt

            # ------------------------------------------------------------
            # 2. Sextupolos simplificados
            # ------------------------------------------------------------
            # Partículas con energía distinta reciben una corrección pequeña.
            energia_media = np.mean(datos[:, ENERGIA])
            desviacion_energia = (datos[:, ENERGIA] - energia_media) / energia_media

            correccion_x = -self.k_sextupolo * desviacion_energia * datos[:, X]**2
            correccion_y = self.k_sextupolo * desviacion_energia * datos[:, Y]**2

            datos[:, VX] += correccion_x * self.dt
            datos[:, VY] += correccion_y * self.dt

            # ------------------------------------------------------------
            # 3. Undulator
            # ------------------------------------------------------------
            # Forzamos una oscilación transversal pequeña en x.
            fase = 2 * np.pi * datos[:, Z] / self.longitud_onda_undulator
            x_undulator = self.amplitud_undulator * np.sin(fase)

            datos[:, X] += 0.03 * (x_undulator - datos[:, X])

            # ------------------------------------------------------------
            # 4. Actualización de posiciones
            # ------------------------------------------------------------
            datos[:, X] += datos[:, VX] * self.dt
            datos[:, Y] += datos[:, VY] * self.dt
            datos[:, Z] += datos[:, VZ] * self.dt

            # Evitar velocidades mayores que la luz por errores numéricos.
            v2 = datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2
            v = np.sqrt(v2)
            mascara = v > 0.99 * VELOCIDAD_LUZ

            datos[mascara, VX] *= (0.99 * VELOCIDAD_LUZ) / v[mascara]
            datos[mascara, VY] *= (0.99 * VELOCIDAD_LUZ) / v[mascara]
            datos[mascara, VZ] *= (0.99 * VELOCIDAD_LUZ) / v[mascara]

            # Energía cinética relativista.
            v2 = datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2
            gamma = 1.0 / np.sqrt(1.0 - v2 / VELOCIDAD_LUZ**2)
            datos[:, ENERGIA] = (gamma - 1.0) * MASA_ELECTRON * VELOCIDAD_LUZ**2

            # Señal de fotones aproximada.
            # No cambia el contrato del Bunch, solo la guardamos como atributo.
            intensidad_fotones = np.mean(np.abs(np.sin(fase)))

            frame = Bunch(datos.copy())
            frame.intensidad_fotones = intensidad_fotones
            frame.z_media = z_media

            historico.append(frame)

        return historico