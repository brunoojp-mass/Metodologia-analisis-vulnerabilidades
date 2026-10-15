# 04 — Aproximación a un 0day: mi flujo de investigación

Un 0day es una vulnerabilidad **aún no divulgada ni parcheada**. No hay CVE, no hay write-up,
no hay parche que diffear. Aquí la metodología de [`01-metodologia.md`](01-metodologia.md) se
vuelve más exigente porque desaparecen los atajos. Describo cómo lo abordaría de forma
práctica, que es justo lo que pide la actividad: *fuzzing, diffing, reversing y entorno*.

---

## 1. Montaje del entorno

Un buen entorno es la mitad del trabajo. Mi setup base:

- **Aislamiento total:** VM dedicada, snapshot limpio, red *host-only* o sin red. Nada toca
  producción.
- **Reproducibilidad:** versión exacta del objetivo fijada y documentada; capacidad de volver
  al snapshot entre pruebas.
- **Observabilidad:** debugger acoplado (x64dbg/WinDbg/GDB+GEF), sanitizers cuando puedo
  recompilar (ASAN/UBSAN), logging del objetivo al máximo.
- **Automatización:** scripts para lanzar/reiniciar el objetivo, capturar crashes y clasificarlos.

> Si el objetivo es un servicio de red o un parser de ficheros, preparo además un *harness*
> que exponga el punto de entrada de forma aislada y rápida de ejecutar (clave para que el
> fuzzing tenga rendimiento).

---

## 2. Mapeo de la superficie de entrada

Antes de lanzar nada, identifico **todos los puntos por los que entran datos**: argumentos,
ficheros de configuración, formatos que parsea, paquetes de red, IPC, APIs, dispositivos.
Cada canal es un vector candidato. Priorizo por:

1. **Accesibilidad** (¿remoto sin autenticación? sube de prioridad).
2. **Complejidad del parser** (más parsing = más superficie de fallo).
3. **Antigüedad / origen** (código legacy o de terceros poco auditado).

---

## 3. Fuzzing dirigido

El fuzzing es mi principal motor de descubrimiento cuando no hay fuente o el parser es complejo.

- **Elección de fuzzer según el objetivo:**
  - Binario recompilable → **AFL++** con instrumentación (cobertura).
  - Binario Windows cerrado → **WinAFL** (DynamoRIO) sobre la función objetivo.
  - Protocolo/estructura estricta → **boofuzz** (modelo el formato campo a campo).
  - Caja negra rápida → **radamsa** mutando entradas válidas.
- **Corpus de semillas** de calidad: entradas válidas y variadas que ejerzan muchas rutas.
- **Harness** que aísle el punto de entrada y permita miles de ejecuciones por segundo.
- **Retroalimentación por cobertura**: dejo que el fuzzer priorice entradas que abren rutas
  nuevas.

El resultado no es "el exploit": es una **colección de crashes** que hay que triar.

---

## 4. Triage de crashes

No todo crash es explotable. Mi criterio para separar ruido de oro:

| Señal | Interpretación |
|-------|----------------|
| Null-pointer dereference | Normalmente **no** explotable (DoS a lo sumo) |
| Escritura en dirección controlada | Muy prometedor (*write-what-where*) |
| Control de `EIP/RIP` | Candidato fuerte a RCE |
| Corrupción de heap / metadatos | Potencial, requiere trabajo (grooming) |
| Lectura fuera de límites | Posible **info-leak** (útil contra ASLR) |

Herramientas: ASAN para entender el tipo de corrupción, `!exploitable`/analizadores de crash,
y clasificación por hash de stack para deduplicar.

---

## 5. Reversing para encontrar la causa raíz

Con un crash prometedor, paso a **ingeniería inversa** para entender *por qué* ocurre:

1. **Estático** (Ghidra/IDA): localizo la función que falla, reconstruyo su lógica, identifico
   la operación insegura (copia sin límite, cálculo de tamaño erróneo, índice sin validar…).
2. **Dinámico** (debugger): sigo la propagación de **mi** entrada registro a registro, confirmo
   qué bytes controlan qué, y acoto las restricciones (badchars, longitudes, validaciones).
3. Formulo la **causa raíz** con precisión (idealmente mapeada a un CWE).

El objetivo de esta fase es pasar de *"crashea con esta entrada"* a *"crashea porque la función
X calcula mal el tamaño en la línea Y, y eso me da la primitiva Z"*.

---

## 6. Diffing (cuando sí aplica)

En un 0day puro no hay parche que comparar, pero el diffing sigue siendo útil en escenarios
intermedios:

- **N-day / 1-day:** cuando sale un parche, lo diffeo contra la versión previa para localizar la
  función corregida y reconstruir el fallo antes de que haya exploit público.
- **Variant analysis:** tras encontrar un fallo, busco **el mismo patrón** en funciones
  hermanas del mismo binario (los bugs raramente vienen solos).

Herramientas: BinDiff, Diaphora.

---

## 7. De la primitiva al PoC

Una vez entendida la primitiva (control de flujo, write-what-where, info-leak…), construyo un
**PoC mínimo que demuestre explotabilidad** y encadeno lo necesario según las protecciones:

- Info-leak para derrotar ASLR → obtener una base válida.
- ROP para sortear DEP/NX.
- Encadenado fiable y reproducible.

> En investigación legítima, el PoC se queda en lo necesario para evidenciar el impacto, y el
> siguiente paso es **disclosure responsable** al fabricante, no la publicación de un arma.

---

## 8. Documentación y divulgación

Cierro con un informe que cualquier otro analista (o el fabricante) pueda seguir: causa raíz,
condiciones, impacto, PoC reproducible y mitigación propuesta. Si es un 0day real, prima el
**disclosure coordinado**.

---

## Diagrama del flujo (mapa mental en texto)

```
             ┌─────────────┐
             │   ENTORNO   │  VM aislada, snapshot, debugger, harness
             └──────┬──────┘
                    ▼
          ┌───────────────────┐
          │ MAPEO DE SUPERFICIE│  ¿por dónde entran los datos?
          └─────────┬─────────┘
                    ▼
            ┌───────────────┐        ┌──────────────────┐
            │    FUZZING     │ ─────► │  TRIAGE CRASHES  │
            └───────┬───────┘        └────────┬─────────┘
                    │  (retroalimenta)         │ (crash prometedor)
                    ▼                          ▼
            ┌───────────────┐          ┌───────────────┐
            │ CORPUS/HARNESS│          │   REVERSING   │  causa raíz + primitiva
            └───────────────┘          └───────┬───────┘
                                               ▼
                                     ┌───────────────────┐
                                     │  PoC + BYPASS      │  (ASLR/DEP/canary…)
                                     └─────────┬─────────┘
                                               ▼
                                     ┌───────────────────┐
                                     │ INFORME + DISCLOSURE│
                                     └───────────────────┘
```


