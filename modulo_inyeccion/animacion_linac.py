"""
modulo_inyeccion/animacion_linac.py — Animación del Linac en diferido


Estrategia (Opción A — Diferido / pre-calculado):
  La lógica (simular_linac) ya calculó todos los frames y los guardó en
  una lista. Esta función SOLO reproduce esa lista como una película.
  Esto permite que el Front y el Back estén completamente separados.

La animación muestra dos paneles sincronizados:
    Izquierda: Vista longitudinal del bunch (x vs z) — las partículas
               entran dispersas y se van agrupando (bunching) y acelerando.
               La zona del Linac se marca en azul translúcido.
    Derecha:   Energía cinética vs z — se ve cómo las partículas ganan
               energía a lo largo del acelerador.

    Colores:    Cada partícula se colorea según su energía (azul = baja,
               rojo/amarillo = alta) usando el colormap 'plasma'.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize
from common.constants import CARGA_ELECTRON


def animar_linac(historico, dt=1e-12, longitud_linac=1.0, intervalo=30,
                 mostrar=True, guardar=False):
    """Reproduce la animación del bunch en el Linac.

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
    # === Configurar figura: 2 paneles lado a lado ===
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # ------------------------------------------------------------------
    # Pre-cálculo de límites globales (todos los frames)
    # ------------------------------------------------------------------
    # Recorremos todo el histórico UNA SOLA VEZ para fijar los ejes
    # y la barra de color, evitando que tiemblen durante la animación.
    todos_z = np.concatenate([h.z for h in historico])
    todas_x = np.concatenate([h.x for h in historico])
    todas_e = np.concatenate([h.energia for h in historico])

    z_min, z_max = todos_z.min(), todos_z.max()
    margen_z = (z_max - z_min) * 0.1
    x_min, x_max = todas_x.min(), todas_x.max()
    margen_x = (x_max - x_min) * 0.1

    # Conversión: Joules → keV (más legible para el humano)
    def j_a_kev(e):
        return e / (CARGA_ELECTRON * 1e3)

    e_min_kev = j_a_kev(todas_e.min())
    e_max_kev = j_a_kev(todas_e.max())

    # ------------------------------------------------------------------
    # Panel 1: Vista longitudinal (x vs z)
    # ------------------------------------------------------------------
    # Sombreamos la zona del Linac y marcamos sus bordes
    ax1.axvspan(-longitud_linac / 2, longitud_linac / 2, alpha=0.12,
                color='blue', label='Linac')
    ax1.axvline(-longitud_linac / 2, color='blue', ls='--', lw=0.8)
    ax1.axvline(longitud_linac / 2, color='blue', ls='--', lw=0.8)

    # Scatter vacío que se llenará frame a frame
    scatter1 = ax1.scatter([], [], c=[], cmap='plasma', s=10, alpha=0.8)
    ax1.set_xlim(z_min - margen_z, z_max + margen_z)
    ax1.set_ylim(x_min - margen_x, x_max + margen_x)
    ax1.set_xlabel('z (m)')
    ax1.set_ylabel('x (m)')
    ax1.set_title('Bunch en el Linac — Vista longitudinal')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    ax1.legend(loc='upper right', fontsize=8)

    # ------------------------------------------------------------------
    # Panel 2: Energía vs posición z
    # ------------------------------------------------------------------
    scatter2 = ax2.scatter([], [], c=[], cmap='plasma', s=10, alpha=0.8)
    ax2.set_xlim(z_min - margen_z, z_max + margen_z)
    ax2.set_ylim(e_min_kev, e_max_kev * 1.15)
    ax2.set_xlabel('z (m)')
    ax2.set_ylabel('Energía cinética (keV)')
    ax2.set_title('Energía de las partículas')
    ax2.grid(True, alpha=0.3)

    # Barra de color única (vinculada al panel de energía)
    norm = Normalize(vmin=e_min_kev, vmax=e_max_kev)
    fig.colorbar(scatter2, ax=ax2, label='Energía (keV)', shrink=0.8)

    # Título general con el tiempo simulado
    titulo_tiempo = fig.suptitle('', fontsize=12, y=1.02)

    # ------------------------------------------------------------------
    # Función de actualización — llamado por FuncAnimation en cada frame
    # ------------------------------------------------------------------
    def actualizar(frame):
        """Actualiza los datos de los scatter plots para el frame dado."""
        bunch = historico[frame]
        z = bunch.z
        x = bunch.x
        e_kev = j_a_kev(bunch.energia)

        # Actualizar panel 1 (x vs z)
        scatter1.set_offsets(np.column_stack([z, x]))
        scatter1.set_array(e_kev)
        scatter1.set_norm(norm)

        # Actualizar panel 2 (E vs z)
        scatter2.set_offsets(np.column_stack([z, e_kev]))
        scatter2.set_array(e_kev)
        scatter2.set_norm(norm)

        # Mostrar tiempo simulado en nanosegundos
        t_ns = frame * dt * 1e9
        titulo_tiempo.set_text(
            f'Simulación del Linac — Paso {frame}/{len(historico) - 1}'
            f' — t = {t_ns:.3f} ns'
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

    # Mostrar en pantalla
    if mostrar:
        plt.tight_layout()
        plt.show()

    return ani
