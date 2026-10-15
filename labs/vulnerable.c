/*
 * vulnerable.c  —  Programa DELIBERADAMENTE vulnerable (Stack Buffer Overflow)
 * ---------------------------------------------------------------------------
 * USO EXCLUSIVO EN LABORATORIO AISLADO Y CON FINES EDUCATIVOS.
 *
 * Compilación (32 bits, sin stack canaries, pila ejecutable):
 *   Windows (MinGW):
 *     gcc -m32 -fno-stack-protector -z execstack -o vulnerable.exe vulnerable.c
 *   Linux:
 *     gcc -m32 -fno-stack-protector -z execstack -no-pie -o vulnerable vulnerable.c
 */

#include <stdio.h>
#include <string.h>

void vulnerable_function(char *input) {
    char buffer[1000];
    strcpy(buffer, input);   // No hay verificación de tamaño -> Stack BOF
    printf("Has introducido: %s\n", buffer);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Uso: %s <input>\n", argv[0]);
        return 1;
    }
    vulnerable_function(argv[1]);
    printf("Programa finalizado correctamente.\n");
    return 0;
}
