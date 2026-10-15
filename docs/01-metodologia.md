# 01 — Mi metodología de análisis de vulnerabilidades

El análisis de una vulnerabilidad no es un procedimiento mecánico, sino un proceso
**multidimensional** que combina técnicas estáticas y dinámicas, razonamiento lógico y
conocimiento profundo de la tecnología objetivo. Por eso mi metodología no es una receta
paso a paso: es un marco de fases que **se retroalimentan** y entre las que salto según lo que
voy descubriendo.

Antes de las fases, dos ideas que para mí son el núcleo de la mentalidad del analista:

1. **Una vulnerabilidad no es una amenaza por sí sola.** Es una puerta potencial. Que exista
   no significa que sea explotable: la explotabilidad real depende del entorno, las
   protecciones activas, la superficie de ataque y mil variables de tiempo de ejecución.
2. **El objetivo no es "petar" el programa, es entenderlo.** Un crash es el principio, no el
   final. La pregunta importante no es *"¿se rompe?"* sino *"¿puedo controlar cómo se rompe?"*.

---

## Fase 1 — Identificación del fallo

Todo empieza con la detección de un comportamiento anómalo o no deseado. Las fuentes que
uso, de más automática a más manual:

- **Fuzzing**: lanzar entradas masivas y malformadas para provocar fallos inesperados.
- **Análisis estático** de código fuente (si lo tengo) o del binario.
- **Diffing entre versiones**: un parche reciente suele revelar qué fallo se corrigió.
- **Inteligencia pública**: CVE, NVD, CWE, Exploit-DB, GitHub, write-ups, y foros/canales
  de seguridad.

**Mentalidad en esta fase:** amplitud antes que profundidad. Recojo señales sin casarme
todavía con ninguna hipótesis.

**Herramientas típicas:** AFL++/WinAFL/boofuzz/radamsa, Ghidra, grep/semgrep sobre fuentes,
BinDiff/Diaphora, lectores de CVE.

---

## Fase 2 — Clasificación y tipificación

Una vez detecto algo raro, determino **la naturaleza del fallo**. Esto condiciona todo lo que
viene después: las herramientas, las protecciones que tendré que esquivar y el tipo de
primitiva que puedo construir. Pregunta guía: *¿qué clase de fallo es?*

- Desbordamiento de búfer (stack o heap)
- Use-After-Free (uso de memoria liberada)
- Validación incorrecta de entrada → inyección
- Gestión indebida de privilegios → escalada
- Condición de carrera, type confusion, integer overflow, etc.

Me apoyo en la taxonomía **CWE** para nombrar el fallo con rigor; eso me permite buscar
patrones conocidos y mitigaciones asociadas.

---

## Fase 3 — Entendimiento del contexto

Una vulnerabilidad aislada dice poco. El contexto define la estrategia y los límites del
impacto. Las cinco preguntas que siempre respondo:

| Pregunta | Por qué importa |
|----------|-----------------|
| ¿Qué **versión** del software está afectada? | Delimita el rango vulnerable y el parche |
| ¿Qué **SO y arquitectura**? (x86/x64/ARM) | Cambia offsets, calling conventions, mitigaciones |
| ¿Qué **protecciones** están activas? | ASLR, DEP/NX, stack canaries, CFG, etc. |
| ¿Qué **nivel de privilegios** tiene el atacante? | Define el objetivo (RCE, LPE, DoS…) |
| ¿Cuál es la **superficie de ataque**? | ¿Remota? ¿Local? ¿Autenticada? |

> Un fallo trivial en 32 bits puede volverse muy complejo en 64 bits (más entropía de ASLR,
> convención de paso de argumentos por registros, etc.). El contexto no es un trámite: es
> media investigación.

---

## Fase 4 — Exploración del vector de explotación

Aquí empieza la investigación técnica profunda. Mi rutina:

1. Reproducir el fallo de forma **controlada y determinista** (misma entrada → mismo crash).
2. Ejecutar bajo **debugger** y observar el estado en el momento del fallo:
   - valor de los registros (¿controlo `EIP`/`RIP`?),
   - contenido de la pila,
   - punteros y estructuras relevantes.
3. Tomar notas del estado a bajo nivel y buscar **qué parte de mi entrada acaba dónde**.
4. Formular una hipótesis: *"si controlo X, puedo redirigir el flujo hacia Y"*.

**Herramientas:** x64dbg/x32dbg, GDB+pwndbg/GEF, WinDbg, Ghidra/IDA para correlacionar el
desensamblado con el comportamiento dinámico.

---

## Fase 5 — Construcción del exploit (en laboratorio)

Cuando entiendo el fallo y su impacto potencial, intento transformarlo en algo útil **dentro
del laboratorio**:

- **Cálculo de offsets** para sobrescribir con precisión la dirección de retorno / registros
  clave (patrones cíclicos tipo `pattern_create`/`pattern_offset`, o `mona.py`).
- **Diseño del payload**: en un PoC de laboratorio basta con "probar control" (p. ej. lanzar
  `calc.exe` o mostrar un mensaje). Es la forma estándar de **validar** que el control de
  ejecución es real, sin construir nada ofensivo contra terceros.
- **Bypass de protecciones** cuando las activo: ROP para DEP/NX, info-leaks para ASLR, etc.
- **Iteración** hasta conseguir algo **fiable y reproducible** (la fiabilidad importa tanto
  como el impacto).

> En este repositorio me quedo deliberadamente en el nivel de *prueba de concepto de
> control de flujo* sobre mi propio binario. El objetivo académico es **entender** el
> mecanismo, no producir armamento.

---

## Fase 6 — Validación, prueba y documentación

Con el PoC en mano:

- Valido que funciona en **distintas ejecuciones/configuraciones** (¿es estable?).
- Confirmo exactamente qué consigue (control de flujo, ejecución, DoS…).
- Redacto un **informe técnico** reproducible: condiciones necesarias, causa raíz, impacto y
  propuesta de mitigación/corrección.

Un buen informe es tan importante como el hallazgo: si otro analista no puede reproducirlo y
entenderlo, el trabajo vale la mitad.

---

## Fase 7 — Reporte / divulgación

Según el contexto (empresa, bug bounty, investigación independiente):

- **Disclosure responsable** al fabricante antes de publicar nada.
- Publicación de un CVE o write-up técnico cuando procede.
- Informe claro con pruebas reproducibles.
- En ciertos casos, compartir una PoC (con o sin exploit completo).

---

## Resumen de herramientas por fase

| Fase | Herramientas de referencia |
|------|----------------------------|
| Identificación | AFL++, WinAFL, boofuzz, radamsa, Ghidra, BinDiff, nmap (NSE) |
| Clasificación | CWE, lectura de CVE/NVD, triage de crashes (ASAN, `!exploitable`) |
| Contexto | `checksec`, `readelf`, PE-bear, detección de mitigaciones |
| Exploración | x64dbg, GDB+GEF/pwndbg, WinDbg, IDA/Ghidra |
| Construcción | `pattern_create`/`pattern_offset`, `mona.py`, msfvenom (PoC lab), ROPgadget |
| Validación/doc | PwnDoc, Faction, capturas, informes propios |
| Reporte | Plantillas de disclosure, CVE request, write-up |

---

## La mentalidad, en una frase

> *No busco romper programas; busco demostrar que entiendo por qué se rompen, con qué
> precisión y bajo qué condiciones — porque solo así puedo también defenderlos.*
