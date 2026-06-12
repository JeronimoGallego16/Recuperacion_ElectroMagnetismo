import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize
from common.constants import CARGA_ELECTRON


def animar_linac(historico, dt=1e-12, longitud_linac=1.0, intervalo=30,
                 mostrar=True, guardar=False):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    todos_z = np.concatenate([h.z for h in historico])
    todas_x = np.concatenate([h.x for h in historico])
    todas_e = np.concatenate([h.energia for h in historico])

    z_min, z_max = todos_z.min(), todos_z.max()
    margen_z = (z_max - z_min) * 0.1
    x_min, x_max = todas_x.min(), todas_x.max()
    margen_x = (x_max - x_min) * 0.1

    def j_a_kev(e):
        return e / (CARGA_ELECTRON * 1e3)

    e_min_kev = j_a_kev(todas_e.min())
    e_max_kev = j_a_kev(todas_e.max())

    ax1.axvspan(-longitud_linac / 2, longitud_linac / 2, alpha=0.12,
                color='blue', label='Linac')
    ax1.axvline(-longitud_linac / 2, color='blue', ls='--', lw=0.8)
    ax1.axvline(longitud_linac / 2, color='blue', ls='--', lw=0.8)

    scatter1 = ax1.scatter([], [], c=[], cmap='plasma', s=10, alpha=0.8)
    ax1.set_xlim(z_min - margen_z, z_max + margen_z)
    ax1.set_ylim(x_min - margen_x, x_max + margen_x)
    ax1.set_xlabel('z (m)')
    ax1.set_ylabel('x (m)')
    ax1.set_title('Bunch en el Linac — Vista longitudinal')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    ax1.legend(loc='upper right', fontsize=8)

    scatter2 = ax2.scatter([], [], c=[], cmap='plasma', s=10, alpha=0.8)
    ax2.set_xlim(z_min - margen_z, z_max + margen_z)
    ax2.set_ylim(e_min_kev, e_max_kev * 1.15)
    ax2.set_xlabel('z (m)')
    ax2.set_ylabel('Energía cinética (keV)')
    ax2.set_title('Energía de las partículas')
    ax2.grid(True, alpha=0.3)

    norm = Normalize(vmin=e_min_kev, vmax=e_max_kev)
    fig.colorbar(scatter2, ax=ax2, label='Energía (keV)', shrink=0.8)

    titulo_tiempo = fig.suptitle('', fontsize=12, y=1.02)

    def actualizar(frame):
        bunch = historico[frame]
        z = bunch.z
        x = bunch.x
        e_kev = j_a_kev(bunch.energia)

        scatter1.set_offsets(np.column_stack([z, x]))
        scatter1.set_array(e_kev)
        scatter1.set_norm(norm)

        scatter2.set_offsets(np.column_stack([z, e_kev]))
        scatter2.set_array(e_kev)
        scatter2.set_norm(norm)

        t_ns = frame * dt * 1e9
        titulo_tiempo.set_text(
            f'Simulación del Linac — Paso {frame}/{len(historico) - 1}'
            f' — t = {t_ns:.3f} ns'
        )

    ani = animation.FuncAnimation(
        fig, actualizar, frames=len(historico),
        interval=intervalo, blit=False
    )

    if guardar:
        ani.save('linac_simulation.gif', writer='pillow', fps=30)

    if mostrar:
        plt.tight_layout()
        plt.show()

    return ani
