# 05 — CVEs reales estudiados y patrones aprendidos

La actividad pide "vulnerabilidades reales que **hayas investigado**". Este documento es una
**plantilla + ejemplos** para que la rellenes con los CVEs que de verdad hayas estudiado. Cada
ficha se centra en **causa raíz y lecciones**, no en armamento: es el enfoque de un write-up
defensivo/académico.

> ⚠️ **Verifica los datos.** No tengo acceso a internet; las fichas de ejemplo resumen lo que es
> conocimiento público general sobre estos CVEs, pero debes **contrastar cada dato** en NVD /
> advisories oficiales antes de entregarlo, y quedarte solo con los CVEs que realmente hayas
> trabajado.

---

## Plantilla de ficha

```markdown
### CVE-AAAA-NNNNN — <nombre/apodo>

- **Producto / versión afectada:** ...
- **Tipo de fallo (CWE):** ...
- **Vector / superficie:** (remoto/local, autenticado/no)
- **Causa raíz:** (qué operación concreta falla y por qué)
- **Impacto:** (RCE, LPE, DoS, info-leak…)
- **Cómo se descubrió / analizó:** (fuzzing, diffing del parche, auditoría…)
- **Mitigaciones implicadas:** (qué protecciones había que sortear, si aplica)
- **Qué aprendí / patrón reutilizable:** (lección que me llevo para otros análisis)
- **Mis observaciones propias:** (lo que TÚ sacaste al estudiarlo)
- **Fuentes:** (NVD, advisory, write-up — verificadas)
```

---

## Ejemplos orientativos (sustituye por los tuyos)

### CVE-2014-0160 — "Heartbleed"

- **Producto:** OpenSSL (extensión Heartbeat de TLS/DTLS), ramas 1.0.1 afectadas.
- **Tipo de fallo (CWE):** CWE-125, lectura fuera de límites (*out-of-bounds read*).
- **Vector:** remoto, no autenticado.
- **Causa raíz:** el servidor confiaba en un campo de longitud enviado por el cliente sin
  comprobar que coincidía con los datos realmente recibidos, devolviendo memoria adyacente del
  proceso.
- **Impacto:** fuga de memoria del servidor (claves, credenciales, datos sensibles). **Info-leak**,
  no ejecución de código.
- **Cómo se analizó:** auditoría del código y del manejo del campo de longitud en el heartbeat.
- **Qué aprendí:** un fallo de *lectura* sin control de tamaño puede ser catastrófico sin tocar
  el flujo de ejecución; y por qué un info-leak es tan valioso (también para derrotar ASLR en
  otros contextos).
- **Mis observaciones propias:** *TODO.*
- **Fuentes:** *TODO — verificar en NVD y advisory de OpenSSL.*

---

### CVE-2017-0144 — "EternalBlue" (MS17-010)

- **Producto:** implementación de **SMBv1** en Windows.
- **Tipo de fallo (CWE):** corrupción de memoria por cálculo/conversión de tamaño incorrecto en
  el parsing de SMB.
- **Vector:** remoto, no autenticado, a través de SMBv1.
- **Causa raíz (a alto nivel):** un desajuste en el tratamiento de ciertos paquetes SMB provoca
  una escritura fuera de los límites esperados en memoria del kernel.
- **Impacto:** RCE en kernel. Fue la base de la propagación de **WannaCry**.
- **Lección defensiva directa (conecta con el módulo):** *deshabilitar SMBv1* es el ejemplo
  canónico de bastionado por eliminación de funcionalidad heredada.
- **Qué aprendí:** el enorme coste de mantener protocolos legacy activos "por si acaso", y por
  qué el bastionado (cerrar lo innecesario) rompe cadenas de explotación enteras.
- **Mis observaciones propias:** *TODO.*
- **Fuentes:** *TODO — verificar MS17-010 y NVD.*

> Aquí me quedo **deliberadamente a nivel de causa raíz y lección defensiva**; no reconstruyo el
> exploit. El valor académico está en entender el patrón y cómo mitigarlo.

---

### CVE-2019-0708 — "BlueKeep"

- **Producto:** Servicios de Escritorio Remoto (RDP) en versiones antiguas de Windows.
- **Tipo de fallo (CWE):** CWE-416, **Use-After-Free**.
- **Vector:** remoto, no autenticado (preauth).
- **Causa raíz (a alto nivel):** gestión incorrecta de un canal virtual durante el
  establecimiento de la sesión deja una estructura utilizable después de liberarse.
- **Impacto:** potencial RCE preautenticación; considerado "wormable".
- **Qué aprendí:** cómo un UAF da al atacante la posibilidad de manipular estructuras internas,
  y por qué Microsoft lo trató con la máxima prioridad (parche incluso para SO fuera de soporte).
- **Mis observaciones propias:** *TODO.*
- **Fuentes:** *TODO — verificar advisory de Microsoft y NVD.*

---

## Patrones transversales que extraigo

Más allá de cada CVE concreto, estos son los **patrones** que reaparecen y que incorporo a mi
metodología:

1. **Confiar en longitudes controladas por el atacante** (Heartbleed, EternalBlue) → siempre
   validar tamaño/consistencia en el lado que recibe.
2. **Gestión de ciclo de vida de objetos** (BlueKeep / UAF) → los fallos de *liberación* son tan
   peligrosos como los de *escritura*.
3. **Funcionalidad legacy activa** (SMBv1) → cada protocolo/feature innecesario es superficie
   gratis para el atacante.
4. **Los bugs vienen en familias** → tras encontrar uno, merece la pena *variant analysis* en
   código hermano.

*TODO: añade los patrones que TÚ hayas identificado en tus propios análisis.*
