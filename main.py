"""
main.py — Pipeline principal de la simulacion del sincrotron

Pipeline:
  1. Linac  (Integrante 1)  -> aceleracion lineal (~27 keV)
  2. Booster (Integrante 2)  -> inyeccion, curvatura + RF (~527 keV)
  3. Ring   (Integrante 3)  -> undulator + fotones
"""

import matplotlib.pyplot as plt
from modulo_inyeccion import Bunch, Linac, animar_linac
from modulo_transferencia import Booster, animar_booster
from modulo_anillo import Ring, animar_ring


def main():
    # ==================================================================
    # ETAPA 1 — Inyeccion y Aceleracion Lineal (Integrante 1)
    # ==================================================================
    print("=== ETAPA 1: Linac ===")
    print("Generando bunch inicial...")
    bunch = Bunch.generar_inicial(n_particulas=200, seed=42)

    print("Simulando Linac (modo DC)...")
    linac = Linac()
    historico_linac = linac.simular(bunch)

    print("Animacion del Linac. Mostrando...")
    animar_linac(historico_linac)

    bunch_salida = historico_linac[-1]

    # ==================================================================
    # ETAPA 2 — Booster (Integrante 2)
    # ==================================================================
    print("\n=== ETAPA 2: Booster ===")
    print("Inyectando en el Booster...")
    booster = Booster()
    historico_booster = booster.simular(bunch_salida)

    print("Animacion del Booster. Mostrando...")
    animar_booster(historico_booster)

    bunch_salida = historico_booster[-1]

    # ==================================================================
    # ETAPA 3 — Ring (Integrante 3)
    # ==================================================================
    print("\n=== ETAPA 3: Ring ===")
    print("Simulando el Ring...")
    ring = Ring()
    historico_ring = ring.simular(bunch_salida)

    print("Animacion del Ring. Mostrando...")
    animar_ring(historico_ring)

    print("\n=== Simulacion completada ===")
    plt.close('all')


if __name__ == "__main__":
    main()
