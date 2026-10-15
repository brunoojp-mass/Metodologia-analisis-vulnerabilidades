#!/usr/bin/env python3
"""
fuzzer.py  —  Fuzzer didáctico de cadenas crecientes
----------------------------------------------------
Lanza el binario de laboratorio con entradas cada vez más largas para localizar
el UMBRAL en el que el programa deja de comportarse con normalidad (primer crash).

USO EXCLUSIVO en laboratorio aislado y sobre binarios propios (labs/vulnerable.c).

Ejemplo:
    python3 fuzzer.py ./vulnerable          # Linux
    python3 fuzzer.py vulnerable.exe        # Windows

Es un ejemplo mínimo para *entender* la mecánica del fuzzing por fuerza de longitud.
Para trabajo serio se usan fuzzers con cobertura (AFL++, WinAFL) o estructurados
(boofuzz), como se explica en docs/04-flujo-0day.md.
"""

import subprocess
import sys


def run_once(binary: str, payload: str) -> int:
    """Ejecuta el binario con el payload y devuelve el código de retorno.

    Un retorno negativo (POSIX) o un código anómalo suele indicar que el proceso
    terminó por una señal (p. ej., SIGSEGV) -> candidato a crash.
    """
    try:
        proc = subprocess.run(
            [binary, payload],
            capture_output=True,
            timeout=5,
        )
        return proc.returncode
    except subprocess.TimeoutExpired:
        return 0  # colgado; lo tratamos aparte si hiciera falta


def looks_like_crash(returncode: int) -> bool:
    # En POSIX, terminación por señal -> returncode negativo.
    # En Windows, códigos como 0xC0000005 (access violation) indican crash.
    if returncode < 0:
        return True
    if returncode in (0xC0000005, 0xC00000FD):  # AV / stack overflow
        return True
    return False


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <binario>")
        sys.exit(1)

    binary = sys.argv[1]

    length = 100
    step = 100
    max_length = 3000

    print(f"[*] Fuzzing '{binary}' con cadenas de 'A' crecientes...\n")

    while length <= max_length:
        payload = "A" * length
        rc = run_once(binary, payload)

        if looks_like_crash(rc):
            print(f"[!] CRASH con {length} bytes (returncode={rc})")
            print(f"[!] Umbral de fallo localizado alrededor de {length} bytes.")
            print("[*] Siguiente paso: reproducir bajo debugger y calcular el offset")
            print("    (ver docs/03-caso-practico-stackbof.md).")
            return

        print(f"    {length:>5} bytes ... OK")
        length += step

    print("\n[*] No se detectó crash en el rango probado. "
          "Aumenta max_length o revisa el harness.")


if __name__ == "__main__":
    main()
