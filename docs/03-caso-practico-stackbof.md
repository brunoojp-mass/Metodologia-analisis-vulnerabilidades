# 03 — Caso práctico: Stack Buffer Overflow en un binario propio

Este documento aplica la metodología de principio a fin sobre un **binario escrito por mí**
(`labs/vulnerable.c`), en una **VM aislada** y con las protecciones desactivadas para
simplificar el análisis en esta etapa inicial. Es el mismo enfoque del manual: *recorrer el
camino del fallo al exploit* para interiorizar cada fase.

> **Entorno:** Windows/Linux x86 (32 bits), binario compilado sin stack canaries y con pila
> ejecutable. Todo ocurre en laboratorio, sobre código propio. Ver [`labs/README.md`](../labs/README.md).

---

## Paso 0 — Por qué este caso

Buscaba un fallo **clásico pero aún vigente**, fácil de reproducir pero con trasfondo técnico:
el **Stack Buffer Overflow**. Permite recorrer todas las fases intermedias (crash → offsets →
control de flujo → PoC) y sienta la base para después activar protecciones y pasar a 64 bits.

El fallo está en el uso de `strcpy()` sin control de tamaño:

```c
void vulnerable_function(char *input) {
    char buffer[1000];
    strcpy(buffer, input);          // <-- sin verificación de tamaño -> Stack BOF
    printf("Has introducido: %s\n", buffer);
}
```

La versión segura reemplaza `strcpy()` por `strcpy_s()` comprobando el tamaño del destino
(ver [`labs/corregido.c`](../labs/corregido.c)).

---

## Paso 1 — Identificación y clasificación

- **Tipo de fallo:** desbordamiento de búfer en pila → **CWE-121 (Stack-based Buffer Overflow)**.
- **Causa raíz:** copia de una entrada controlada por el usuario a un búfer fijo sin validar
  longitud.
- **Fuente de identificación:** análisis estático del fuente + confirmación por fuzzing.

---

## Paso 2 — Contexto

| Dimensión | Valor en el lab |
|-----------|-----------------|
| Versión | Binario propio, build de laboratorio |
| SO / Arquitectura | x86 (32 bits) |
| Protecciones | Sin canary, pila ejecutable, (ASLR/DEP off en esta etapa) |
| Privilegios | Usuario del propio proceso |
| Superficie | Local — argumento por línea de comandos |

El registro de instrucción relevante en 32 bits es **`EIP`** (en 64 bits sería `RIP`).

---

## Paso 3 — Identificación del punto de entrada

En este binario el punto de entrada es evidente: **el argumento de línea de comandos**, que
llega a `vulnerable_function()` y se pasa **directo** a `strcpy()` sin control previo.

> En un binario real los puntos de entrada son más variados (ficheros, paquetes de red,
> formularios, APIs, dispositivos). Mapear la superficie temprano reduce el tiempo de las fases
> siguientes. *TODO: captura del flujo de datos trazado en Ghidra.*

---

## Paso 4 — Fuzzing para encontrar el umbral

Uso un fuzzer sencillo (ver [`labs/fuzzer.py`](../labs/fuzzer.py)) que envía cadenas cada vez
más largas hasta que el programa deja de comportarse con normalidad. El objetivo es detectar el
**umbral exacto** en el que pasa de estable a crash.

```
Enviando 100 bytes...  OK
Enviando 500 bytes...  OK
Enviando 1000 bytes... OK
Enviando 1100 bytes... CRASH (el proceso termina de forma anómala)
```

> *TODO: captura de la salida real de tu fuzzer y del tamaño que provoca el primer crash.*

El búfer es de 1000 bytes, pero el crash útil llega un poco más allá (hay que sobrepasar el
búfer, el guardado de `EBP` y alcanzar la dirección de retorno).

---

## Paso 5 — Análisis del crash y control de EIP

Reproduzco el crash bajo debugger (x32dbg/GDB) y observo el estado en el momento del fallo. La
pregunta central: **¿la dirección de retorno (`EIP`) acaba conteniendo bytes que yo controlo?**

Para localizar el **offset exacto** entre el inicio del búfer y `EIP`, uso un patrón cíclico no
repetitivo:

```text
1) Genero un patrón único:      pattern_create 1200
2) Lo paso como entrada y provoco el crash
3) Leo el valor que cayó en EIP (p. ej. 0x41367241)
4) Calculo el offset:           pattern_offset 0x41367241  ->  offset = N
```

Cuando controlo `EIP`, la confirmación clásica es sobrescribirlo con un valor reconocible y ver
que el debugger intenta ejecutar justo esa dirección:

```
[EIP] = 42424242   ("BBBB")   <-- control de flujo confirmado
```

> *TODO: captura del debugger con EIP = 42424242 y el valor de los demás registros.*

Esto cumple dos objetivos: **confirma el control de flujo** y permite **calcular el offset
exacto** para construir entradas precisas que sobrescriban `EIP` de forma controlada, evitando
corromper memoria de más y maximizando la estabilidad.

---

## Paso 6 — De control de EIP a prueba de concepto

Con el offset confirmado, la estructura de la entrada queda:

```
[ relleno hasta EIP ][ dirección de retorno controlada ][ ... ]
   N bytes                4 bytes (x86)
```

En lugar de apuntar a una dirección fija (frágil), el patrón robusto en estos labs es redirigir
`EIP` a una instrucción **`JMP ESP`** (o equivalente) presente en un módulo sin ASLR, de modo
que la ejecución salte a la zona que yo controlo justo después.

**Validación del control (PoC de laboratorio):** el objetivo aquí **no** es un payload
ofensivo, sino *demostrar que el control de ejecución es real*. El estándar didáctico es
ejecutar algo inocuo y visible — abrir `calc.exe` o imprimir un mensaje — exactamente como
muestra el manual. Eso basta para evidenciar RCE en el laboratorio.

> Me detengo deliberadamente en el nivel de *PoC de control de flujo*. No incluyo shellcode
> ofensivo ni cargas dirigidas: el objetivo académico es entender el mecanismo, y la cadena
> completa de pasos para generar un payload ya está suficientemente documentada en los recursos
> del módulo.

---

## Paso 7 — Diffing vulnerable vs. corregido

Compilo ambos binarios y los comparo con **BinDiff** (sobre Ghidra/IDA) para ver, a nivel de
ensamblador, qué cambió al pasar de `strcpy()` a `strcpy_s()`:

- Aparece la **comprobación de tamaño** antes de la copia.
- Cambia el flujo: ahora hay una rama que **aborta** si el tamaño excede el destino.

Esto entrena el ojo para reconocer, **sin fuente**, el patrón "copia insegura → copia
verificada" en binarios reales y parches de seguridad.

> *TODO: captura de BinDiff mostrando la función modificada y el bloque de verificación nuevo.*

---

## Paso 8 — Mitigación y cómo rompe la explotación

| Protección activada | Efecto sobre este exploit |
|---------------------|---------------------------|
| `strcpy_s()` (corrección de código) | Elimina la causa raíz: ya no hay overflow |
| Stack canary (`-fstack-protector`) | Detecta la sobrescritura antes del `ret` y aborta |
| DEP/NX | El salto a shellcode en pila provoca crash → fuerza ROP |
| ASLR | El `JMP ESP` fijo deja de ser fiable → obliga a info-leak |

La corrección en el código **elimina** la vulnerabilidad; las mitigaciones del sistema no la
eliminan pero **encarecen mucho** su explotación. Es el puente natural hacia la siguiente etapa
(64 bits + protecciones), documentada como trabajo futuro.

---

## Conclusiones del caso

1. Recorrer el camino completo —fuente → crash → offset → control de `EIP` → PoC → diffing—
   da una comprensión que ejecutar herramientas "a ciegas" nunca da.
2. El control de `EIP` es el punto de inflexión: pasar de "se rompe" a "controlo cómo se rompe".
3. El diffing cierra el círculo: entender la corrección es entender la vulnerabilidad desde el
   otro lado.

*TODO: añade tus propias conclusiones y qué te costó más durante la práctica.*
