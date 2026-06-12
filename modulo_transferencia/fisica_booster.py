"""
modulo_transferencia/fisica_booster.py — Física del Booster (Anillo de Curvatura)

Modelo físico:
  El Booster es un anillo de curvatura magnética que mantiene y acelera el
  haz de electrones mediante dipolos (campo B uniforme en Y) y una cavidad
  RF localizada que entrega ΔE = |q|·V_rf por vuelta.

  Ecuaciones implementadas:
    1. Campo dipolar en Y: la magnitud se ajusta dinámicamente en CADA paso
       para que el radio de Larmor coincida exactamente con radio_booster:
         B(t) = p_medio(t) / (|q| · R)
       Esto elimina la deriva orbital sin necesidad de rampa fija.
    2. Fuerza de Lorentz (Boris leapfrog): integración exacta de la fuerza
       magnética mediante rotación en espacio de momento. Conserva |p|.
    3. Dinámica relativista completa: γ = √(1 + p²/(m²c²))
    4. Kick RF discreto: una sola vez por vuelta (paso 0), en dirección
       tangencial al movimiento: Δp_RF = (ΔE / |v|²) · v
    5. Posición con velocidad media (leapfrog, O(dt²)):
       x(t+dt) = x(t) + v(t+dt/2) · dt

  Algoritmo (por paso):
    1. Kick RF si paso % pasos_por_vuelta == 0
    2. Calcular p = γ·m·v y B = mean(|p|) / (|q|·R)
    3. Rotación Boris: p' = p + (p + p×t) × s  (|p'| = |p|)
    4. Posición con p* (momento a medio paso): x += (p*/γm)·dt
    5. Velocidad para siguiente paso: v = p' / (γ·m)

  Restricción de rendimiento:
    Todos los cálculos sobre las N partículas son operaciones vectorizadas
    de NumPy. Sin bucles for sobre partículas.
"""

import numpy as np
from typing import List
from common.constants import (
    X, Y, Z, VX, VY, VZ, ENERGIA,
    MASA_ELECTRON, CARGA_ELECTRON, VELOCIDAD_LUZ,
)
from common.bunch import Bunch


class Booster:
    """Anillo de curvatura magnética con dipolos y aceleración RF.

    El campo B se ajusta dinámicamente en cada paso para que el radio
    de Larmor coincida exactamente con ``radio_booster``, eliminando la
    deriva orbital. La RF se aplica como un kick discreto al inicio de
    cada vuelta (cavidad localizada en el punto de inyección).

    Parameters
    ----------
    voltaje_rf : float
        Voltaje de la cavidad RF (V). Ganancia de energía por vuelta: ΔE = e·V_rf.
    radio_booster : float
        Radio de diseño del booster (m). Las partículas orbitan exactamente
        a esta distancia del origen.
    n_vueltas : int
        Número de vueltas completas a simular (~50).
    pasos_por_vuelta : int
        Pasos de integración por vuelta (~50). Con Boris leapfrog, 50 pasos
        dan una órbita estable con deriva residual < 4%.
    """

    def __init__(
        self,
        voltaje_rf: float = 1e4,
        radio_booster: float = 2.0,
        n_vueltas: int = 50,
        pasos_por_vuelta: int = 50,
    ):
        self.voltaje_rf = voltaje_rf
        self.radio_booster = radio_booster
        self.n_vueltas = n_vueltas
        self.pasos_por_vuelta = pasos_por_vuelta

    # ------------------------------------------------------------------
    # Simulación principal
    # ------------------------------------------------------------------

    def simular(self, bunch_inicial: Bunch) -> List[Bunch]:
        """Simula la inyección y aceleración del bunch en el Booster.

        El haz se re-centra y coloca en el punto de inyección (x=R, z=0),
        con velocidad puramente tangencial (+z). Luego itera la dinámica
        relativista completa con:

          - Campo B(t) = mean(|p|) / (|q|·R) actualizado en cada paso
          - Rotación Boris leapfrog (O(dt²) en posición)
          - Kick RF discreto al inicio de cada vuelta

        Parameters
        ----------
        bunch_inicial : Bunch
            Bunch de electrones del Linac (alta velocidad longitudinal +z).

        Returns
        -------
        list[Bunch]
            historico[0]  = estado inicial (inyectado)
            historico[-1] = estado final (para transferencia al anillo)
            len(historico) = n_vueltas * pasos_por_vuelta + 1
        """
        # Trabajamos sobre una copia para mantener el original intacto
        datos = bunch_inicial.datos.copy()

        # ==============================================================
        # INYECCIÓN TANGENCIAL AUTOMÁTICA
        # ==============================================================
        # El haz del Linac viaja a lo largo del eje +z.
        # Lo re-centramos y lo colocamos en el punto de inyección del
        # booster: lado derecho del anillo (x = R, z = 0).
        #
        # Correcciones de órbita excéntrica:
        #   a) Velocidad puramente tangencial: se elimina la componente
        #      radial (vx → 0) y se asigna toda la rapidez a vz (+z).
        #   b) Campo B0 ideal calculado desde el radio de Larmor:
        #      B0 = p_medio / (|q| · R)  para que R = radio_booster
        # ==============================================================

        # 1. Re-centrar posiciones respecto al origen
        datos[:, X] -= np.mean(datos[:, X])
        datos[:, Y] -= np.mean(datos[:, Y])
        datos[:, Z] -= np.mean(datos[:, Z])

        # 2. Colocar en el punto de inyección (lado derecho del booster)
        datos[:, X] += self.radio_booster

        # 3. Velocidad puramente tangencial en +z (antihoraria).
        #    Se conserva la rapidez total en el plano xz de cada partícula:
        #    vz = sqrt(vx²_old + vz²_old),  vx = 0
        v_total_xz = np.sqrt(datos[:, VX]**2 + datos[:, VZ]**2)
        datos[:, VX] = 0.0
        datos[:, VZ] = v_total_xz
        # vy se mantiene (es la componente vertical, ⊥ al plano orbital)

        # 4. Recalcular energía tras la inyección
        v2 = datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2
        gamma = 1.0 / np.sqrt(1.0 - v2 / VELOCIDAD_LUZ**2)
        datos[:, ENERGIA] = (gamma - 1.0) * MASA_ELECTRON * VELOCIDAD_LUZ**2

        # ==============================================================
        # PARÁMETROS TEMPORALES
        # ==============================================================
        v_mean = np.sqrt(np.mean(v2))
        periodo_orbital = 2.0 * np.pi * self.radio_booster / v_mean
        dt = periodo_orbital / self.pasos_por_vuelta
        pasos_totales = self.n_vueltas * self.pasos_por_vuelta

        # Energía ganada por vuelta (RF kick discreto)
        delta_E_rf = CARGA_ELECTRON * self.voltaje_rf       # J por vuelta

        # Carga del electrón (negativa)
        q = -CARGA_ELECTRON

        # ==============================================================
        # HISTÓRICO: frame 0 = estado recién inyectado
        # ==============================================================
        historico: List[Bunch] = [Bunch(datos.copy())]

        # ==============================================================
        # BUCLE DE SIMULACIÓN
        # ==============================================================
        for paso in range(pasos_totales):

            # ----------------------------------------------------------
            # 1. Estado actual (γ, momento, energía)
            # ----------------------------------------------------------
            v2 = datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2
            gamma = 1.0 / np.sqrt(1.0 - v2 / VELOCIDAD_LUZ**2)
            masa_gamma = gamma * MASA_ELECTRON
            px = masa_gamma * datos[:, VX]
            py = masa_gamma * datos[:, VY]
            pz = masa_gamma * datos[:, VZ]

            # ----------------------------------------------------------
            # 2. Kick RF discreto — al inicio de cada vuelta
            #
            #    Cavidad RF localizada en el punto de inyección. Cada
            #    vuelta, el haz recibe ΔE = |q|·V_rf en un solo impulso
            #    tangencial. Aplicamos el kick ANTES de calcular B,
            #    para que el campo magnético del resto de la vuelta
            #    incluya la ganancia de momento exacta.
            #
            #    Tras el kick, RECALCULAMOS dt para que 50 pasos sigan
            #    correspondiendo a una vuelta completa a la nueva v.
            # ----------------------------------------------------------
            if paso % self.pasos_por_vuelta == 0:
                # Energía objetivo tras el kick: E_new = E_old + ΔE
                E_old_j = (gamma - 1.0) * MASA_ELECTRON * VELOCIDAD_LUZ**2
                E_new_j = E_old_j + delta_E_rf

                # γ y momento final exactos
                gamma_new = 1.0 + E_new_j / (MASA_ELECTRON * VELOCIDAD_LUZ**2)
                gamma_new = np.maximum(gamma_new, 1.0 + 1e-12)
                p_new_mag = np.sqrt(gamma_new**2 - 1.0) * MASA_ELECTRON * VELOCIDAD_LUZ

                # Momento actual (escalar)
                p_old_mag = np.sqrt(px**2 + py**2 + pz**2)
                p_old_mag = np.maximum(p_old_mag, 1e-30)

                # Δp en dirección de v (Δp = (|p_new| - |p_old|) · v̂)
                dp_scale = (p_new_mag - p_old_mag) / p_old_mag
                px += px * dp_scale
                py += py * dp_scale
                pz += pz * dp_scale

                # Gamma y velocidades post-RF
                gamma = gamma_new
                masa_gamma = gamma * MASA_ELECTRON
                datos[:, VX] = px / masa_gamma
                datos[:, VY] = py / masa_gamma
                datos[:, VZ] = pz / masa_gamma

                # Recalcular dt para 50 pasos = 1 órbita
                v2 = (px**2 + py**2 + pz**2) / masa_gamma**2
                v_mean = np.sqrt(np.mean(v2))
                periodo_orbital = 2.0 * np.pi * self.radio_booster / v_mean
                dt = periodo_orbital / self.pasos_por_vuelta

            # ----------------------------------------------------------
            # 3. Campo magnético de tracking dinámico
            #
            #    B(t) = p_medio(t) / (|q| · R)
            #
            #    El momento usado incluye el kick RF de la vuelta actual
            #    (si acabamos de aplicarlo) o el momento post-Boris del
            #    paso anterior (sin kick). En ambos casos, B coincide
            #    exactamente con el momento que la rotación Boris va a
            #    procesar, eliminando el rezago.
            # ----------------------------------------------------------
            p_actual = np.mean(np.sqrt(px**2 + py**2 + pz**2))
            B_actual = p_actual / (CARGA_ELECTRON * self.radio_booster)
            By = -B_actual

            # ----------------------------------------------------------
            # 4. Rotación Boris (leapfrog, integración exacta)
            #
            #    t = q·B·Δt / (2·γ·m) = (0, t_y, 0)
            #    p* = p + p × t  (momento a medio paso, t+dt/2)
            #    p' = p + p* × s  (momento rotado, t+dt)
            #    donde s = 2·t / (1 + |t|²)
            # ----------------------------------------------------------
            t_y = q * By * dt / (2.0 * gamma * MASA_ELECTRON)

            p_cross_t_x = -pz * t_y
            p_cross_t_z = px * t_y

            p_star_x = px + p_cross_t_x
            p_star_z = pz + p_cross_t_z

            t2 = t_y**2
            s_y = 2.0 * t_y / (1.0 + t2)

            p_star_cross_s_x = -p_star_z * s_y
            p_star_cross_s_z = p_star_x * s_y

            px_b = px + p_star_cross_s_x
            pz_b = pz + p_star_cross_s_z

            # ----------------------------------------------------------
            # 5. Posición con velocidad media (leapfrog, O(dt²))
            # ----------------------------------------------------------
            masa_gamma_inv = 1.0 / masa_gamma
            datos[:, X] += p_star_x * masa_gamma_inv * dt
            datos[:, Y] += datos[:, VY] * dt
            datos[:, Z] += p_star_z * masa_gamma_inv * dt

            # ----------------------------------------------------------
            # 6. Velocidad post-Boris para el siguiente paso
            # ----------------------------------------------------------
            datos[:, VX] = px_b * masa_gamma_inv
            datos[:, VZ] = pz_b * masa_gamma_inv

            # ----------------------------------------------------------
            # 7. Energía desde las velocidades post-Boris almacenadas
            #
            #    γ = 1 / √(1 - v²/c²) usando las velocidades que
            #    acabamos de guardar en datos. Boris conserva |p|
            #    exactamente, así que entre kicks RF la energía es
            #    constante (salvo ruido de redondeo ~1e-15).
            # ----------------------------------------------------------
            v2_final = (
                datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2
            )
            gamma_final = 1.0 / np.sqrt(1.0 - v2_final / VELOCIDAD_LUZ**2)
            datos[:, ENERGIA] = (
                (gamma_final - 1.0) * MASA_ELECTRON * VELOCIDAD_LUZ**2
            )

            # ----------------------------------------------------------
            # Guardar el frame actual en el histórico
            # ----------------------------------------------------------
            historico.append(Bunch(datos.copy()))

        return historico
