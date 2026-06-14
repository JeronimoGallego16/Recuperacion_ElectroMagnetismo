"""
modulo_inyeccion/animacion_linac.py — Animación del Linac en diferido


Estrategia (Opción A — Diferido / pre-calculado):
  La lógica (simular_linac) ya calculó todos los frames y los guardó en
  una lista. Esta función SOLO reproduce esa lista como una película.
  Esto permite que el Front y el Back estén completamente separados.

La animación muestra TRES paneles sincronizados:
  1. Vista longitudinal (x vs z)  —  cómo las partículas se agrupan
  2. Energía vs z                 —  cómo ganan energía en el Linac
  3. Espacio de fase (vz vs z)    —  el bunching en el plano fase:
     las partículas convergen a un punto en (posición, velocidad).
     Esta es la gráfica más importante del Linac.

Colores: plasma (azul = baja energía, amarillo/rojo = alta energía).
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize
from matplotlib.gridspec import GridSpec
from common.constants import CARGA_ELECTRON, VELOCIDAD_LUZ


def animar_linac(historico, dt=1e-12, longitud_linac=1.0, intervalo=30,
                 mostrar=True, guardar=False):
    """Reproduce la animación del bunch en el Linac (3 paneles).

    Parameters
    ----------
    historico : list[Bunch]
        Lista de Bunch generada por Linac.simular(). Cada elemento es
        el estado del sistema en un instante de tiempo.
    dt : float
        Paso de tiempo usado en la simulación (para el eje temporal).
    longitud_linac : float
        Longitud del linac (para dibujar la zona sombreada).
    intervalo : int
        Milisegundos entre frames (menor = más rápido).
    mostrar : bool
        Si True, llama a plt.show() al final.
    guardar : bool
        Si True, guarda la animación como GIF.

    Returns
    -------
    FuncAnimation
        Objeto de animación de Matplotlib (se puede guardar o mostrar).
    """
    # === Layout: 2 filas × 2 columnas (el tercer panel ocupa toda la fila inferior) ===
    fig = plt.figure(figsize=(16, 9))
    fig.subplots_adjust(top=0.90, left=0.06, right=0.91, bottom=0.06)
    gs = GridSpec(2, 2, height_ratios=[1, 1.2], hspace=0.35, wspace=0.3)
    ax1 = fig.add_subplot(gs[0, 0])  # x vs z
    ax2 = fig.add_subplot(gs[0, 1])  # E vs z
    ax3 = fig.add_subplot(gs[1, :])  # vz vs z — espacio de fase (ancho completo)

    # ------------------------------------------------------------------
    # Pre-cálculo de límites globales (todos los frames)
    # ------------------------------------------------------------------
    # Se recorren todos los frames UNA SOLA VEZ para fijar los ejes
    # y la barra de color, evitando que tiemblen durante la animación.
    todos_z = np.concatenate([h.z for h in historico])
    todas_x = np.concatenate([h.x for h in historico])
    todas_vz = np.concatenate([h.vz for h in historico])
    todas_e = np.concatenate([h.energia for h in historico])

    # Límites de z (compartidos entre paneles)
    z_min, z_max = todos_z.min(), todos_z.max()
    margen_z = (z_max - z_min) * 0.1 if z_max > z_min else 0.1

    # Límites de x
    x_min, x_max = todas_x.min(), todas_x.max()
    margen_x = (x_max - x_min) * 0.1 if x_max > x_min else 0.1

    # Límites de vz (en unidades de c)
    vz_min, vz_max = todas_vz.min() / VELOCIDAD_LUZ, todas_vz.max() / VELOCIDAD_LUZ
    margen_vz = (vz_max - vz_min) * 0.1 if vz_max > vz_min else 0.1

    # Conversión: Joules → keV (más legible para el humano)
    def j_a_kev(e):
        return e / (CARGA_ELECTRON * 1e3)

    e_min_kev = j_a_kev(todas_e.min())
    e_max_kev = j_a_kev(todas_e.max())
    margen_e = (e_max_kev - e_min_kev) * 0.15 if e_max_kev > e_min_kev else 1.0

    # Normalización única del color (energía en keV)
    norm = Normalize(vmin=e_min_kev, vmax=e_max_kev)

    # ------------------------------------------------------------------
    # Panel 1: Vista longitudinal (x vs z)
    # ------------------------------------------------------------------
    ax1.axvspan(-longitud_linac / 2, longitud_linac / 2, alpha=0.12,
                color='blue', label='Linac')
    ax1.axvline(-longitud_linac / 2, color='blue', ls='--', lw=0.8)
    ax1.axvline(longitud_linac / 2, color='blue', ls='--', lw=0.8)

    scatter1 = ax1.scatter([], [], c=[], cmap='plasma', s=10, alpha=0.8)
    ax1.set_xlim(z_min - margen_z, z_max + margen_z)
    ax1.set_ylim(x_min - margen_x, x_max + margen_x)
    ax1.set_xlabel('z (m)')
    ax1.set_ylabel('x (m)')
    ax1.set_title('Vista longitudinal del bunch')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    ax1.legend(loc='upper right', fontsize=8)

    # ------------------------------------------------------------------
    # Panel 2: Energía vs posición z
    # ------------------------------------------------------------------
    scatter2 = ax2.scatter([], [], c=[], cmap='plasma', s=10, alpha=0.8)
    ax2.set_xlim(z_min - margen_z, z_max + margen_z)
    ax2.set_ylim(e_min_kev - margen_e, e_max_kev + margen_e)
    ax2.set_xlabel('z (m)')
    ax2.set_ylabel('Energía cinética (keV)')
    ax2.set_title('Energía de las partículas')
    ax2.grid(True, alpha=0.3)

    # Barra de color (compartida por todos los paneles)
    fig.colorbar(scatter2, ax=[ax1, ax2, ax3], label='Energía (keV)',
                 shrink=0.6, location='right')

    # ------------------------------------------------------------------
    # Panel 3: Espacio de fase longitudinal (vz/c vs z)
    # ------------------------------------------------------------------
    # El panel más importante del Linac. Muestra el espacio de fase
    # (posición vs velocidad). El bunching se ve como la convergencia
    # de puntos hacia una región compacta en (z, vz/c).
    ax3.axvspan(-longitud_linac / 2, longitud_linac / 2, alpha=0.12,
                color='blue', label='Linac')
    ax3.axvline(-longitud_linac / 2, color='blue', ls='--', lw=0.8)
    ax3.axvline(longitud_linac / 2, color='blue', ls='--', lw=0.8)

    scatter3 = ax3.scatter([], [], c=[], cmap='plasma', s=10, alpha=0.8)
    ax3.set_xlim(z_min - margen_z, z_max + margen_z)
    ax3.set_ylim(vz_min - margen_vz, vz_max + margen_vz)
    ax3.set_xlabel('z (m)')
    ax3.set_ylabel('v_z / c')
    ax3.set_title('Espacio de fase longitudinal (v_z/c vs z) — Bunching')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper right', fontsize=8)

    # Título general con el tiempo simulado
    titulo_tiempo = fig.suptitle('Simulación del Linac', fontsize=15, y=0.96, fontweight='bold')

    # ------------------------------------------------------------------
    # Función de actualización — llamado por FuncAnimation en cada frame
    # ------------------------------------------------------------------
    def actualizar(frame):
        """Actualiza los datos de los scatter plots para el frame dado."""
        bunch = historico[frame]
        z = bunch.z
        x = bunch.x
        vz_c = bunch.vz / VELOCIDAD_LUZ
        e_kev = j_a_kev(bunch.energia)

        # Panel 1 (x vs z)
        scatter1.set_offsets(np.column_stack([z, x]))
        scatter1.set_array(e_kev)
        scatter1.set_norm(norm)

        # Panel 2 (E vs z)
        scatter2.set_offsets(np.column_stack([z, e_kev]))
        scatter2.set_array(e_kev)
        scatter2.set_norm(norm)

        # Panel 3 (vz/c vs z) — espacio de fase
        scatter3.set_offsets(np.column_stack([z, vz_c]))
        scatter3.set_array(e_kev)
        scatter3.set_norm(norm)

        # Mostrar tiempo simulado en nanosegundos
        t_ns = frame * dt * 1e9
        titulo_tiempo.set_text(
            f'Simulación del Linac  —  '
            f'Paso {frame}/{len(historico) - 1}  —  '
            f't = {t_ns:.3f} ns  —  '
            f'{bunch.n_particulas} electrones'
        )

    # ------------------------------------------------------------------
    # Crear la animación
    # ------------------------------------------------------------------
    ani = animation.FuncAnimation(
        fig, actualizar, frames=len(historico),
        interval=intervalo, blit=False
    )

    # Guardar como GIF (requiere pillow instalado)
    if guardar:
        ani.save('linac_simulation.gif', writer='pillow', fps=30)

    # Mostrar en pantalla (sin tight_layout para respetar subplots_adjust)
    if mostrar:
        plt.show()

    return ani
