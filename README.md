# Metodología de análisis de vulnerabilidades y desarrollo de exploits

> **Máster en Ciberseguridad — Módulo 6: Vulnerabilidades**
> Tarea individual: *Metodología de análisis de vulnerabilidades y explotación*
>
> **Autor:** `Bruno Juste Pérez`
> **Repositorio:** `https://github.com/brunoojp-mass/Metodologia-analisis-vulnerabilidades`
> **Fecha:** `15/10/2026`

---

## 1. Propósito de este repositorio

Este proyecto documenta mi **visión y metodología personal** para el análisis de
vulnerabilidades en software real y el desarrollo de exploits, construida a partir de los
contenidos del módulo, de lecturas técnicas y de práctica en un entorno de laboratorio
controlado.

No pretende ser un recetario cerrado, sino un marco de trabajo flexible y realista: la
forma en la que yo abordaría una vulnerabilidad desde que detecto un comportamiento
anómalo hasta que soy capaz de entenderlo, reproducirlo y, en un laboratorio propio,
demostrar su explotabilidad.

El repositorio está pensado como pieza de **portfolio profesional**: algo que podría enseñar
en una entrevista técnica para evidenciar criterio, estructura y capacidad de investigación
autónoma.

> ⚠️ **Ámbito y ética.** Todo el trabajo práctico se realiza sobre binarios escritos por mí
> (`labs/vulnerable.c`), en una máquina virtual aislada y sin conexión a redes de producción.
> El análisis de CVEs reales se limita a la comprensión de su causa raíz y de las lecciones de
> diseño que enseñan, con fines de aprendizaje y defensa.

---

## 2. Índice de contenidos

| Documento | Contenido |
|-----------|-----------|
| [`docs/01-metodologia.md`](docs/01-metodologia.md) | Mi metodología: fases, mentalidad y herramientas por fase |
| [`docs/02-conceptos-clave.md`](docs/02-conceptos-clave.md) | Base conceptual: vulnerabilidad, exploit, payload y mitigaciones modernas |
| [`docs/03-caso-practico-stackbof.md`](docs/03-caso-practico-stackbof.md) | Caso práctico guiado: Stack Buffer Overflow en un binario propio (32 bits) |
| [`docs/04-flujo-0day.md`](docs/04-flujo-0day.md) | Aproximación a un 0day: fuzzing, diffing, reversing y montaje del entorno |
| [`docs/05-casos-reales-cve.md`](docs/05-casos-reales-cve.md) | CVEs reales estudiados y patrones aprendidos |
| [`referencias.md`](referencias.md) | Bibliografía, write-ups, cursos y recursos |

Código y material de laboratorio:

| Recurso | Descripción |
|---------|-------------|
| [`labs/vulnerable.c`](labs/vulnerable.c) | Programa deliberadamente vulnerable (Stack BOF) |
| [`labs/corregido.c`](labs/corregido.c) | Versión corregida con función segura |
| [`labs/fuzzer.py`](labs/fuzzer.py) | Fuzzer didáctico (cadenas crecientes) para encontrar el umbral de fallo |
| [`labs/README.md`](labs/README.md) | Cómo compilar y reproducir el laboratorio |

---

## 3. Resumen de la metodología (vista rápida)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     CICLO DE ANÁLISIS DE VULNERABILIDADES                   │
│                    (no lineal — las fases se retroalimentan)                │
└──────────────────────────────────────────────────────────────────────────┘

  [1] Identificación        →  Detecto un comportamiento anómalo o un fallo
          │                     (fuzzing, análisis estático, diffing, CVE/CWE)
          ▼
  [2] Clasificación         →  ¿Qué tipo de fallo es? (BOF, UAF, iny., privesc…)
          │
          ▼
  [3] Contexto              →  Versión, SO, arquitectura, protecciones, superficie
          │
          ▼
  [4] Exploración vector    →  Debugging, crash dumps, estado de registros/pila
          │
          ▼
  [5] Construcción exploit  →  Offsets, control de EIP/RIP, bypass, payload (lab)
          │
          ▼
  [6] Validación + doc.     →  Reproducibilidad, impacto, informe técnico
          │
          ▼
  [7] Reporte / divulgación →  Disclosure responsable, CVE, write-up, PoC
```

Cada fase se desarrolla en [`docs/01-metodologia.md`](docs/01-metodologia.md).

---

## 4. Entorno de trabajo

- **Host:** `VM Windows`
- **VM de laboratorio:** `Windows 10 (x89)` aislada (red *host-only*)
- **Compilador:** MingGW (Windows)
- **Toolchain principal:** Ghidra, x64dbg / x32dbg, BindDiff, fuzzer propio en python, AFL++/WinAFL

Detalle reproducible en [`labs/README.md`](labs/README.md).

---

## 5. Cómo leer este repositorio

Si vienes de una entrevista o eres otro analista:

1. Empieza por [`docs/01-metodologia.md`](docs/01-metodologia.md) para entender *cómo pienso*.
2. Sigue con [`docs/03-caso-practico-stackbof.md`](docs/03-caso-practico-stackbof.md) para ver *la metodología aplicada de principio a fin*.
3. Termina con [`docs/04-flujo-0day.md`](docs/04-flujo-0day.md) para ver *cómo extrapolaría todo a una vulnerabilidad desconocida*.

---

## 6. Checklist de personalización (bórrala antes de entregar)

- [ ] Rellenar nombre, URL del repo y fecha.
- [ ] Sustituir los bloques `<...>` y los `TODO:` por contenido propio.
- [ ] Añadir capturas **reales** de tu laboratorio (crash en el debugger, EIP sobrescrito, diffing en BinDiff/Ghidra, salida del fuzzer).
- [ ] Completar en `docs/05-casos-reales-cve.md` con observaciones propias de los CVEs que **de verdad** hayas estudiado.
- [ ] Revisar que todo lo que afirmas haber hecho, lo has hecho tú.
- [ ] Verificar las referencias (yo no tengo acceso a internet; comprueba cada enlace/dato).
