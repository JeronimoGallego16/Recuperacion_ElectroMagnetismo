from modulo_anillo import generar_bunch_post_booster, Ring, animar_ring

print("Creando bunch ficticio post-Booster...")
bunch = generar_bunch_post_booster(n_particulas=200, seed=42)

print("Simulando Ring...")
ring = Ring()
historico_ring = ring.simular(bunch)

print("Frames generados:", len(historico_ring))
print("Partículas:", historico_ring[-1].n_particulas)
print("Intensidad final de fotones:", historico_ring[-1].intensidad_fotones)
print("z media final:", historico_ring[-1].z_media)

print("Mostrando animación del Ring...")
animar_ring(historico_ring)