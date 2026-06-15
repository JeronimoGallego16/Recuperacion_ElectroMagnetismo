"""
# common/bunch.py — Clase Bunch: envuelve la matriz de electrones (N, 7)

# Esta clase es el contrato del equipo. Todos los módulos reciben y
# devuelven instancias de Bunch. El array NumPy crudo vive en bunch.datos.
#
# Uso típico:
#   bunch = Bunch.generar_inicial(200)       # crear con distribución Gaussiana
#   print(bunch.z)                           # todas las posiciones z
#   print(bunch.energia)                     # todas las energías
#   arr = bunch.datos                        # array NumPy (N, 7) subyacente

"""
import numpy as np
from common.constants import (
    X, Y, Z, VX, VY, VZ, ENERGIA,
    MASA_ELECTRON,
)


class Bunch:
    """Contenedor para un conjunto de electrones (bunch).

    Atributo principal:
        datos : ndarray  —  array NumPy de forma (N, 7), donde N = n_particulas
                            Cada fila es un electrón con columnas [x,y,z,vx,vy,vz,E]
    """

    def __init__(self, datos=None, n_particulas=0):
        """Inicializa el bunch a partir de un array existente o crea uno vacío.

        Parameters
        ----------
        datos : array_like, opcional
            Array de forma (N, 7) con los datos de los electrones.
        n_particulas : int, opcional
            Si no se pasan datos, crea un bunch vacío con este número de partículas.
        """
        if datos is not None:
            self.datos = np.asarray(datos, dtype=float)
        else:
            self.datos = np.zeros((n_particulas, 7))

        # Metadatos opcionales usados por el módulo del anillo.
        # No forman parte de la matriz principal del bunch.
        self.intensidad_fotones = 0.0
        self.z_media = 0.0

    # ------------------------------------------------------------------
    # Propiedades de acceso a columnas por nombre
    # ------------------------------------------------------------------
    # Permiten escribir  bunch.z  en lugar de  bunch.datos[:, Z]
    # ------------------------------------------------------------------

    @property
    def x(self):
        return self.datos[:, X]

    @property
    def y(self):
        return self.datos[:, Y]

    @property
    def z(self):
        return self.datos[:, Z]

    @property
    def vx(self):
        return self.datos[:, VX]

    @property
    def vy(self):
        return self.datos[:, VY]

    @property
    def vz(self):
        return self.datos[:, VZ]

    @property
    def energia(self):
        return self.datos[:, ENERGIA]

    @property
    def n_particulas(self):
        """Número de electrones en el bunch."""
        return self.datos.shape[0]

    # ------------------------------------------------------------------
    # Métodos de utilidad
    # ------------------------------------------------------------------

    def copia(self):
        """Devuelve una copia independiente del Bunch."""
        nuevo_bunch = Bunch(self.datos.copy())
        nuevo_bunch.intensidad_fotones = self.intensidad_fotones
        nuevo_bunch.z_media = self.z_media
        return nuevo_bunch

    def actualizar_energia(self):
        """Recalcula la energía cinética de cada partícula desde las velocidades.

        Fórmula:  E = 0.5 * m_e * (vx² + vy² + vz²)

        Se llama automáticamente en cada paso de simulación, pero está
        expuesto por si algún módulo modifica las velocidades manualmente.
        """
        v2 = self.vx**2 + self.vy**2 + self.vz**2
        self.datos[:, ENERGIA] = 0.5 * MASA_ELECTRON * v2

    # ------------------------------------------------------------------
    # Método de fábrica (classmethod) — generar bunch inicial
    # ------------------------------------------------------------------

    @classmethod
    def generar_inicial(cls, n_particulas=200, sigma_pos=5e-4, sigma_vel=5e5,
                        v0_axial=1e7, seed=None):
        """Crea un Bunch con distribución Gaussiana en posición y velocidad.

        Simula la emisión de electrones desde un cañón:
          - Posiciones (x, y, z) centradas en 0 con dispersión sigma_pos
          - Velocidades transversales (vx, vy) centradas en 0 con sigma_vel
          - Velocidad longitudinal (vz) centrada en v0_axial con sigma_vel
          - Energía calculada desde la velocidad

        Parameters
        ----------
        n_particulas : int
            Número de electrones en el bunch.
        sigma_pos : float
            Desviación estándar de la posición (m).
        sigma_vel : float
            Desviación estándar de la velocidad (m/s).
        v0_axial : float
            Velocidad longitudinal media (m/s) — eje z.
        seed : int, opcional
            Semilla para reproducibilidad.

        Returns
        -------
        Bunch
            Instancia con los electrones generados.
        """
        if seed is not None:
            np.random.seed(seed)

        # Matriz vacía de forma (N, 7)
        datos = np.zeros((n_particulas, 7))

        # Posiciones: Gaussiana centrada en 0
        datos[:, X] = np.random.normal(0, sigma_pos, n_particulas)
        datos[:, Y] = np.random.normal(0, sigma_pos, n_particulas)
        datos[:, Z] = np.random.normal(0, sigma_pos * 2, n_particulas)

        # Velocidades: Gaussiana con media v0_axial en el eje z
        datos[:, VX] = np.random.normal(0, sigma_vel, n_particulas)
        datos[:, VY] = np.random.normal(0, sigma_vel, n_particulas)
        datos[:, VZ] = np.random.normal(v0_axial, sigma_vel, n_particulas)

        # Energía cinética E = 0.5 * m * v²
        v2 = datos[:, VX]**2 + datos[:, VY]**2 + datos[:, VZ]**2
        datos[:, ENERGIA] = 0.5 * MASA_ELECTRON * v2

        return cls(datos)
