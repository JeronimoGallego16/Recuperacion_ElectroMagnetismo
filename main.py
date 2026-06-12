import matplotlib.pyplot as plt
from modulo_inyeccion import Bunch, Linac, animar_linac


def main():
    print("Generando bunch inicial...")
    bunch = Bunch.generar_inicial(n_particulas=200, seed=42)

    print("Creando Linac y simulando...")
    linac = Linac()
    historico = linac.simular(bunch)

    print(f"Animación lista ({len(historico)} frames). Mostrando...")
    animar_linac(historico)

    plt.close('all')


if __name__ == "__main__":
    main()
