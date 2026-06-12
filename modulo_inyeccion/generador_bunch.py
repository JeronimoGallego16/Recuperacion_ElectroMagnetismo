# =============================================================================
# modulo_inyeccion/generador_bunch.py — Generación del bunch inicial
# =============================================================================
# Re-exporta Bunch.generar_inicial como función independiente para
# compatibilidad con el estilo funcional si se prefiere:
#
#   from modulo_inyeccion import generar_bunch_inicial
#   bunch = generar_bunch_inicial(200)
# =============================================================================

from common.bunch import Bunch

# Aliasing: permite usar tanto Bunch.generar_inicial() como
# la función suelta generar_bunch_inicial()
generar_bunch_inicial = Bunch.generar_inicial
