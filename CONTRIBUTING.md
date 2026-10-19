# Cómo colaborar

**Regla:** toda cifra debe tener una fuente verificable (URL pública y, si es posible, una consulta reproducible) y una fecha de consulta. No se aceptan estimaciones propias, interpolaciones ni índices compuestos opacos.

## Corregir un dato
1. Abre un *issue* con la etiqueta `corrección` e indica: el dato que aparece en la web, el dato correcto, la URL de la fuente y la fecha de consulta.
2. Si sabes cómo arreglarlo, envía un *pull request*. Si el dato es automático, corrige el script en `scripts/`; si es manual, `data/manual.json`.

## Proponer una fuente o un indicador nuevo
Abre un *issue* `nueva-fuente` con:
- organismo, URL, licencia de reutilización y si tiene API o descarga;
- definición exacta del indicador, cobertura temporal y frecuencia;
- cuadro al que pertenece (macro, promesas, calidad democrática, corrupción) y sus riesgos de sesgo.

## Pull requests
- Un cambio por PR. Comprueba que `bash scripts/update_all.sh` funciona en local.
- Los datos manuales llevan siempre `url` y una fecha.
- Distingue los hechos registrales (BOE, CGPJ, Eurostat), los índices de expertos y las valoraciones de terceros.
- Nada de datos personales de investigados no condenados más allá de lo publicado en resoluciones públicas.
