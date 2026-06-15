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

from common.constants import VELOCIDAD_LUZ


def animar_ring(historico, intervalo=30):
    fig, ejes = plt.subplots(2, 2, figsize=(11, 8))

    ax_haz = ejes[0, 0]
    ax_fase_x = ejes[0, 1]
    ax_fase_y = ejes[1, 0]
    ax_fotones = ejes[1, 1]

    scat_haz = ax_haz.scatter([], [], s=6, alpha=0.6)
    linea_centro, = ax_haz.plot([], [], linewidth=2.5)

    scat_fase_x = ax_fase_x.scatter([], [], s=10)
    scat_fase_y = ax_fase_y.scatter([], [], s=10)

    linea_fotones, = ax_fotones.plot([], [])

    centros_z = np.array([np.mean(b.z) for b in historico])
    centros_x = np.array([np.mean(b.x) for b in historico])

    intensidades = np.array([
        getattr(b, "intensidad_fotones", 0.0) for b in historico
    ])
    # Datos precomputados para evitar que la animación acumule datos viejos
    # cuando los frames se reinician.
    centros_z = np.array([np.mean(b.z) for b in historico])
    centros_x = np.array([np.mean(b.x) for b in historico])

    intensidades = np.array([
        getattr(b, "intensidad_fotones", 0.0) for b in historico
    ])

    ax_haz.set_title("Undulator: trayectoria media y bunch actual")
    ax_haz.set_xlabel("z")
    ax_haz.set_ylabel("x")

    ax_fase_x.set_title("Espacio de fase horizontal")
    ax_fase_x.set_xlabel("x")
    ax_fase_x.set_ylabel("vx / c")

    ax_fase_y.set_title("Espacio de fase vertical")
    ax_fase_y.set_xlabel("y")
    ax_fase_y.set_ylabel("vy / c")

    ax_fotones.set_title("Intensidad relativa de fotones")
    ax_fotones.set_xlabel("frame")
    ax_fotones.set_ylabel("intensidad")

    def configurar_limites():
        todos_x = np.concatenate([b.x for b in historico])
        todos_y = np.concatenate([b.y for b in historico])
        todos_vx = np.concatenate([b.vx / VELOCIDAD_LUZ for b in historico])
        todos_vy = np.concatenate([b.vy / VELOCIDAD_LUZ for b in historico])

        x_min, x_max = np.percentile(todos_x, [1, 99])
        y_min, y_max = np.percentile(todos_y, [1, 99])
        vx_min, vx_max = np.percentile(todos_vx, [1, 99])
        vy_min, vy_max = np.percentile(todos_vy, [1, 99])

        margen_x = max((x_max - x_min) * 0.2, 1e-3)
        margen_y = max((y_max - y_min) * 0.2, 1e-3)
        margen_vx = max((vx_max - vx_min) * 0.2, 1e-4)
        margen_vy = max((vy_max - vy_min) * 0.2, 1e-4)

        z_centro_min = np.min(centros_z)
        z_centro_max = np.max(centros_z)

        margen_z_centro = max((z_centro_max - z_centro_min) * 0.05, 1e-3)
        margen_x_centro = max(np.max(np.abs(centros_x)) * 1.5, 0.02)

        ax_haz.set_xlim(
            z_centro_min - margen_z_centro,
            z_centro_max + margen_z_centro
        )
        ax_haz.set_ylim(
            -margen_x_centro,
            margen_x_centro
        )

        ax_fase_x.set_xlim(x_min - margen_x, x_max + margen_x)
        ax_fase_x.set_ylim(vx_min - margen_vx, vx_max + margen_vx)

        ax_fase_y.set_xlim(y_min - margen_y, y_max + margen_y)
        ax_fase_y.set_ylim(vy_min - margen_vy, vy_max + margen_vy)

        ax_fotones.set_xlim(0, len(historico))
        ax_fotones.set_ylim(0, 1.2)

    configurar_limites()

    def actualizar(frame):
        bunch = historico[frame]

        datos_haz = np.column_stack((bunch.z, bunch.x))
        datos_fase_x = np.column_stack((bunch.x, bunch.vx / VELOCIDAD_LUZ))
        datos_fase_y = np.column_stack((bunch.y, bunch.vy / VELOCIDAD_LUZ))

        scat_haz.set_offsets(datos_haz)
        scat_fase_x.set_offsets(datos_fase_x)
        scat_fase_y.set_offsets(datos_fase_y)

        linea_centro.set_data(
            centros_z[:frame + 1],
            centros_x[:frame + 1]
        )

        linea_fotones.set_data(
            np.arange(frame + 1),
            intensidades[:frame + 1]
        )

        fig.suptitle(f"Storage Ring - Frame {frame}")

        return scat_haz, scat_fase_x, scat_fase_y, linea_fotones, linea_centro

    animacion = FuncAnimation(
        fig,
        actualizar,
        frames=len(historico),
        interval=intervalo,
        blit=False,
        repeat=True,
        repeat_delay=500
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.90)
    plt.show()

    return animacion