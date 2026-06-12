# =============================================================================
# main.py — Pipeline principal de la simulación del sincrotrón
# =============================================================================
#
# Este archivo orquesta las 3 etapas del proyecto. A medida que cada
# integrante termine su módulo, se van descomentando las líneas.
#
# Pipeline final:
#   1. Bunch.generar_inicial()           → Integrante 1: crear partículas
#   2. Linac.simular()                   → Integrante 1: aceleración lineal
#   3. Booster.simular()                 → Integrante 2: curvatura + dipolos
#   4. Ring.simular()                    → Integrante 3: cuadrupolos + undulator
#
# La animación es Opción A (diferido): la lógica corre primero y guarda
# todo el histórico, luego la animación solo lo reproduce.
# =============================================================================

import matplotlib.pyplot as plt
from modulo_inyeccion import Bunch, Linac, animar_linac


def main():
    """Punto de entrada de la simulación."""

    # ==================================================================
    # ETAPA 1 — Inyección y Aceleración Lineal (Integrante 1)
    # ==================================================================
    print("=== ETAPA 1: Linac ===")
    print("Generando bunch inicial...")
    bunch = Bunch.generar_inicial(n_particulas=200, seed=42)

    print("Creando Linac y simulando...")
    linac = Linac()
    historico_linac = linac.simular(bunch)

    print(f"Animación lista ({len(historico_linac)} frames). Mostrando...")
    animar_linac(historico_linac)

    # Al cerrar la ventana de animación, el estado final del Linac
    # estará listo para pasar al próximo módulo:
    #   bunch_para_booster = historico_linac[-1]

    # ==================================================================
    # ETAPA 2 — Booster (Integrante 2) — Descomentar cuando esté listo
    # ==================================================================
    # from modulo_transferencia import Booster, animar_booster
    #
    # print("=== ETAPA 2: Booster ===")
    # booster = Booster()
    # historico_booster = booster.simular(historico_linac[-1])
    # animar_booster(historico_booster)
    # bunch_para_ring = historico_booster[-1]

    # ==================================================================
    # ETAPA 3 — Anillo (Integrante 3) — Descomentar cuando esté listo
    # ==================================================================
    # from modulo_anillo import Ring, animar_ring
    #
    # print("=== ETAPA 3: Ring ===")
    # ring = Ring()
    # historico_ring = ring.simular(historico_booster[-1])
    # animar_ring(historico_ring)

    print("=== Simulación completada ===")
    plt.close('all')


if __name__ == "__main__":
    main()
