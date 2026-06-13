"""
modulo_inyeccion/fisica_linac.py — Física del Acelerador Lineal (Linac)

Modelo físico:
  DOS MODOS:

  1) 'dc' (RECOMENDADO — default)
     Campo constante E_z = E0.
     Aceleración pareja para todas las partículas.

  2) 'rf'
     Campo RF viajero E_z = E0·sin(ωt - kz + φ).
     Produce aceleración + bunching natural.

Dinámica relativista (siempre activa):
  F = dp/dt,  p = γ·m·v,  E_k = (γ-1)·m·c²
"""

import numpy as np
from common.constants import (
    X, Y, Z, VX, VY, VZ, ENERGIA,
    MASA_ELECTRON, CARGA_ELECTRON, VELOCIDAD_LUZ,
)
from common.bunch import Bunch


class Linac:
    """Acelerador lineal (Linac) con dos modos de operación.

    Modos:
      - 'dc' (default): campo eléctrico constante E_z = E0.
      - 'rf': campo RF viajero E_z = E0·sin(ωt - kz + φ).

    Parameters
    ----------
    modo : {'dc', 'rf'}
    E0 : float, optional
        Por defecto: DC→2e5, RF→5e6.
    frecuencia : float, default 3e9
        Frecuencia RF (Hz). Solo usado en modo 'rf'.
    fase : float, default π/4
        Fase inicial (rad). Solo usado en modo 'rf'.
    longitud : float, default 1.0
        Longitud física del linac (m).
    """

    def __init__(self, modo='dc', E0=None, frecuencia=3e9,
                 fase=np.pi / 4, longitud=1.0):
        self.modo = modo
        self.frecuencia = frecuencia
        self.fase = fase
        self.longitud = longitud

        # Valores por defecto de E0 según modo
        if E0 is None:
            E0 = 2e5 if modo == 'dc' else 5e6
        self.E0 = E0

        self.omega = 2 * np.pi * frecuencia

    # ------------------------------------------------------------------
    # Campo eléctrico según modo
    # ------------------------------------------------------------------
    def _campo_electrico(self, t, datos):
        if self.modo == 'dc':
            return self.E0
        k = self.omega / VELOCIDAD_LUZ
        return self.E0 * np.sin(self.omega * t - k * datos[:, Z] + self.fase)

    # ------------------------------------------------------------------
    # Simulación principal
    # ------------------------------------------------------------------
    def simular(self, bunch, dt=1e-12, pasos=2500):
        datos = bunch.datos.copy()
        historico = [Bunch(datos.copy())]

        m = MASA_ELECTRON
        c = VELOCIDAD_LUZ
        q = CARGA_ELECTRON
        mc2 = m * c * c

        for paso in range(pasos):
            t = paso * dt

            vz = datos[:, VZ]
            vx, vy = datos[:, VX], datos[:, VY]
            v2 = vx*vx + vy*vy + vz*vz

            # γ actual
            gamma = 1.0 / np.sqrt(1.0 - v2 / (c*c))

            # Momento
            mg = gamma * m
            px, py, pz = mg * vx, mg * vy, mg * vz

            # Campo E_z y máscara del linac
            mascara = np.abs(datos[:, Z]) < self.longitud / 2

            if self.modo == 'rf':
                k = self.omega / c
                E_z = self.E0 * np.sin(self.omega * t - k * datos[:, Z] + self.fase)
            else:
                E_z = self.E0

            # Actualizar momento longitudinal
            dp_z = np.where(mascara, q * E_z * dt, 0.0)
            pz += dp_z

            # Nuevo γ desde |p|
            p2 = px*px + py*py + pz*pz
            gamma_new = np.sqrt(1.0 + p2 / (m*m * c*c))

            # Velocidades post-kick
            mg_new = gamma_new * m
            datos[:, VX] = px / mg_new
            datos[:, VY] = py / mg_new
            datos[:, VZ] = pz / mg_new

            # Posiciones
            datos[:, X] += datos[:, VX] * dt
            datos[:, Y] += datos[:, VY] * dt
            datos[:, Z] += datos[:, VZ] * dt

            # Energía cinética relativista
            datos[:, ENERGIA] = (gamma_new - 1.0) * mc2

            historico.append(Bunch(datos.copy()))

        return historico
