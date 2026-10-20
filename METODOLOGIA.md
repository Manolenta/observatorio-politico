# Metodología del Observatorio de calidad política (España)

Versión 0.1 · 19-10-2026 · Prototipo

## 0. Principios

1. **Primero el dato bruto y su fuente.** Cada cifra lleva la fuente original con enlace, la consulta exacta (URL de API o búsqueda) y la fecha de extracción. Quien quiera puede repetir la consulta y obtener lo mismo.
2. **Sin índice compuesto propio.** No hay ponderaciones ni una nota final del gobierno. Si en el futuro se muestra alguna agregación, debe ser opcional, con los pesos visibles y modificables por el usuario y con el dato bruto al lado.
3. **Hechos separados de valoraciones.** Etiquetas:
   - *Hecho registral*: BOE, CGPJ, Eurostat.
   - *Índice de expertos o de percepción*: V-Dem, Freedom House, TI-CPI, WGI, EIU.
   - *Valoración de terceros*: verificadores como Newtral.
   No se mezclan en un mismo gráfico.
4. **Huecos visibles.** Lo que no se ha podido obtener aparece como `pendiente`, nunca estimado ni interpolado.
5. **Mismos criterios para todos los gobiernos.** Mismas consultas y mismas reglas de asignación temporal para todas las legislaturas desde 1977.
6. **Comparación internacional.** Siempre que haya datos: España frente a UE-27, zona euro, Alemania, Francia, Italia y Portugal.

## 1. Cuadro 1: datos macroeconómicos

| Indicador | Definición | Fuente / conjunto de datos | API | Frecuencia | Desde |
|---|---|---|---|---|---|
| Crecimiento real del PIB | % de variación anual del PIB en volumen | Eurostat `tec00115` | Sí (JSON-stat, sin clave) | Anual (y trimestral) | 2014 en este conjunto; FMI desde 1980 |
| PIB per cápita en PPA | Índice de volumen, UE27=100 | Eurostat `tec00114` | Sí | Anual | 2014 (otros conjuntos llegan a 1995) |
| PIB per cápita PPA | $ internacionales constantes de 2021 | Banco Mundial `NY.GDP.PCAP.PP.KD` | Sí (API v2) | Anual | 1990 |
| Tasa de paro | % de población activa, 15-74 años | Eurostat `une_rt_a` (EPA armonizada) | Sí | Anual (mensual en `une_rt_m`) | 2009 aquí (FMI `LUR` desde 1980) |
| Paro juvenil | 15-24 años | Eurostat `une_rt_a` | Sí | Anual | 2009 |
| Deuda pública | % del PIB según el Protocolo de Déficit Excesivo | Eurostat `gov_10dd_edpt1` (GD, S13) | Sí | Anual (notificaciones de abril y octubre) | 1995 (FMI `GGXWDG_NGDP` desde 1980) |
| Déficit / superávit | B9, % del PIB | Eurostat `gov_10dd_edpt1` (B9) | Sí | Anual | 1995 (FMI `GGXCNL_NGDP`) |
| Inflación | IPCA, tasa media anual | Eurostat `prc_hicp_aind` (CP00, RCH_A_AVG) | Sí | Anual (mensual en `prc_hicp_manr`) | 1996 (FMI `PCPIPCH` desde 1980) |
| Productividad | PIB por hora trabajada en PPS, UE27=100 | Eurostat `tesem160` (NLPR_HW) | Sí | Anual | 2005 |
| Series largas | Paro, deuda, saldo, PIB, IPC | FMI World Economic Outlook (DataMapper API) | Sí | Semestral (abril y octubre) | 1980 |

Enlaces:
- Eurostat: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/
- Banco Mundial: https://api.worldbank.org/v2/
- FMI: https://www.imf.org/external/datamapper/api/v1/

**Pendientes / ampliaciones:**
- OCDE (SDMX, https://sdmx.oecd.org/public/rest/): productividad multifactorial y salario real.
- INE (API JSON Tempus3, https://servicios.ine.es/wstempus/js/): EPA trimestral, IPC mensual y AROPE.
- BCE Data Portal (https://data-api.ecb.europa.eu/): prima de riesgo y tipos.

Hay que verificar estas tres con sus API antes de integrarlas.

**Comparar entre legislaturas:**
- Para cada legislatura se muestra el valor en el año de inicio y en el del final, y su diferencia frente a la UE-27 en esos mismos años. La diferencia relativa con la UE neutraliza buena parte del ciclo común.
- Las series se marcan con líneas verticales en el inicio de cada legislatura. Esto es una referencia temporal, no una atribución.

**Riesgos de sesgo:**
- *Atribución causal.* El paro, la deuda o la inflación dependen del ciclo global, de la política monetaria del BCE (desde 1999), de shocks como la COVID o la energía y de inercias de gobiernos anteriores. La web dice explícitamente que no atribuye.
- *Elección del año base.* Usar siempre año de inicio y año de fin completos, sin escoger el más favorable.
- *Revisiones.* Eurostat y el FMI revisan sus series. Se guarda la fecha de actualización en origen (campo `actualizado_fuente`). Conviene archivar cada extracción (git) para poder reconstruir lo que se publicó.
- *Proyecciones.* El WEO incluye estimaciones y proyecciones. En la web aparecen con trazo discontinuo para los años ≥ año actual.
- *Rupturas de serie.* EPA 2005, SEC 2010 y cambios de base del IPC. Hay que documentarlas en cada gráfico cuando se amplíe.

## 2. Cuadro 2: cumplimiento de promesas

**Indicadores:**
- (a) Recuento de Newtral PactoCheck: 50 compromisos de los pactos de gobierno e investidura de 2023, clasificados en cumplida, en progreso, pendiente o incumplida.
- (b) Tabla curada de promesas clave con estado y evidencia documental, preferentemente del BOE.
- (c) Futuro: cruce programa ↔ votaciones, como hace El Congreso en tu mano (https://elcongresoentumano.es/programas).

**Fuentes:**
- https://pactocheck.newtral.es/ (metodología: https://www.newtral.es/pactocheck-metodologia/)
- Programas electorales en PDF de cada partido
- Acuerdos de investidura
- BOE
- Autoevaluación del Gobierno «Cumpliendo» (https://www.lamoncloa.gob.es/paginas/cumpliendo/index.aspx), etiquetada como *autoevaluación* y nunca usada como fuente única

**API:** no hay. Hay que recopilar a mano en `data/manual.json`, una vez al mes o cuando el verificador actualice.

**Reglas:**
- «Cumplida» = norma publicada en el BOE, o medida ejecutada y verificable.
- «Parcial» = existe la norma, pero con un alcance menor que el prometido.
- «En trámite» = iniciativa viva en las Cortes o en el Consejo de Ministros.
- «Incumplida» = descartada, plazo vencido o iniciativa decaída al disolverse las Cortes.
- Cada estado lleva su enlace.

**Comparar entre legislaturas:** solo con una misma metodología. Hay que aplicar el mismo criterio de selección de promesas, por ejemplo las N promesas concretas y medibles del programa ganador y de los pactos, a cada legislatura. No hay series comparables antes de 2019; hay que construirlas.

**Riesgos de sesgo:**
- La selección de qué promesas se miden: publicar la lista completa y el criterio de selección.
- Las promesas vagas («impulsar», «fomentar»): se excluyen, como hace Newtral.
- Un gobierno en minoría no puede cumplir lo que el Congreso rechaza. Hay que separar *no presentado* de *presentado y rechazado*.
- El estado de una promesa cambia con el tiempo: guardar el histórico con fecha.
- La oposición (PP, Vox) no gobierna a nivel estatal. Su cumplimiento se mide en los gobiernos autonómicos con una metodología aparte, sin mezclarlo en el mismo gráfico.

## 3. Cuadro 3: calidad democrática

### 3.1 Producción normativa: leyes frente a reales decretos-leyes (dato propio a partir del BOE)

**Definiciones:**
- Normas de la *Jefatura del Estado* publicadas en la Sección I del BOE cuyo título empieza por «Ley», «Ley Orgánica» o «Real Decreto-ley» con número N/AAAA.
- Cada norma se asigna a la legislatura según su **fecha de disposición**.
- Cada legislatura va desde su sesión constitutiva del Congreso hasta la siguiente. Incluye el periodo tras la disolución, porque se sancionan leyes ya aprobadas y la Diputación Permanente convalida RDL.

**Indicadores:**
- Número de leyes ordinarias, leyes orgánicas y RDL.
- RDL por año y leyes por año, para normalizar por la duración de la legislatura.
- Ratio RDL / (leyes + leyes orgánicas).
- RDL derogados, es decir, no convalidados por el Congreso. Se cuentan los «Acuerdo de derogación» publicados en el BOE.
- RDL convalidados (acuerdos de convalidación publicados).

**Fuentes:**
- Buscador oficial del BOE (https://www.boe.es/buscar/boe.php), consulta por título y año (Sección I).
- Complemento con la API de legislación consolidada (https://www.boe.es/datosabiertos/api/legislacion-consolidada).
- Script `scripts/fetch_boe.py`. Las URL de cada consulta quedan en `data/boe_normas.json` (campo `consultas`) y cada norma con su referencia BOE.

**Control de calidad:**
- Se comprueba que la numeración anual sea continua (1..N). Quedan 35 números sin localizar de unas 2.850 normas (alrededor del 1,2%). 30 son de 1977-1985 (algunos de 1977 son anteriores a julio y quedan fuera del periodo), 4 de 2001 y 1 de 2004 (RDL 6/2004). Probablemente se deben a títulos con formato atípico o a erratas en la fuente. Ninguno es de la XII Legislatura ni posterior. Se listan al ejecutar la validación.
- Contraste con prensa (ABC, 15-10-2026):
  - XII Legislatura: ABC cuenta 39 leyes y 63 RDL convalidados; aquí salen 39 y 63. **Coincide.**
  - XV Legislatura: ABC cuenta 43 RDL convalidados; aquí salen 43. **Coincide.** ABC cuenta 37 leyes; aquí salen 34 (21 + 13 orgánicas). La diferencia está por explicar; puede deberse al criterio de recuento.
- Los acuerdos de convalidación solo tienen un título homogéneo desde mediados de los años 2000, así que la columna «convalidados» no es fiable antes de esa época. Los «derogados» sí parecen completos (RDL 1/2006, 4/2017, 21/2018, 27/2020, 7/2023…), pero conviene contrastarlos con el Congreso.

**Frecuencia:** diaria (BOE). Se puede ejecutar una vez por semana.

**Riesgos de sesgo:**
- Los RDL están justificados en crisis como la COVID (2020-2021) o la DANA. Hay que mostrar el contexto, no solo el número.
- Las legislaturas cortas o en funciones (XI, XIII) distorsionan las medias: normalizar por año y señalarlas.
- Una ley no equivale a otra (una ley ómnibus frente a una de artículo único). Ampliación posible: número de artículos o palabras.
- Los RDL que se tramitan después como proyecto de ley pueden acabar contando dos veces. Ampliación: marcar los RDL «tramitados como proyecto de ley».

### 3.2 Indultos

- **Definición:** reales decretos publicados en la Sección III del BOE con «se indulta» en el título, por año de publicación.
- **Fuente:** buscador oficial del BOE (mismo script).
- **Contraste:** El Indultómetro de Civio (https://civio.es/el-indultometro/).
- **Riesgos:**
  - Desde 2012-2013 bajan mucho por un cambio de criterio y de demanda, no solo por el gobierno.
  - Un indulto parcial y uno total no son comparables.
  - Algunos RD pueden afectar a más de una persona.
  - Se recomienda añadir el tipo de delito (Civio lo clasifica).

### 3.3 Amnistías

Es un hecho registral: Ley 46/1977 y Ley Orgánica 1/2024 (BOE-A-2024-11776). Se muestra como hecho, sin puntuación.

### 3.4 Índices internacionales (de expertos o de percepción)

| Índice | Escala | Fuente | Descarga automática | Frecuencia |
|---|---|---|---|---|
| V-Dem: democracia electoral y liberal, estado de derecho, control judicial | 0-1 | https://v-dem.net (vía Our World in Data CSV) | Sí (CSV de OWID; o el conjunto completo de V-Dem) | Anual (marzo) |
| Freedom House: derechos políticos (0-40) y libertades civiles (0-60) | puntos | https://freedomhouse.org (vía OWID) | Sí | Anual |
| Banco Mundial WGI: voz y rendición de cuentas, estado de derecho, eficacia del gobierno | -2,5 a 2,5 | API del Banco Mundial `GOV_WGI_*` | Sí | Anual |
| EIU Democracy Index | 0-10 | EIU | **No**: licencia no redistribuible (OWID devuelve 403) | Anual (`pendiente`, transcribir del informe) |
| WJP Rule of Law Index | 0-1 | https://worldjusticeproject.org | Excel anual (`pendiente`) | Anual |
| Informe sobre el Estado de Derecho de la Comisión Europea | cualitativo | Comisión Europea | No | Anual (julio). Codificar las recomendaciones y su seguimiento |
| Consejo de Transparencia y Buen Gobierno | reclamaciones, resoluciones incumplidas | https://www.consejodetransparencia.es | Memorias en PDF (`pendiente`) | Anual |

**Riesgos de sesgo:**
- Son percepciones de expertos con metodologías propias y cambiantes: se muestran sin reescalar ni combinar.
- Hay desfase temporal: el índice de un año refleja en parte el anterior.
- Usar índices que dependen unos de otros como si fueran independientes. Por ejemplo, el TI-CPI incorpora V-Dem y WJP.

### 3.5 Indicadores institucionales (dato propio a partir del BOE y del Congreso; `scripts/fetch_institucional.py`)

- **Días de Gobierno en funciones tras unas elecciones.** Se cuentan desde la jornada electoral hasta el real decreto de nombramiento del Presidente del Gobierno. La fecha de las elecciones sale del texto de cada RD de disolución. Los RD de 1979, 1982 y 1986 solo existen en PDF en el BOE: se leyeron con `pdftotext` y quedan guardados en caché, con su referencia BOE, en `data/institucional.json`. Cuando se repiten elecciones sin investidura (2015-2016 y 2019) se cuenta un solo periodo. No se incluyen la etapa en funciones de 1981 (dimisión) ni la de 2018 (moción de censura). Las elecciones de 1977 no tienen RD de disolución y quedan fuera.
- **Años con Presupuestos prorrogados.** Un año sin «Ley N/AAAA … de Presupuestos Generales del Estado para AAAA» publicada en el BOE cuenta como «prorrogados todo el año» (art. 134.4 CE). Si la ley se publicó después del 1 de enero, el año cuenta como «prórroga parcial».
- **Retraso en la renovación del CGPJ.** Se compara cada renovación completa (dos RD el mismo día, uno a propuesta del Congreso y otro del Senado) con la anterior más 5 años. Es una aproximación con la fecha del RD (±10 días respecto a la constitución del Consejo). Se excluyen los nombramientos parciales de 1989 y 1994, que fueron sustituciones.
- **RDL tramitados como proyecto de ley.** Para la XV Legislatura se usan los datos abiertos del Congreso: proyectos de ley «procedente del Real Decreto-ley». Para las legislaturas anteriores el dato está **pendiente**: el Congreso solo publica en abierto la legislatura en curso, y los acuerdos de convalidación del BOE no dicen si se acordó tramitarlos como proyecto.
- **Retraso en la renovación del Tribunal Constitucional.** **Pendiente.** El TC se renueva por tercios, con cuatro órganos proponentes y con sustituciones por vacante. Para calcular el retraso habría que asignar cada nombramiento del BOE a su tercio, y eso solo puede hacerse leyendo cada RD a mano.

### 3.6 Validación y registro de cambios

Antes de publicar, `scripts/validate.py` comprueba lo siguiente:
- que no aparezcan huecos nuevos en la numeración del BOE (hay 35 conocidos y revisados);
- que no haya saltos anómalos (×4 o más) entre años completos del CGPJ;
- que todo dato manual tenga URL y fecha;
- que los enlaces respondan. Un enlace roto solo genera un aviso.

Si hay errores, el workflow no publica y abre un issue. `scripts/changelog.py` anota en `data/changelog.json` y en `CHANGELOG.md` las cifras clave que cambian en cada actualización.

## 4. Cuadro 4: corrupción

| Indicador | Definición | Fuente | API | Frecuencia |
|---|---|---|---|---|
| Personas procesadas o con juicio oral por corrupción pública | Auto de procesamiento o de apertura de juicio oral | CGPJ, Repositorio de datos sobre procesos por corrupción (resumen nacional) | No (HTML por trimestre; extracción por script `fetch_cgpj.py`) | Trimestral (desde el 2.º semestre de 2015) |
| Sentencias condenatorias (con o sin conformidad, parciales), absolutorias, «otras causas» | Forma de terminación | Ídem | Ídem | Trimestral |
| TI Índice de Percepción de la Corrupción | 0-100 | Transparency International (OWID; 2025 transcrito de TI España) | CSV | Anual (febrero) |
| WGI control de la corrupción | -2,5 a 2,5 | Banco Mundial | Sí | Anual |
| V-Dem corrupción política | 0-1 (más = peor) | V-Dem (OWID) | Sí | Anual |
| GRECO | Recomendaciones cumplidas, parciales o no cumplidas | Consejo de Europa (https://www.coe.int/es/web/greco/evaluations/spain) | No (PDF) | Por ronda (`pendiente`) |
| Eurobarómetro especial de corrupción | % que cree que la corrupción está extendida | Comisión Europea | Microdatos GESIS (`pendiente`) | Cada 1-2 años |
| Causas archivadas, prescritas o anuladas por defectos de forma o plazos | Fin del proceso sin sentencia sobre el fondo | **No hay estadística oficial que lo desglose** | No | `pendiente` |

**Validación CGPJ:** la suma de 2025 da 114 personas físicas, 13 jurídicas, 25 procedimientos, 52 sentencias condenatorias y 19 absolutorias. Coincide con la nota de prensa del CGPJ del 6-4-2026.

**Propuesta para las causas sin sentencia firme:** construir una base de casos propia y abierta:
- Una fila por causa: tribunal, partido o cargo, fechas de instrucción, juicio y sentencia; desenlace (condena, absolución, archivo, prescripción, nulidad por defectos procesales, por ejemplo prueba anulada o plazo de instrucción); fuente documental (sentencia del CENDOJ, https://www.poderjudicial.es/search/, más nota de prensa).
- Revisión por dos personas con criterios publicados.
- Sin nombres de investigados no condenados más allá de lo publicado en resoluciones públicas (presunción de inocencia y RGPD).
- Para atribuir por partido, solo casos con sentencia firme y cargo ejercido en el momento de los hechos.

**Riesgos de sesgo:**
- Un número mayor de procesados puede significar más corrupción o más eficacia judicial. Hay que leerlo junto a los índices de percepción.
- El tiempo judicial es largo: los hechos suelen ser de 5 a 15 años antes. No se debe atribuir al gobierno del año de la sentencia.
- Mezclar corrupción local, autonómica y estatal: desglosar por ámbito si el dato lo permite.
- Sesgo mediático en la recopilación manual de casos.

## 5. Comparación entre legislaturas: reglas generales

- Unidad: legislatura (de una sesión constitutiva a la siguiente) y, cuando aplique, presidente del Gobierno. La XII Legislatura tiene dos gobiernos (moción de censura del 1-6-2018).
- Normalizar por la duración (por año), indicar las legislaturas en funciones y no comparar legislaturas de menos de un año.
- Mostrar siempre el valor de España frente a la UE o a sus vecinos en los mismos años.
- Datos desde 1977 donde existen (BOE, FMI desde 1980). Si una serie empieza más tarde, se dice.

## 6. Cómo se evitan los índices compuestos opacos

- Cada tarjeta muestra la serie bruta, la fuente original, el enlace a la consulta exacta y la fecha de extracción.
- Todos los datos están en `data/*.json` y se regeneran con scripts públicos (`scripts/`). El historial de git hace de hemeroteca.
- Si se ofrece algún resumen, debe ser un panel opcional donde el usuario elige los indicadores y los pesos, con el cálculo visible.
- Hay que distinguir visualmente hechos registrales, índices de expertos y valoraciones de terceros.
- Política de correcciones: un formulario o issue público y un registro de cambios con fecha.

## 7. Publicación gratuita y actualización automática (propuesta, no ejecutada)

1. **GitHub Pages + GitHub Actions** (recomendada):
   - Repositorio público con `site/`, `scripts/` y `data/`.
   - Un workflow programado (`cron: "17 7 * * *"` con `timezone: "Europe/Madrid"`, es decir, a diario a las 07:17 hora de Madrid en verano y en invierno) ejecuta `scripts/update_all.sh`, hace commit de `data/` (historial auditable) y despliega `site/` en Pages.
   - Workflow en `.github/workflows/actualizar.yml`.
   - Coste: 0 € (repositorios públicos: Actions gratis).
2. **Cloudflare Pages o Netlify:** conectados al mismo repositorio. La compilación la hace GitHub Actions y estos solo sirven el sitio estático. Ofrecen CDN y dominio propio gratis.
3. **GitLab Pages + CI programada:** alternativa equivalente.
4. **Dominio:** opcional, unos 10 €/año. Por ejemplo, un `.es` apuntado a Pages.
5. **Robustez:**
   - Si una fuente falla, el script conserva el dato anterior y lo marca con un aviso.
   - Se recomienda que la Action abra un issue automático cuando falle una fuente o cuando la validación de numeración del BOE detecte huecos nuevos.
   - Hay que identificarse con un User-Agent y respetar los límites de cada servidor (BOE, CGPJ).
6. **Licencias:**
   - Eurostat, Banco Mundial y FMI permiten reutilizar con cita.
   - BOE: reutilización libre (Ley 37/2007).
   - OWID: CC-BY.
   - EIU: **no redistribuible**.
   - Newtral: enlazar y citar, no copiar su base completa.
