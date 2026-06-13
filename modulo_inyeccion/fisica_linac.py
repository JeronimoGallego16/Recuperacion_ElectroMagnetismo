"""
modulo_inyeccion/fisica_linac.py — Física del Acelerador Lineal (Linac)

 Modelo físico:
   Campo RF viajero:  E_z(z,t) = E0 · sin(ω·t - k·z + φ)

   DOS MODOS:

   1) 'dc' (RECOMENDADO — default)
      Cada partícula tiene su propio k = ω / v_z adaptado paso a paso.
      Esto mantiene cada electrón en su fase de resonancia individual:
      las que arrancan en fase aceleradora se aceleran, las que arrancan
      en fase desaceleradora se frenan, produciendo BUNCHING real.

   2) 'dc'
      Campo constante. Aceleración pareja para todas. No hay bunching.

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
    """Acelerador lineal (Linac).

    Parameters
    ----------
    E0 : float
        Amplitud del campo eléctrico (V/m).
    modo : str
        'rf' (default, con bunching) | 'dc' (campo constante)
    frecuencia : float
        Frecuencia RF (Hz). Solo usado en modo 'rf'.
    fase : float
        Fase inicial del campo (rad). π/4 da aceleración + bunching.
    longitud : float
        Longitud física del linac (m).
    """

    MODOS_VALIDOS = {'rf', 'dc'}

    def __init__(self, E0=2e5, modo='dc', frecuencia=3e9,
                 fase=np.pi / 4, longitud=1.0):
        if modo not in self.MODOS_VALIDOS:
            raise ValueError(f"Modo debe ser uno de {self.MODOS_VALIDOS}")
        self.E0 = E0
        self.modo = modo
        self.frecuencia = frecuencia
        self.fase = fase
        self.longitud = longitud
        self.omega = 2 * np.pi * frecuencia

    def simular(self, bunch, dt=1e-12, pasos=3000):
        """Ejecuta la simulación del paso del bunch por el Linac.

        Returns
        -------
        list[Bunch]
            historico[0]  = estado inicial
            historico[-1] = estado final (pasa al próximo módulo)
        """
        datos = bunch.datos.copy()
        historico = [Bunch(datos.copy())]

        if self.modo == 'rf':
            self._simular_rf(datos, dt, pasos, historico)
        else:
            self._simular_dc(datos, dt, pasos, historico)

        return historico

    # ------------------------------------------------------------------
    # Modo RF — bunching por fase individual
    # ------------------------------------------------------------------
    # Cada partícula tiene k_i = ω / v_z_i, lo que la mantiene en fase
    # consigo misma. La fase que ve depende de su condición inicial:
    #
    #   θ_i = ω·(t - z_i/v_z_i) + φ ≈ -ω·z0_i/v_z_i + φ  (constante)
    #
    # Esto produce:
    #   - Partículas en fase aceleradora  (θ ~ π/4):  ganan energía
    #   - Partículas en fase desaceleradora (θ ~ 5π/4): pierden energía
    #   - Convergencia en espacio de fase:  BUNCHING
    # ------------------------------------------------------------------
    def _simular_rf(self, datos, dt, pasos, historico):
        c = VELOCIDAD_LUZ
        m = MASA_ELECTRON
        q = CARGA_ELECTRON
        mc2 = m * c * c
        omega = self.omega

        for paso in range(pasos):
            t = paso * dt

            # Velocidad actual de cada partícula (evitar división por cero)
            vz = np.abs(datos[:, VZ])
            vz = np.maximum(vz, 1e3)

            # k individual para cada partícula:  k_i = ω / v_z_i
            k_i = omega / vz

            # Campo RF individual:  E_z_i = E0 · sin(ω·t - k_i·z_i + φ)
            E_z = self.E0 * np.sin(omega * t - k_i * datos[:, Z] + self.fase)

            # Solo acelera dentro del linac
            mascara = np.abs(datos[:, Z]) < self.longitud / 2

            # === Paso relativista: F = dp/dt ===
            vx, vy = datos[:, VX], datos[:, VY]
            v2 = vx*vx + vy*vy + vz*vz
            gamma = 1.0 / np.sqrt(1.0 - v2 / (c*c))

            mg = gamma * m
            px, py, pz = mg * vx, mg * vy, mg * vz

            dp_z = np.where(mascara, q * E_z * dt, 0.0)
            pz += dp_z

            p2 = px*px + py*py + pz*pz
            gamma_new = np.sqrt(1.0 + p2 / (m*m * c*c))

            mg_new = gamma_new * m
            datos[:, VX] = px / mg_new
            datos[:, VY] = py / mg_new
            datos[:, VZ] = pz / mg_new

            datos[:, X] += datos[:, VX] * dt
            datos[:, Y] += datos[:, VY] * dt
            datos[:, Z] += datos[:, VZ] * dt

            datos[:, ENERGIA] = (gamma_new - 1.0) * mc2

            historico.append(Bunch(datos.copy()))

    # ------------------------------------------------------------------
    # Modo DC — campo constante, sin bunching
    # ------------------------------------------------------------------
    def _simular_dc(self, datos, dt, pasos, historico):
        c = VELOCIDAD_LUZ
        m = MASA_ELECTRON
        q = CARGA_ELECTRON
        mc2 = m * c * c

        for paso in range(pasos):
            vx, vy, vz = datos[:, VX], datos[:, VY], datos[:, VZ]
            v2 = vx*vx + vy*vy + vz*vz
            gamma = 1.0 / np.sqrt(1.0 - v2 / (c*c))

            mg = gamma * m
            px, py, pz = mg * vx, mg * vy, mg * vz

            mascara = np.abs(datos[:, Z]) < self.longitud / 2
            dp_z = np.where(mascara, q * self.E0 * dt, 0.0)
            pz += dp_z

            p2 = px*px + py*py + pz*pz
            gamma_new = np.sqrt(1.0 + p2 / (m*m * c*c))

            mg_new = gamma_new * m
            datos[:, VX] = px / mg_new
            datos[:, VY] = py / mg_new
            datos[:, VZ] = pz / mg_new

            datos[:, X] += datos[:, VX] * dt
            datos[:, Y] += datos[:, VY] * dt
            datos[:, Z] += datos[:, VZ] * dt

            datos[:, ENERGIA] = (gamma_new - 1.0) * mc2

            historico.append(Bunch(datos.copy()))
