# Recuperacion_ElectroMagnetismo — Simulación de Sincrotrón

## Acuerdo del equipo: estructura del Bunch

Cada electrón es una fila en un array NumPy (N, 7). La clase `Bunch` envuelve esa matriz:

| Columna | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---------|---|---|---|---|---|---|---|
| Variable | x | y | z | vx | vy | vz | energia |
| Propiedad | `.x` | `.y` | `.z` | `.vx` | `.vy` | `.vz` | `.energia` |

- Acceso al array crudo: `bunch.datos` (array NumPy de forma (N, 7))
- Índices en `common.constants`: `X=0, Y=1, Z=2, VX=3, VY=4, VZ=5, ENERGIA=6`
- Unidades: posiciones en m, velocidades en m/s, energía en J

## Pipeline final (cuando estén los 3 integrantes)

```python
from common import Bunch
from modulo_inyeccion import Linac, animar_linac
from modulo_transferencia import Booster, animar_booster
from modulo_anillo import Ring, animar_ring

bunch = Bunch.generar_inicial(n_particulas=200)

linac = Linac()
historico_linac = linac.simular(bunch)       # Int. 1
animar_linac(historico_linac)

booster = Booster()
historico_booster = booster.simular(historico_linac[-1])  # Int. 2
animar_booster(historico_booster)

ring = Ring()
historico_ring = ring.simular(historico_booster[-1])      # Int. 3
animar_ring(historico_ring)
```

## Arquitectura

```
├── main.py
├── common/
│   ├── constants.py          # Constantes físicas + índices de columna
│   └── bunch.py              # Clase Bunch (envuelve el array N×7)
├── modulo_inyeccion/         # Integrante 1 ✅
│   ├── generador_bunch.py    # generar_bunch_inicial()
│   ├── fisica_linac.py       # Clase Linac con método .simular()
│   └── animacion_linac.py    # animar_linac(historico)
├── modulo_transferencia/     # Integrante 2 ⬜
│   ├── fisica_booster.py     # Clase Booster con .simular() — Lorentz, dipolos
│   ├── animacion_booster.py  # animar_booster() — haz circular
│   └── mock_bunch.py         # 🟡 Datos de prueba (para desarrollo aislado)
└── modulo_anillo/            # Integrante 3 ⬜
    ├── fisica_ring.py        # Clase Ring con .simular() — cuadrupolos, undulator
    ├── animacion_ring.py     # animar_ring() — espacio fase, zigzag
    └── mock_bunch.py         # 🟡 Datos de prueba (para desarrollo aislado)
```

## Cómo deben usar la clase Bunch los otros integrantes

```python
from common import Bunch

# Para crear un bunch desde cero (mock o real):
datos = np.zeros((n, 7))
# ... llenar columnas ...
bunch = Bunch(datos)

# Para leer propiedades:
print(bunch.z)        # array de posiciones z
print(bunch.energia)  # array de energías

# Para pasar datos a la siguiente etapa:
bunch_siguiente = bunch  # el Bunch completo viaja entre módulos

# Para acceder al array NumPy crudo (si necesitan indexing directo):
arr = bunch.datos  # shape (N, 7)
```

## Trabajo en paralelo con mock data

- `modulo_transferencia.mock_bunch.generar_bunch_post_linac()` → devuelve un `Bunch` simulando la salida del Linac. El Integrante 2 puede desarrollar su Booster sin esperar al Integrante 1.
- `modulo_anillo.mock_bunch.generar_bunch_post_booster()` → devuelve un `Bunch` simulando la salida del Booster. El Integrante 3 puede desarrollar el Ring sin esperar a los otros dos.

## Ejecutar

```bash
pip install numpy matplotlib
python main.py
```
