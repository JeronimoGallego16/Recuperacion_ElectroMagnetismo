"""
modulo_transferencia/animacion_booster.py — Animación del Booster en diferido


Estrategia (Opción A — Diferido / pre-calculado):
  La lógica (Booster.simular) ya calculó todos los frames y los guardó en
  una lista. Esta función SOLO reproduce esa lista como una película.
  Esto permite que el Front y el Back estén completamente separados.

La animación muestra DOS paneles sincronizados:
  1. Vista en planta (x vs z)  —  el haz de electrones girando en círculos
     alrededor del booster. Se dibuja el círculo de referencia del radio
     de diseño y el punto de inyección.
  2. Panel derecho con dos sub-gráficas apiladas:
     a. Energía cinética media (keV) vs paso de simulación
     b. Radio orbital medio (m) vs paso de simulación

Colores: plasma (azul = baja energía, amarillo/rojo = alta energía).
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize
from matplotlib.gridspec import GridSpec
from common.constants import CARGA_ELECTRON, VELOCIDAD_LUZ


def animar_booster(historico, radio_booster=2.0, intervalo=30,
                   mostrar=True, guardar=False):
    """Reproduce la animación del bunch en el Booster (3 paneles).

    Parameters
    ----------
    historico : list[Bunch]
        Lista de Bunch generada por Booster.simular(). Cada elemento es
        el estado del sistema en un instante de tiempo.
    radio_booster : float
        Radio de diseño del booster (m). Se usa para dibujar el círculo
        de referencia y el punto de inyección.
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
    n_frames = len(historico)

    # === Layout: 2 columnas (izquierda ancha, derecha estrecha) ===
    fig = plt.figure(figsize=(16, 9))
    fig.subplots_adjust(top=0.90, left=0.05, right=0.92, bottom=0.06)
    gs = GridSpec(2, 2, width_ratios=[1.5, 1], hspace=0.35, wspace=0.3)
    ax1 = fig.add_subplot(gs[:, 0])   # Órbita (toda la altura izquierda)
    ax2 = fig.add_subplot(gs[0, 1])   # Energía (arriba derecha)
    ax3 = fig.add_subplot(gs[1, 1])   # Radio (abajo derecha)

    # ==================================================================
    # Pre-cálculo de límites globales (todos los frames)
    # ==================================================================
    todas_x = np.concatenate([h.x for h in historico])
    todas_z = np.concatenate([h.z for h in historico])
    todas_e = np.concatenate([h.energia for h in historico])

    # Límites del plano xz con margen para el círculo de diseño
    x_min, x_max = todas_x.min(), todas_x.max()
    z_min, z_max = todas_z.min(), todas_z.max()
    margen_planta = max(x_max - x_min, z_max - z_min) * 0.15
    x_lim = (
        min(x_min, -radio_booster) - margen_planta,
        max(x_max, radio_booster) + margen_planta,
    )
    z_lim = (
        min(z_min, -radio_booster) - margen_planta,
        max(z_max, radio_booster) + margen_planta,
    )

    # Conversión: Joules → keV (más legible)
    def j_a_kev(e):
        return e / (CARGA_ELECTRON * 1e3)

    e_min_kev = j_a_kev(todas_e.min())
    e_max_kev = j_a_kev(todas_e.max())
    margen_e = (e_max_kev - e_min_kev) * 0.15 if e_max_kev > e_min_kev else 1.0

    # Normalización única del color (energía en keV)
    norm = Normalize(vmin=e_min_kev, vmax=e_max_kev)

    # Pre-calcular energía media y radio medio de CADA frame
    energia_media = np.array([j_a_kev(h.energia.mean()) for h in historico])
    radio_medio = np.array([
        np.sqrt(np.mean(h.x**2 + h.z**2)) for h in historico
    ])

    # ==================================================================
    # Panel 1: Vista en planta (x vs z) — órbita circular
    # ==================================================================
    # Círculo de referencia del booster
    theta = np.linspace(0, 2 * np.pi, 300)
    ax1.plot(radio_booster * np.cos(theta), radio_booster * np.sin(theta),
             '--', color='gray', lw=1.0, alpha=0.5,
             label=f'Radio de diseño = {radio_booster} m')
    # Punto de inyección (lado derecho)
    ax1.plot(radio_booster, 0, 'g*', markersize=14, label='Inyección')

    scatter1 = ax1.scatter([], [], c=[], cmap='plasma', s=10, alpha=0.8)
    ax1.set_xlim(x_lim)
    ax1.set_ylim(z_lim)
    ax1.set_xlabel('x (m)')
    ax1.set_ylabel('z (m)')
    ax1.set_title('Órbita en el Booster — haz de electrones')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    ax1.legend(loc='upper right', fontsize=8)

    # ==================================================================
    # Panel 2: Energía cinética media
    # ==================================================================
    line_e, = ax2.plot([], [], 'o-', color='orange', markersize=2, lw=1.5)
    ax2.set_xlim(0, n_frames - 1)
    ax2.set_ylim(e_min_kev - margen_e, e_max_kev + margen_e)
    ax2.set_xlabel('Paso de simulación')
    ax2.set_ylabel('Energía media (keV)')
    ax2.set_title('Evolución de la energía cinética')
    ax2.grid(True, alpha=0.3)

    # ==================================================================
    # Panel 3: Radio orbital medio
    # ==================================================================
    line_r, = ax3.plot([], [], 'o-', color='teal', markersize=2, lw=1.5)
    r_min, r_max = radio_medio.min(), radio_medio.max()
    margen_r = (r_max - r_min) * 0.15 if r_max > r_min else 0.5
    ax3.set_xlim(0, n_frames - 1)
    ax3.set_ylim(r_min - margen_r, r_max + margen_r)
    ax3.axhline(radio_booster, color='gray', ls='--', lw=0.8,
                label=f'R diseño = {radio_booster} m')
    ax3.set_xlabel('Paso de simulación')
    ax3.set_ylabel('Radio orbital medio (m)')
    ax3.set_title('Estabilización del radio orbital')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper right', fontsize=8)

    # Barra de color (compartida por todos los paneles)
    cbar = fig.colorbar(scatter1, ax=[ax1, ax2, ax3],
                         label='Energía (keV)',
                         shrink=0.6, location='right')

    # Título general con tiempo simulado
    titulo_tiempo = fig.suptitle(
        'Simulación del Booster', fontsize=15, y=0.96, fontweight='bold'
    )

    # ==================================================================
    # Función de actualización — llamado por FuncAnimation en cada frame
    # ==================================================================
    def actualizar(frame):
        """Actualiza los datos de los plots para el frame dado."""
        bunch = historico[frame]
        z = bunch.z
        x = bunch.x
        e_kev = j_a_kev(bunch.energia)

        # Panel 1: vista en planta (xz)
        scatter1.set_offsets(np.column_stack([x, z]))
        scatter1.set_array(e_kev)
        scatter1.set_norm(norm)

        # Panel 2: evolución de la energía media (hasta el frame actual)
        line_e.set_data(np.arange(frame + 1), energia_media[:frame + 1])

        # Panel 3: evolución del radio medio (hasta el frame actual)
        line_r.set_data(np.arange(frame + 1), radio_medio[:frame + 1])

        # Título: paso, energía media y radio medio actuales
        titulo_tiempo.set_text(
            f'Simulación del Booster  —  '
            f'Paso {frame}/{n_frames - 1}  —  '
            f'⟨E⟩ = {e_kev.mean():.2f} keV  —  '
            f'⟨R⟩ = {radio_medio[frame]:.3f} m'
        )

    # ==================================================================
    # Crear la animación
    # ==================================================================
    ani = animation.FuncAnimation(
        fig, actualizar, frames=n_frames,
        interval=intervalo, blit=False
    )

    # Guardar como GIF (requiere pillow instalado)
    if guardar:
        ani.save('booster_simulation.gif', writer='pillow', fps=30)

    # Mostrar en pantalla
    if mostrar:
        plt.show()

    return ani
