# 02 — Base conceptual

Resumo aquí, con mis palabras, los conceptos que sostienen toda la metodología. El objetivo
es demostrar que no uso los términos de memoria, sino que entiendo cómo se relacionan.

---

## Los tres pilares

### Vulnerabilidad
Debilidad inherente en un sistema, aplicación, servicio o hardware que puede ser aprovechada
para obtener un comportamiento no previsto por el desarrollador. Puede originarse en el
**diseño**, en la **implementación** o en el **despliegue/configuración**.

Técnicamente, se materializa cuando hay una **desviación entre la lógica implementada y el
modelo de seguridad esperado**: un buffer overflow que sobrescribe memoria adyacente, un
use-after-free que deja manipular estructuras internas, una validación de entrada deficiente
que permite inyección, etc.

### Exploit
El **medio técnico** que convierte una vulnerabilidad en un comportamiento no deseado. No es
solo "provocar un error": es **controlar las consecuencias del fallo de forma precisa y
predecible** para obtener una ventaja (RCE, escalada, fuga de información, DoS…).

El valor de un exploit no está solo en su impacto, sino en su **fiabilidad** y su
**portabilidad**: uno que funciona estable en muchas configuraciones vale mucho más que uno
que requiere condiciones muy específicas.

### Payload
La **carga útil** que determina qué acción concreta se ejecuta tras abrir la brecha. El
exploit abre la puerta; el payload es lo que entra por ella.

- Básico: una llamada al sistema, ejecución de comandos, una *reverse/bind shell*.
- Avanzado: *staged payloads*, evasión antiforense, persistencia, exfiltración.
- Restricciones de diseño: espacio disponible, *badchars*, políticas del sistema, sandboxing.

> **Relación entre los tres:** la vulnerabilidad es el *punto débil*, el exploit es la
> *técnica* que lo aprovecha, y el payload es *lo que se ejecuta* una vez dentro.

---

## Técnicas de descubrimiento y análisis

### Fuzzing
Proporcionar entradas masivas y mayoritariamente aleatorias a un programa para detectar
fallos. Si inyectas suficientes datos, tarde o temprano activas un comportamiento no previsto.

- **Black-box**: sin conocimiento interno.
- **Grey-box**: con cobertura de código para dirigir las entradas (lo más habitual hoy).
- **White-box**: con acceso al fuente para dirigir inputs a zonas críticas.

Los fuzzers modernos **instrumentan** el binario y usan **retroalimentación por cobertura**:
si una entrada alcanza una ruta nueva, la usan como semilla para mutar. La parte difícil no es
provocar el crash, es **triar** el crash (¿es explotable o solo un `null-deref`?).

### Ingeniería inversa (reversing)
Descomponer y analizar el comportamiento interno de un binario cuando no hay fuente.
Combino:

- **Análisis estático**: inspecciono el binario (funciones, strings, xrefs, flujo) con
  Ghidra/IDA/Cutter.
- **Análisis dinámico**: ejecuto bajo debugger y observo el comportamiento en tiempo real.

La combinación permite entender cómo reacciona el software a cada entrada, cómo gestiona la
memoria y qué validaciones aplica (o no).

### Diffing de binarios
Comparar dos versiones de un binario (normalmente vulnerable vs. parcheada) para localizar qué
cambió. Como el parche suele tocar justo la función vulnerable, el diff **señala la causa
raíz**. Herramientas: BinDiff, Diaphora. Es la base del *patch diffing* y del estudio de
1-days.

---

## Mitigaciones modernas (y por qué me importan)

Entender las protecciones sirve para dos cosas: saber **cómo ha evolucionado la seguridad** y
saber **qué tendré que sortear** en un laboratorio de explotación avanzada.

| Protección | Qué hace | Implicación para el analista |
|------------|----------|------------------------------|
| **ASLR** | Aleatoriza direcciones (stack, heap, librerías) | Obliga a *info-leaks*; baja entropía o binarios mal compilados la debilitan |
| **DEP / NX** | Marca memoria como no ejecutable | Mata el shellcode clásico en pila → empuja a **ROP** |
| **Stack Canaries** | Valor centinela antes del *return address* | Hay que *leakear*, brute-forcear (forks) o saltarlo según el layout |
| **CFG** | Restringe destinos de saltos indirectos | Dificulta ROP salvo usando destinos válidos o fallos de corrupción complejos |
| **SafeSEH** | Valida handlers SEH (x86) | Muy efectivo en 32 bits; irrelevante en x64 (SEH basado en metadatos fuera de pila) |
| **Secure Boot** | Firma la cadena de arranque (UEFI) | Barrera contra bootkits; eleva el umbral de persistencia a bajo nivel |
| **DSE** | Exige drivers firmados (kernel x64) | Empuja a técnicas como **BYOVD** |
| **PatchGuard** | Detecta modificación de estructuras del kernel | Hookear el kernel provoca BSOD; muro para rootkits |

> **Idea clave:** las mitigaciones rara vez *eliminan* la vulnerabilidad; **encarecen** la
> explotación. La explotación moderna es tanto detectar el fallo como entender cómo esquivar
> estas capas sin romper el sistema por el camino.

---

## Vulnerabilidad conocida (CVE) vs. desconocida (0day)

- **Conocida**: publicada y (normalmente) parcheada. Puedo apoyarme en CVE/NVD, write-ups y
  diffing del parche.
- **0day**: aún no divulgada ni parcheada. No hay atajos: dependo de fuzzing, reversing y
  razonamiento desde cero.

En ambos casos el trabajo del analista es el mismo: **identificar el fallo, entender su causa
raíz, determinar el impacto y, si procede, construir un PoC** que evidencie la explotabilidad.
