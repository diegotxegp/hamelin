# HAMELIN — Cuestionario del participante

*(Imprimir solo las partes 1–4. La parte "Notas para el equipo investigador" no se entrega.)*

---

## 1. Datos

- **Nombre y apellidos:** ______________________________
- **Herramienta utilizada:** ______________________________
- **Orden de uso** (1ª, 2ª… herramienta que pruebas hoy): ____

---

## 2. Registro por dataset

Vas a probar Hamelin con los datasets que te indiquen, **empezando por el que te ha tocado** y siguiendo en orden. Haz **tantos como quieras**. Para cada uno, **anota la hora del reloj del proyector** (24 h, con segundos, p. ej. 10:14:32) en cada momento y rellena una fila.

| Momento | Qué anotar |
|---|---|
| **H1** | Hora a la que **empiezas** el dataset (lo cargas en la herramienta) |
| **H2** | Hora a la que pulsas **Train** por primera vez |
| **H3** | Hora a la que **aparecen los resultados** |
| **H4** | Hora a la que pulsas **Train** de nuevo (si vuelves a entrenar) |
| **H5** | Hora a la que aparecen los resultados del segundo entrenamiento |

| Nº | Dataset | H1 | H2 | H3 | H4 | H5 | ¿Lo terminé? (Sí / No) | Resultados que obtuve | Problemas o errores que me encontré o cometí (y cuánto me afectaron: **bajo** = no cambió el resultado, **medio** = repetí un paso, **alto** = no pude seguir sin ayuda) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | : | : | : | : | : | | | |
| 2 | | : | : | : | : | : | | | |
| 3 | | : | : | : | : | : | | | |
| 4 | | : | : | : | : | : | | | |
| 5 | | : | : | : | : | : | | | |
| 6 | | : | : | : | : | : | | | |

---

## 3. Tu opinión sobre la herramienta

Marca de **1** (totalmente en desacuerdo) a **5** (totalmente de acuerdo).

| | Afirmación | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| 1 | Me ha resultado fácil de usar. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | Me ha parecido más complicada de lo necesario. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3 | En todo momento sabía qué estaba ocurriendo. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4 | Sentí que era yo quien llevaba el mando. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5 | Entendí lo que me mostraba. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6 | Me fío de lo que me ha devuelto. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 7 | Cuando algo salió mal, supe cómo seguir. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 8 | Estuve tranquilo/a con lo que ocurre con mis datos. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 9 | Sabría explicar a otra persona cómo llegué a mis resultados. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 10 | Me ha ayudado a comprender mejor los datos. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 11 | Usarla me ha costado poco esfuerzo. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 12 | Pude dejar que trabajara sola sin vigilarla de cerca. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 13 | En general, estoy satisfecho/a. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 14 | La volvería a usar. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 15 | Tuve información suficiente para decidir si usaría lo que obtuve en un caso real. | ☐ | ☐ | ☐ | ☐ | ☐ |

---

## 4. Para terminar

- **¿Qué es lo que mejor ha funcionado?** ______________________________
- **¿Qué es lo que peor, o qué cambiarías primero?** ______________________________

**¡Gracias!**

---
---

# Notas para el equipo investigador (no entregar)

## Asignación de datasets (rotación en cascada)

Los 14 datasets se numeran en el orden de la tabla. El participante *k* empieza en el dataset ((*k* − 1) mod 14) + 1 y continúa en orden cíclico (…, 13, 14, 1, 2, …). Así, con 14 participantes o más, cada dataset se prueba en primera posición el mismo número de veces y todos quedan cubiertos aunque cada persona haga pocos.

| Nº | Carpeta | Dataset | Filas × cols | Resultado (última columna) |
|---|---|---|---|---|
| 1 | Binary | blood-transfusion-service-center | 748 × 5 | binario |
| 2 | Binary | breast-w | 699 × 10 | binario |
| 3 | Binary | credit-g | 1000 × 21 | binario |
| 4 | Binary | diabetes | 768 × 9 | binario |
| 5 | Binary | qsar-biodeg | 1055 × 42 | binario |
| 6 | Classification | analcatdata_dmft | 797 × 5 | 5 clases |
| 7 | Classification | cmc | 1473 × 10 | 3 clases |
| 8 | Classification | hypothyroid | 3772 × 30 | 4 clases |
| 9 | Classification | mfeat-morphological | 2000 × 7 | 10 clases |
| 10 | Classification | vehicle | 846 × 19 | 4 clases |
| 11 | Regression | cholesterol | 303 × 14 | continuo |
| 12 | Regression | cloud | 108 × 6 | continuo |
| 13 | Regression | liver-disorders | 345 × 6 | continuo (ordinal 16 valores) |
| 14 | Regression | plasma_retinol | 315 × 14 | continuo |

Los datos están en `workspace/data/`. Antes del estudio, archivar o vaciar `workspace/logs/usage_log.csv` (o anotar el `session_id` de cada participante).

## Medidas para el artículo (revisor: *"Add a study with real users, reporting completion, errors, time and satisfaction"*)

| Medida | Fuente |
|---|---|
| **Finalización** | Columna "¿Lo terminé?" (% de datasets terminados sobre los intentados, por participante y tipo de dataset) |
| **Resultados** | Columna "Resultados que obtuve" (métrica anotada por el participante; comparar con los modelos guardados en el proyecto) |
| **Tiempo** | Tramo 1 (configuración) = H2 − H1; entrenamiento = H3 − H2; tramo 2 (revisión hasta reentrenar) = H4 − H3; reentrenamiento = H5 − H4. Contrastar con `usage_log.csv` |
| **Errores** | Columna "Problemas o errores" (recuento, categorías y gravedad bajo/medio/alto, para ponderar) + avisos/errores automáticos (`warning_shown` / `error_shown`) |
| **Satisfacción** | Ítems 13–14 y respuestas abiertas |
| **Usabilidad y principios HCAI** | Ítems 1–12 (ver correspondencia) |

Resumen automático de la aplicación:

```bash
python tools/usage_summary.py workspace/logs/usage_log.csv --out resumen_sesiones.csv
```

## Correspondencia de los ítems (el participante no la ve)

Los ítems 1 y 2 se inspiran en el SUS (Brooke, 1996) y el resto en el marco HCAI de Shneiderman (alta automatización y alto control humano). Son una adaptación *ad hoc*, no una escala validada: declararlo como limitación.

| Ítems | Dimensión |
|---|---|
| 1, 2 | Usabilidad (SUS abreviado) |
| 4 | Control humano |
| 12 | Automatización fiable (eje independiente del control: **no promediar** con el ítem 4) |
| 3 | Transparencia |
| 5 | Explicabilidad |
| 7 | Fiabilidad y seguridad (gestión de errores) |
| 6 | Confianza calibrada |
| 8 | Privacidad |
| 9 | Trazabilidad y responsabilidad |
| 10 | Empoderamiento |
| 11 | Bienestar (carga cognitiva) |
| 13, 14 | Satisfacción |
| 15 | Confianza informada / disposición de uso real |

Si se compara con otras herramientas, registrar junto a cada cuestionario el orden de uso (A-B o B-A) para permitir análisis pareados (Wilcoxon). El reloj del proyector debe mostrar segundos y conviene recordar a los participantes que lo miren al empezar y terminar.

Puntuación: invertir el ítem 2 (6 − valor). Media por dimensión y global; cumple ≥ 4, parcial entre 3 y 4, no cumple < 3. Para los tiempos, mediana y rango intercuartílico por tipo de dataset (binario / multiclase / regresión) y tramo.

**Referencias:** Brooke, J. (1996). *SUS: a quick and dirty usability scale*. Shneiderman, B. (2020). *Human-Centered Artificial Intelligence: Reliable, Safe & Trustworthy*. Int. J. Human–Computer Interaction. Shneiderman, B. (2022). *Human-Centered AI*. Oxford University Press.
