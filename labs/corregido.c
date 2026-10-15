/*
 * corregido.c  —  Versión CORREGIDA del programa vulnerable
 * ---------------------------------------------------------------------------
 * Se reemplaza strcpy() por una copia con verificación de tamaño, eliminando
 * la causa raíz del desbordamiento.
 *
 * Nota: strcpy_s() forma parte de las "Annex K bounds-checking interfaces".
 * En MinGW/MSVC está disponible; en otros toolchains puede no estarlo. Como
 * alternativa portable se incluye, comentada, una variante con snprintf().
 *
 * Compilación (32 bits):
 *   gcc -m32 -o corregido.exe corregido.c
 */

#include <stdio.h>
#include <string.h>

void vulnerable_function(char *input) {
    char buffer[1000];

    // Uso de función segura con verificación de tamaño del destino
    if (strcpy_s(buffer, sizeof(buffer), input) != 0) {
        printf("Error copiando los datos de entrada.\n");
        return;
    }

    /* Alternativa portable (descomentar si strcpy_s no está disponible):
     *
     * snprintf(buffer, sizeof(buffer), "%s", input);
     * buffer[sizeof(buffer) - 1] = '\0';
     */

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
