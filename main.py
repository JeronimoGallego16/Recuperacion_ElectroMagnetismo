"""
main.py — Pipeline principal de la simulación del sincrotrón

Pipeline:
  1. Linac  (Integrante 1)  → aceleración lineal (~37 keV)
  2. Booster (Integrante 2)  → inyección, curvatura + RF
  3. Ring   (Integrante 3)  → (pendiente)

Cada etapa:
  - Calcula toda la física primero (Opción A, diferido)
  - Guarda el histórico completo
  - Pasa el último frame a la siguiente etapa
"""

import matplotlib.pyplot as plt
from modulo_inyeccion import Bunch, Linac, animar_linac
from modulo_transferencia import Booster, animar_booster


def main():
    # ==================================================================
    # ETAPA 1 — Inyección y Aceleración Lineal (Integrante 1)
    # ==================================================================
    print("=== ETAPA 1: Linac ===")
    print("Generando bunch inicial...")
    bunch = Bunch.generar_inicial(n_particulas=200, seed=42)

    print("Simulando Linac (modo DC)...")
    linac = Linac()
    historico_linac = linac.simular(bunch)

    print(f"Animación del Linac ({len(historico_linac)} frames). Mostrando...")
    animar_linac(historico_linac)

    # Pasar el estado final a la siguiente etapa
    bunch_salida = historico_linac[-1]

    # ==================================================================
    # ETAPA 2 — Booster (Integrante 2)
    # ==================================================================
    print("\n=== ETAPA 2: Booster ===")
    print("Inyectando en el Booster...")
    booster = Booster()
    historico_booster = booster.simular(bunch_salida)

    print(f"Animación del Booster ({len(historico_booster)} frames). Mostrando...")
    animar_booster(historico_booster)

    # bunch_salida = historico_booster[-1]  # para el Integrante 3

    # ==================================================================
    # ETAPA 3 — Ring (Integrante 3 — pendiente)
    # ==================================================================
    # from modulo_anillo import Ring, animar_ring
    # print("\n=== ETAPA 3: Ring ===")
    # ring = Ring()
    # historico_ring = ring.simular(historico_booster[-1])
    # animar_ring(historico_ring)

    print("\n=== Simulación completada ===")
    plt.close('all')


if __name__ == "__main__":
    main()
