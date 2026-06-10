# Contexto — Refactorización Temporal

> Se relee al iniciar cada sesión para recuperar el hilo.

---

## 1. ¿De dónde venimos?

Postulomaniaco es un scraper + analizador de ofertas laborales que opera sobre un único proveedor: Computrabajo Colombia. El software funciona, pero creció de forma orgánica y acumuló scripts de prueba, lógica duplicada, archivos de migración ya cumplidos y acoplamiento entre el scraper y el pipeline de analytics.

No es un desastre. Es el resultado de iterar. Pero llegó el momento de ordenar.

---

## 2. ¿Hacia dónde vamos?

Van a ingresar nuevos scrapers de otros portales. Cada uno tendrá su propia lógica de extracción, pero compartirán el resto del ecosistema: limpieza, normalización, minería de tecnologías, motor de compatibilidad, persistencia, API y scheduler.

Necesitamos una arquitectura clara que defina dónde vive cada scraper, qué contrato debe cumplir para enchufarse al pipeline y qué es común vs. específico de cada fuente.

**Antes de construir lo nuevo, hay que ordenar la casa.**

---

## 3. ¿Qué es esta refactorización?

Una auditoría completa del proyecto con tres propósitos: limpiar, ordenar y definir la arquitectura para recibir nuevos scrapers. No se reescribe lógica funcional. Se quita lo que sobra, se mueve lo mal ubicado y se documenta lo decidido.

La carpeta `refactorizacion_temporal/` es desechable. Acompaña el proceso y se elimina al terminar.

---

## 4. Espíritu del proceso

Sin prisa. Una conversación donde cada tema se aborda con calma, se indaga y se resuelve antes de pasar al siguiente. No hay un plan rígido: el camino se traza sobre la marcha.

Cada sesión deja una huella escrita en esta carpeta para no repetir ni olvidar nada al día siguiente.

### Mi rol

Soy una segunda opinión. Observo, señalo deudas técnicas y duplicaciones, propongo estructuras y explico el porqué de cada sugerencia. Pregunto cuando algo no está claro. Me adapto a tu ritmo y nivel. Me equivoco y corrijo.

---

## 5. Objetivo final

Código limpio, arquitectura documentada y lista para nuevos scrapers, trazabilidad de lo decidido, y un desarrollador que entiende su software con criterio propio.
