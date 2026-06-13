"""
modulo_inyeccion/fisica_linac.py — Física del Acelerador Lineal (Linac)


 Modelo físico:
   El Linac acelera electrones mediante un campo eléctrico RF viajero
   a lo largo del eje longitudinal z. El campo tiene la forma:

     E_z(z, t) = E0 · sin(ω·t - k·z + φ)

   donde:
     ω = 2π·frecuencia  (frecuencia angular RF)
     k = ω / c          (número de onda, la onda viaja a velocidad de la luz)
     φ = fase inicial

   Este campo produce dos efectos simultáneos:
     1. ACELERACIÓN: las partículas ganan energía cinética en z
     2. BUNCHING: el gradiente del campo agrupa las partículas en
        paquetes (las que van adelante reciben menos fuerza, las de
        atrás reciben más, convergiendo en una fase estable)

 Dinámica relativista (predeterminada):
   Cuando relativista=True, se usa F = dp/dt con p = γ·m·v:
     1. Se calcula γ desde la velocidad actual
     2. Se obtiene el momento p = γ·m·v
     3. Se actualiza p_z con el impulso q·E·dt
     4. Se recalcula γ desde |p|²: γ = √(1 + p²/(m²c²))
     5. Se obtiene la nueva velocidad v = p / (γ·m)
     6. Energía cinética relativista: E_k = (γ - 1)·m·c²

   Esto es correcto para cualquier velocidad (0 ≤ v < c).

 Dinámica Newtoniana (relativista=False):
   Usa F = m·a (original). Válido solo cuando v ≪ c.
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
        Aceleración pareja de todas las partículas.
      - 'rf': campo RF viajero E_z = E0·sin(ωt - kz + φ).
        Produce aceleración + bunching natural.

    Parameters de __init__
    ----------------------
    modo : {'dc', 'rf'}
        Modo de operación del Linac.
    E0 : float
        Amplitud del campo eléctrico (V/m).
        - DC: E0 = 2e5 V/m → ~37 keV (default).
        - RF: E0 = 5e6 V/m → ~75 keV.
    frecuencia : float
        Frecuencia RF (Hz). Solo usado en modo 'rf'. Típico: 3e9 Hz (banda S).
    fase : float
        Fase inicial del campo (rad). Solo usado en modo 'rf'.
        π/4 da aceleración + bunching.
    longitud : float
        Longitud física del linac (m). Fuera de este rango no hay campo.
    relativista : bool
        Si True, usa dinámica relativista (F = dp/dt, p = γ·m·v).
        Si False, usa Newton (F = m·a). Recomendado: True.
    """

    def __init__(self, modo='dc', E0=None, frecuencia=3e9,
                 fase=np.pi / 4, longitud=1.0, relativista=True):
        self.modo = modo
        self.frecuencia = frecuencia
        self.fase = fase
        self.longitud = longitud
        self.relativista = relativista

        # Valores por defecto de E0 según modo
        if E0 is None:
            if modo == 'dc':
                E0 = 2e5
            else:
                E0 = 5e6
        self.E0 = E0

        # Precálculo de parámetros de la onda (modo RF)
        self.omega = 2 * np.pi * frecuencia
        self.k = self.omega / VELOCIDAD_LUZ   # número de onda

    # ------------------------------------------------------------------
    # Campo eléctrico según modo de operación
    # ------------------------------------------------------------------
    def _campo_electrico(self, t, datos):
        """Devuelve E_z para cada partícula según el modo."""
        if self.modo == 'dc':
            return self.E0
        else:
            return self.E0 * np.sin(
                self.omega * t - self.k * datos[:, Z] + self.fase
            )

    def simular(self, bunch, dt=1e-12, pasos=2500):
        """Ejecuta la simulación del paso del bunch por el Linac.

        Aplica el campo RF viajero E_z(z,t) partícula por partícula.

        Parameters
        ----------
        bunch : Bunch
            Bunch de electrones a acelerar.
        dt : float
            Paso de tiempo (s). 1e-12 s = 1 ps.
        pasos : int
            Número de iteraciones de simulación.

        Returns
        -------
        list[Bunch]
            Lista con el estado del bunch en CADA paso de tiempo.
            historico[0]   = estado inicial
            historico[-1]  = estado final (para pasar al próximo módulo)
            len(historico) = pasos + 1 (incluye el inicial)
        """
        # Trabajamos sobre una copia para no mutar el original
        datos = bunch.datos.copy()

        # El frame 0 es el estado inicial
        historico = [Bunch(datos.copy())]

        if self.relativista:
            self._simular_relativista(datos, dt, pasos, historico)
        else:
            self._simular_newtoniano(datos, dt, pasos, historico)

        return historico

    # ------------------------------------------------------------------
    # Versión Newtoniana:  F = m·a   (original, v ≪ c)
    # ------------------------------------------------------------------
    def _simular_newtoniano(self, datos, dt, pasos, historico):
        for paso in range(pasos):
            t = paso * dt

            # Campo eléctrico según modo
            E_z = self._campo_electrico(t, datos)

            # Máscara: fuera del linac no hay campo
            mascara = np.abs(datos[:, Z]) < self.longitud / 2
            a_z = np.where(mascara, CARGA_ELECTRON * E_z / MASA_ELECTRON, 0.0)

            # Integración semi-implícita: velocidad → posición
            datos[:, VZ] += a_z * dt
            datos[:, X] += datos[:, VX] * dt
            datos[:, Y] += datos[:, VY] * dt
            datos[:, Z] += datos[:, VZ] * dt

            # Energía cinética Newtoniana: E = ½ m v²
            v2 = datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2
            datos[:, ENERGIA] = 0.5 * MASA_ELECTRON * v2

            historico.append(Bunch(datos.copy()))

    # ------------------------------------------------------------------
    # Versión Relativista:  F = dp/dt,  p = γ·m·v
    # ------------------------------------------------------------------
    def _simular_relativista(self, datos, dt, pasos, historico):
        for paso in range(pasos):
            t = paso * dt

            # Campo eléctrico según modo
            E_z = self._campo_electrico(t, datos)

            # 1. Velocidad al cuadrado y factor γ actual
            v2 = datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2
            gamma = 1.0 / np.sqrt(1.0 - v2 / VELOCIDAD_LUZ**2)

            # 2. Momento lineal relativista:  p = γ·m·v
            masa_gamma = gamma * MASA_ELECTRON
            px = masa_gamma * datos[:, VX]
            py = masa_gamma * datos[:, VY]
            pz = masa_gamma * datos[:, VZ]

            # 3. Actualizar p_z con el impulso  Δp = q·E·Δt
            mascara = np.abs(datos[:, Z]) < self.longitud / 2
            dp_z = np.where(mascara, CARGA_ELECTRON * E_z * dt, 0.0)
            pz += dp_z

            # 4. Recalcular γ desde |p|:
            #    γ = √(1 + p²/(m²c²))   →  proviene de  E² = p²c² + m²c⁴
            p2 = px**2 + py**2 + pz**2
            gamma_new = np.sqrt(1.0 + p2 / (MASA_ELECTRON * VELOCIDAD_LUZ)**2)

            # 5. Nueva velocidad:  v = p / (γ·m)
            masa_gamma_new = gamma_new * MASA_ELECTRON
            datos[:, VX] = px / masa_gamma_new
            datos[:, VY] = py / masa_gamma_new
            datos[:, VZ] = pz / masa_gamma_new

            # 6. Actualizar posiciones
            datos[:, X] += datos[:, VX] * dt
            datos[:, Y] += datos[:, VY] * dt
            datos[:, Z] += datos[:, VZ] * dt

            # 7. Energía cinética relativista:  E_k = (γ - 1)·m·c²
            datos[:, ENERGIA] = (gamma_new - 1.0) * MASA_ELECTRON * VELOCIDAD_LUZ**2

            historico.append(Bunch(datos.copy()))
