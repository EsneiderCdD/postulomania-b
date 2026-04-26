# Modelo de Correlación y Compatibilidad

Este documento describe el motor de inteligencia de datos utilizado para puntuar la compatibilidad entre el perfil del desarrollador y las ofertas laborales extraídas de CompuTrabajo.

## 1. El Modelo Matemático (WMS - Weighted Match Score)

La compatibilidad se calcula como un porcentaje (0% a 100%) utilizando cuatro pilares fundamentales:

### A. Afinidad Técnica (70% del peso base)
Se basa en la coincidencia exacta entre el `tech_stack` extraído de la oferta y los valores asignados en `user_profile.json`.
*   **Fórmula**: `Promedio de (Valores del Usuario para Tecnologías Requeridas)`
*   **Neutralidad**: Si la oferta no especifica requisitos técnicos, se asigna un valor base de 0.5.

### B. Factor de Experiencia (30% del peso base)
Compara los años de experiencia requeridos por la oferta (`experiencia_anios`) contra los declarados en el perfil.
*   **Cumple/Supera**: Si `User_Exp >= Req_Exp`, el factor es 1.0.
*   **No cumple**: El factor es proporcional: `User_Exp / Req_Exp`.

### C. Penalización de Idioma (Multiplicador Crítico)
El inglés actúa como un filtro de protección.
*   **Sin Inglés**: Si la oferta no lo requiere, el multiplicador es 1.0.
*   **Con Inglés**: El puntaje total se multiplica por el nivel de inglés del usuario (0.0 a 1.0).

### D. Nivel Educativo y Compensación
Normaliza los niveles (Técnico=1, Tecnólogo=2, Ingeniero=3).
*   **Compensación**: Si el usuario tiene menos educación de la pedida pero tiene **>= 2 años extra** de experiencia sobre el requisito, la penalización por educación se anula.
*   **Penalización**: En caso de no cumplir y no compensar, se aplica una reducción del 10% al puntaje final.

---

## 2. Implementación en el Software

### Configuración del Perfil
*   **Archivo**: `profile/user_profile.json`
*   **Instrucciones**: El usuario debe calificar sus saberes de **0.0 a 1.0**.
    *   0.3 - 0.5: Junior / Autonomía básica.
    *   0.6 - 0.8: Mid / Autonomía total.
    *   0.9 - 1.0: Senior / Experto.

### Archivos Clave
1.  `analytics/correlator.py`: Contiene la función `calculate_score` y la lógica de negocio. Es el "cerebro".
2.  `analytics/master_sync.py`: Integra el correlador en el flujo de sincronización global.
3.  `analytics/processes/mining.py`: Extrae las variables (tecnologías, años, inglés, educación) de la descripción de la vacante.

### Ubicación de Resultados
Los resultados se proyectan directamente en la **Tabla Maestra**:
*   `data/global/master_analytics.json` -> Columna `"compatibilidad"`.
