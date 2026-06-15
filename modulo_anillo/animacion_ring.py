"""
modulo_anillo/animacion_ring.py

Animación del Storage Ring.

Muestra:
1. Movimiento del bunch en el undulator.
2. Espacio de fase horizontal.
3. Espacio de fase vertical.
4. Intensidad relativa de fotones.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from common.constants import X, Y, Z, VX, VY


def animar_ring(historico, intervalo=30):
    fig, ejes = plt.subplots(2, 2, figsize=(11, 8))

    ax_haz = ejes[0, 0]
    ax_fase_x = ejes[0, 1]
    ax_fase_y = ejes[1, 0]
    ax_fotones = ejes[1, 1]

    scat_haz = ax_haz.scatter([], [], s=10)
    scat_fase_x = ax_fase_x.scatter([], [], s=10)
    scat_fase_y = ax_fase_y.scatter([], [], s=10)

    linea_fotones, = ax_fotones.plot([], [])

    fotones_hist = []

    ax_haz.set_title("Undulator: trayectoria del bunch")
    ax_haz.set_xlabel("z")
    ax_haz.set_ylabel("x")

    ax_fase_x.set_title("Espacio de fase horizontal")
    ax_fase_x.set_xlabel("x")
    ax_fase_x.set_ylabel("vx")

    ax_fase_y.set_title("Espacio de fase vertical")
    ax_fase_y.set_xlabel("y")
    ax_fase_y.set_ylabel("vy")

    ax_fotones.set_title("Intensidad relativa de fotones")
    ax_fotones.set_xlabel("frame")
    ax_fotones.set_ylabel("intensidad")

    def configurar_limites():
        todos_x = np.concatenate([b.x for b in historico])
        todos_y = np.concatenate([b.y for b in historico])
        todos_z = np.concatenate([b.z for b in historico])
        todos_vx = np.concatenate([b.vx for b in historico])
        todos_vy = np.concatenate([b.vy for b in historico])

        ax_haz.set_xlim(np.min(todos_z), np.max(todos_z))
        ax_haz.set_ylim(np.min(todos_x), np.max(todos_x))

        ax_fase_x.set_xlim(np.min(todos_x), np.max(todos_x))
        ax_fase_x.set_ylim(np.min(todos_vx), np.max(todos_vx))

        ax_fase_y.set_xlim(np.min(todos_y), np.max(todos_y))
        ax_fase_y.set_ylim(np.min(todos_vy), np.max(todos_vy))

        ax_fotones.set_xlim(0, len(historico))
        ax_fotones.set_ylim(0, 1.2)

    configurar_limites()

    def actualizar(frame):
        bunch = historico[frame]

        datos_haz = np.column_stack((bunch.z, bunch.x))
        datos_fase_x = np.column_stack((bunch.x, bunch.vx))
        datos_fase_y = np.column_stack((bunch.y, bunch.vy))

        scat_haz.set_offsets(datos_haz)
        scat_fase_x.set_offsets(datos_fase_x)
        scat_fase_y.set_offsets(datos_fase_y)

        intensidad = getattr(bunch, "intensidad_fotones", 0)
        fotones_hist.append(intensidad)

        linea_fotones.set_data(
            np.arange(len(fotones_hist)),
            fotones_hist
        )

        fig.suptitle(f"Storage Ring - Frame {frame}")

        return scat_haz, scat_fase_x, scat_fase_y, linea_fotones

    animacion = FuncAnimation(
        fig,
        actualizar,
        frames=len(historico),
        interval=intervalo,
        blit=False
    )

    plt.tight_layout()
    plt.show()

    return animacion