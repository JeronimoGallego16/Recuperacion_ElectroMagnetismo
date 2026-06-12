
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

   La integración es semi-implícita (Euler): primero se actualiza la
   velocidad con la aceleración, luego la posición con la nueva velocidad.

"""
import numpy as np
from common.constants import (
    X, Y, Z, VX, VY, VZ, ENERGIA,
    MASA_ELECTRON, CARGA_ELECTRON, VELOCIDAD_LUZ,
)
from common.bunch import Bunch


class Linac:
    """Acelerador lineal (Linac) con campo RF viajero.

    Encapsula los parámetros físicos del linac y el método de simulación.

    Parameters de __init__
    ----------------------
    E0 : float
        Amplitud del campo eléctrico RF (V/m). Típico: 1e6 a 10e6 V/m.
    frecuencia : float
        Frecuencia RF (Hz). Típico: 3e9 Hz (banda S).
    fase : float
        Fase inicial del campo (rad). π/4 da aceleración + bunching.
    longitud : float
        Longitud física del linac (m). Fuera de este rango no hay campo.
    """

    def __init__(self, E0=1e6, frecuencia=3e9, fase=np.pi / 4, longitud=1.0):
        self.E0 = E0
        self.frecuencia = frecuencia
        self.fase = fase
        self.longitud = longitud

        # Precálculo de parámetros de la onda
        self.omega = 2 * np.pi * frecuencia
        self.k = self.omega / VELOCIDAD_LUZ   # número de onda

    def simular(self, bunch, dt=1e-12, pasos=2500):
        """Ejecuta la simulación del paso del bunch por el Linac.

        Aplica el campo RF viajero E_z(z,t) partícula por partícula
        usando integración semi-implícita (Euler).

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

        for paso in range(pasos):
            t = paso * dt  # tiempo actual

            # Campo RF viajero E_z(z,t) = E0 * sin(ωt - kz + φ)
            # Cada partícula siente un campo distinto según su posición z
            E_z = self.E0 * np.sin(self.omega * t - self.k * datos[:, Z] + self.fase)

            # Máscara: fuera del linac no hay campo acelerador
            mascara = np.abs(datos[:, Z]) < self.longitud / 2
            a_z = np.where(mascara, CARGA_ELECTRON * E_z / MASA_ELECTRON, 0.0)

            # Integración semi-implícita:
            #   1° actualizar velocidad con la aceleración actual
            #   2° actualizar posición con la NUEVA velocidad
            datos[:, VZ] += a_z * dt
            datos[:, X] += datos[:, VX] * dt
            datos[:, Y] += datos[:, VY] * dt
            datos[:, Z] += datos[:, VZ] * dt

            # Recalcular energía cinética: E = 0.5 * m * v²
            v2 = datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2
            datos[:, ENERGIA] = 0.5 * MASA_ELECTRON * v2

            # Guardar el frame actual
            historico.append(Bunch(datos.copy()))

        return historico
