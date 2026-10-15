# Laboratorio

> ⚠️ **Solo en una VM aislada, sin red de producción, sobre estos binarios propios.**

Material para reproducir el caso práctico de [`../docs/03-caso-practico-stackbof.md`](../docs/03-caso-practico-stackbof.md).

## Contenido

| Archivo | Descripción |
|---------|-------------|
| `vulnerable.c` | Programa con Stack Buffer Overflow (`strcpy` sin control) |
| `corregido.c` | Versión segura (`strcpy_s` / `snprintf`) |
| `fuzzer.py` | Fuzzer didáctico de cadenas crecientes |

## Compilación

**Windows (MinGW):**
```bat
cd C:\MinGW\bin
:: 32 bits, pila ejecutable, sin stack cookies
gcc -m32 -fno-stack-protector -z execstack -o vulnerable.exe vulnerable.c
:: 32 bits, versión corregida
gcc -m32 -o corregido.exe corregido.c
```

**Linux:**
```bash
sudo apt install gcc-multilib        # soporte 32 bits
gcc -m32 -fno-stack-protector -z execstack -no-pie -o vulnerable vulnerable.c
gcc -m32 -o corregido corregido.c
```

## Reproducción rápida

```bash
# 1) Comportamiento normal
./vulnerable "hola"

# 2) Buscar el umbral de fallo con el fuzzer
python3 fuzzer.py ./vulnerable

# 3) Reproducir el crash bajo debugger y calcular el offset
#    (x32dbg en Windows, gdb+GEF en Linux) -> ver docs/03
```

## Verificar protecciones

```bash
# Linux
checksec --file=./vulnerable
readelf -l ./vulnerable | grep -i stack
```

## Trabajo futuro (siguiente etapa del portfolio)

- Recompilar a **64 bits** (`RIP` en vez de `EIP`, argumentos por registros).
- Activar **ASLR / DEP / stack canaries** una por una y documentar cómo cada una rompe la
  explotación y qué técnica de bypass exigiría (info-leak, ROP, etc.).
