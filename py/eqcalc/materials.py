"""Catálogo reducido de materiales (1 material por familia, intervalo de temperatura definido).

AVISO: valores de esfuerzo admisible transcritos de memoria/tablas públicas con fines académicos.
Deben contrastarse con ASME II-D (edición declarada), ASME B31.3 Tabla A-1 y API 650 Tabla 5-2
antes de cualquier uso. Fuera del intervalo declarado el programa NO extrapola: lanza error.
"""
from __future__ import annotations

MATERIALS = {
    # --- Tuberías: ASME B31.3 Tabla A-1 (esfuerzo básico S, MPa) -------------------------
    "A106-B": {
        "familia": "tuberia",
        "descripcion": "Acero al carbono sin costura ASTM A106 Gr.B",
        "norma_esfuerzo": "ASME B31.3 Tabla A-1 (verificar edición)",
        "YS": 240.0, "TS": 415.0,   # MPa, para esfuerzo de flujo (API 581 Ec. 2.13)
        "T_min": 20.0, "T_max": 399.0,
        # (temperatura °C, S MPa)
        "S_tabla": [(38, 137.9), (204, 137.9), (260, 137.9), (316, 137.9), (343, 137.9), (371, 130.3), (399, 119.3)],
        "E_defecto": 1.0,           # factor de calidad (sin costura)
    },
    # --- Recipientes: ASME II-D, Tabla 1A (SA-516 Gr.70) ----------------------------------
    "SA-516-70": {
        "familia": "recipiente",
        "descripcion": "Placa de acero al carbono ASME SA-516 Gr.70",
        "norma_esfuerzo": "ASME II-D Tabla 1A (verificar edición)",
        "YS": 260.0, "TS": 485.0,
        "T_min": 20.0, "T_max": 399.0,
        "S_tabla": [(40, 137.9), (343, 137.9), (371, 133.8), (399, 124.8)],
        "E_defecto": 0.85,
    },
    # --- Tanques: API 650 Tabla 5-2a (ASTM A36) --------------------------------------------
    "A36": {
        "familia": "tanque",
        "descripcion": "Placa de acero ASTM A36 (API 650)",
        "norma_esfuerzo": "API 650 Tabla 5-2a (verificar edición)",
        "YS": 250.0, "TS": 400.0,
        "Sd": 160.0, "St": 171.0,   # esfuerzo de diseño y de prueba hidrostática, MPa (T ≤ 93 °C)
        "T_min": 0.0, "T_max": 93.0,
        "E_defecto": 0.85,
    },
}


class MaterialError(ValueError):
    pass


def get_material(nombre: str) -> dict:
    if nombre not in MATERIALS:
        raise MaterialError(f"Material '{nombre}' fuera del catálogo reducido ({', '.join(MATERIALS)}).")
    return MATERIALS[nombre]


def allowable_stress(nombre: str, T: float) -> float:
    """Esfuerzo admisible S [MPa] a la temperatura T [°C] por interpolación lineal en la tabla."""
    mat = get_material(nombre)
    if "S_tabla" not in mat:
        raise MaterialError(f"'{nombre}' no usa tabla S(T); ver Sd/St de API 650.")
    if not (mat["T_min"] <= T <= mat["T_max"]):
        raise MaterialError(
            f"Temperatura {T:g} °C fuera del intervalo declarado para {nombre} "
            f"({mat['T_min']:g}–{mat['T_max']:g} °C)."
        )
    tabla = mat["S_tabla"]
    if T <= tabla[0][0]:
        return tabla[0][1]
    for (t0, s0), (t1, s1) in zip(tabla, tabla[1:]):
        if t0 <= T <= t1:
            return s0 + (s1 - s0) * (T - t0) / (t1 - t0)
    return tabla[-1][1]
