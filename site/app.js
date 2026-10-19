const O = window.OBS || {};
const fmt = (v, d = 1) => v == null || isNaN(v) ? '—' : Number(v).toLocaleString('es-ES', {maximumFractionDigits: d, minimumFractionDigits: 0});
const fecha = s => s ? new Date(s).toLocaleString('es-ES', {dateStyle: 'medium', timeStyle: 'short'}) + ' (hora de Madrid)' : 'pendiente';
const link = (u, t) => u ? `<a href="${u}" target="_blank" rel="noopener">${t || u}</a>` : '<span class="pend">pendiente</span>';
const COLORS = {ES: '#c62828', ESP: '#c62828', Spain: '#c62828', EU27_2020: '#14213d', EUU: '#14213d', EA20: '#5c6bc0', DE: '#888', DEU: '#888', Germany: '#888', FR: '#4a90d9', FRA: '#4a90d9', France: '#4a90d9', IT: '#2e7d32', ITA: '#2e7d32', Italy: '#2e7d32', PT: '#f9a825', PRT: '#f9a825', Portugal: '#f9a825'};
const NOMBRES = {ES: 'España', ESP: 'España', Spain: 'España', EU27_2020: 'UE-27', EUU: 'UE', EA20: 'Zona euro', DE: 'Alemania', DEU: 'Alemania', Germany: 'Alemania', FR: 'Francia', FRA: 'Francia', France: 'Francia', IT: 'Italia', ITA: 'Italia', Italy: 'Italia', PT: 'Portugal', PRT: 'Portugal', Portugal: 'Portugal'};
const LEG = [['C', 1977], ['I', 1979], ['II', 1982], ['III', 1986], ['IV', 1989], ['V', 1993], ['VI', 1996], ['VII', 2000], ['VIII', 2004], ['IX', 2008], ['X', 2011], ['XII', 2016], ['XIV', 2019], ['XV', 2023]];
const YEAR = new Date().getFullYear();
const legPlugin = {id: 'leg', afterDatasetsDraw(c) {
  const x = c.scales.x, a = c.chartArea, ctx = c.ctx; if (!x || !c.config.options.plugins.legLines) return;
  ctx.save(); ctx.strokeStyle = 'rgba(0,0,0,.15)'; ctx.fillStyle = '#999'; ctx.font = '9px sans-serif';
  LEG.forEach(([n, y]) => { const i = c.data.labels.indexOf(String(y)); if (i < 0) return; const px = x.getPixelForValue(i);
    ctx.beginPath(); ctx.moveTo(px, a.top); ctx.lineTo(px, a.bottom); ctx.stroke(); ctx.fillText(n, px + 2, a.top + 9); });
  ctx.restore(); }};
Chart.register(legPlugin);

function lineChart(canvas, series, keys, opts = {}) {
  const years = [...new Set(keys.flatMap(k => Object.keys(series[k] || {})))].filter(y => /^\d{4}$/.test(y)).sort();
  const ys = years.filter(y => (!opts.maxYear || +y <= opts.maxYear) && (!opts.minYear || +y >= opts.minYear));
  const ds = keys.filter(k => series[k]).map(k => ({label: NOMBRES[k] || k, data: ys.map(y => series[k][y] ?? null),
    borderColor: COLORS[k] || '#999', backgroundColor: COLORS[k] || '#999', borderWidth: k.startsWith('ES') || k === 'Spain' ? 2.6 : 1.4, pointRadius: 0, spanGaps: true,
    segment: opts.projFrom ? {borderDash: ctx => +ys[ctx.p1DataIndex] >= opts.projFrom ? [4, 4] : undefined} : undefined}));
  return new Chart(canvas, {type: 'line', data: {labels: ys, datasets: ds}, options: {animation: false, responsive: true,
    plugins: {legend: {labels: {boxWidth: 10, font: {size: 11}}}, legLines: opts.leg !== false}, scales: {y: {title: {display: !!opts.y, text: opts.y}}}}});
}
function card(parent, title, srcHtml) {
  const d = document.createElement('div'); d.className = 'card';
  d.innerHTML = `<h3>${title}</h3><canvas height="200"></canvas><p class="src">${srcHtml}</p>`; parent.appendChild(d); return d.querySelector('canvas');
}
const last = s => { const ks = Object.keys(s || {}).filter(y => /^\d{4}$/.test(y)).sort(); return ks.length ? [ks[ks.length - 1], s[ks[ks.length - 1]]] : [null, null]; };

// Cabecera
document.getElementById('meta').innerHTML = `Datos generados: ${fecha(O.generado)} · XV Legislatura: Cortes disueltas el 6-10-2026 (${link('https://www.boe.es/buscar/doc.php?id=BOE-A-2026-20742', 'RD 806/2026')}); elecciones el 29-11-2026.`;

// 1 · MACRO
(function () {
  const M = (O.macro && O.macro.indicadores) || [];
  const byId = Object.fromEntries(M.map(i => [i.id, i]));
  const kp = document.getElementById('kpis');
  [['paro', '%'], ['paro_juvenil', '%'], ['deuda', '% PIB'], ['deficit', '% PIB'], ['inflacion', '%'], ['pib_crecimiento', '%'], ['pib_pc_pps', 'UE=100'], ['productividad_hora', 'UE=100']].forEach(([id, u]) => {
    const i = byId[id]; const d = document.createElement('div'); d.className = 'kpi';
    if (!i || i.estado !== 'ok') { d.innerHTML = `<div class="l">${i ? i.nombre : id}</div><div class="v"><span class="pend">pendiente</span></div>`; kp.appendChild(d); return; }
    const [y, v] = last(i.series.ES); const eu = i.series.EU27_2020 ? i.series.EU27_2020[y] : null;
    d.innerHTML = `<div class="l">${i.nombre}</div><div class="v">${fmt(v)} <small>${u}</small></div><div class="c">${y} · UE-27: ${fmt(eu)} · ${link(i.web, i.fuente)}</div>`; kp.appendChild(d);
  });
  const g = document.getElementById('macro-charts');
  M.forEach(i => {
    const src = `Fuente: ${link(i.web, i.fuente)} · ${link(i.url, 'API')} · extraído ${fecha(O.macro.extraido)}${i.actualizado_fuente ? ' · actualizado en origen: ' + i.actualizado_fuente : ''}${i.aviso ? ' · ⚠ ' + i.aviso : ''}`;
    if (i.estado !== 'ok') { const d = document.createElement('div'); d.className = 'card'; d.innerHTML = `<h3>${i.nombre}</h3><p><span class="pend">pendiente</span> ${i.error || ''}</p>`; g.appendChild(d); return; }
    const isImf = i.fuente.startsWith('FMI');
    const keys = Object.keys(i.series).sort((a, b) => (a.startsWith('ES') ? -1 : 1));
    const cv = card(g, i.nombre, src + (isImf ? ` · <b>tramo discontinuo = estimación/proyección del FMI (≥ ${YEAR})</b>` : ''));
    lineChart(cv, i.series, keys, isImf ? {projFrom: YEAR, maxYear: YEAR + 1} : {});
  });
})();

// 2 · PROMESAS
(function () {
  const P = (O.manual && O.manual.pactocheck) || null;
  if (P) {
    new Chart(document.getElementById('ch-pacto'), {type: 'bar', data: {labels: ['Compromisos'], datasets: [
      {label: 'Cumplidas', data: [P.cumplidas], backgroundColor: '#1a7f37'}, {label: 'En progreso', data: [P.en_progreso], backgroundColor: '#90a4ae'},
      {label: 'Pendientes (sin iniciar)', data: [P.pendientes], backgroundColor: '#cfd8dc'}, {label: 'Incumplidas', data: [P.incumplidas], backgroundColor: '#c62828'}]},
      options: {indexAxis: 'y', animation: false, plugins: {legend: {position: 'bottom'}}, scales: {x: {stacked: true, max: P.total}, y: {stacked: true}}}});
    document.getElementById('src-pacto').innerHTML = `Fuente: ${link(P.url, P.fuente)} (actualizado ${P.fecha_dato}); ${link(P.url_balance, 'balance de Newtral')} · Recopilado a mano el ${O.manual.consultado}. ⚠ ${P.aviso}`;
  }
  const rows = ((O.manual && O.manual.promesas) || []).map(p => `<tr><td>${p.promesa}<br><small>${p.origen}</small></td><td class="e-${p.estado}">${p.estado}</td><td>${p.evidencia}</td><td>${link(p.url, 'fuente')}</td></tr>`).join('');
  document.getElementById('tabla-promesas').innerHTML = `<table><tr><th>Promesa</th><th>Estado</th><th>Evidencia</th><th></th></tr>${rows}</table>`;
})();

// 3 · DEMOCRACIA
(function () {
  const B = O.boe || {}; const L = (B.por_legislatura || []);
  const labs = L.map(r => r.legislatura);
  new Chart(document.getElementById('ch-rdl'), {type: 'bar', data: {labels: labs, datasets: [
    {label: 'Leyes ordinarias', data: L.map(r => r.leyes_ordinarias), backgroundColor: '#14213d', stack: 'l'},
    {label: 'Leyes orgánicas', data: L.map(r => r.leyes_organicas), backgroundColor: '#5c6bc0', stack: 'l'},
    {label: 'Reales decretos-leyes', data: L.map(r => r.rdl), backgroundColor: '#fca311', stack: 'r'},
    {label: 'RDL derogados (no convalidados)', data: L.map(r => r.rdl_derogados), backgroundColor: '#c62828', stack: 'd'}]},
    options: {animation: false, plugins: {legend: {labels: {boxWidth: 10, font: {size: 11}}}}}});
  new Chart(document.getElementById('ch-rdl-anual'), {data: {labels: labs, datasets: [
    {type: 'bar', label: 'Leyes/año', data: L.map(r => r.leyes_por_año), backgroundColor: '#14213d', yAxisID: 'y'},
    {type: 'bar', label: 'RDL/año', data: L.map(r => r.rdl_por_año), backgroundColor: '#fca311', yAxisID: 'y'},
    {type: 'line', label: 'Ratio RDL/leyes', data: L.map(r => r.ratio_rdl_leyes), borderColor: '#c62828', backgroundColor: '#c62828', yAxisID: 'y2'}]},
    options: {animation: false, scales: {y: {title: {display: true, text: 'normas por año'}}, y2: {position: 'right', grid: {display: false}, title: {display: true, text: 'ratio'}}}}});
  document.getElementById('src-rdl').innerHTML = `Fuente: ${link('https://www.boe.es/buscar/boe.php', 'BOE, buscador oficial (Sección I, Jefatura del Estado)')} + ${link('https://www.boe.es/datosabiertos/', 'API de legislación consolidada')} · extraído ${fecha(B.extraido)}. Se asigna por la fecha de la disposición; cada legislatura va de una sesión constitutiva a la siguiente. ${B.nota_xv || ''}`;
  document.getElementById('tabla-leg').innerHTML = `<table><tr><th>Leg.</th><th>Periodo</th><th>Gobierno</th><th>Años</th><th>Leyes</th><th>L. orgánicas</th><th>RDL</th><th>RDL convalidados*</th><th>RDL derogados</th><th>Leyes/año</th><th>RDL/año</th><th>RDL/leyes</th></tr>` +
    L.map(r => `<tr><td>${r.legislatura}</td><td>${r.inicio} → ${r.fin}</td><td>${r.gobierno}</td><td class="n">${fmt(r.años, 2)}</td><td class="n">${r.leyes_ordinarias}</td><td class="n">${r.leyes_organicas}</td><td class="n">${r.rdl}</td><td class="n">${r.rdl_convalidados_publicados}</td><td class="n">${r.rdl_derogados}</td><td class="n">${fmt(r.leyes_por_año)}</td><td class="n">${fmt(r.rdl_por_año)}</td><td class="n">${fmt(r.ratio_rdl_leyes, 2)}</td></tr>`).join('') +
    `</table><p class="small">* Acuerdos de convalidación del Congreso publicados en el BOE con título normalizado. Es fiable desde la XII Legislatura; antes los títulos no siguen un formato uniforme y el dato se queda corto. El detalle norma a norma (con referencia BOE) está en <code>data/boe_normas.json</code>.</p>`;
  const I = B.indultos_por_año || [];
  new Chart(document.getElementById('ch-indultos'), {type: 'bar', data: {labels: I.map(r => String(r.año)), datasets: [{label: 'Reales decretos de indulto', data: I.map(r => r.indultos), backgroundColor: '#5c6bc0'}]},
    options: {animation: false, plugins: {legLines: true, legend: {display: false}}}});
  document.getElementById('src-ind').innerHTML = `Fuente: BOE Sección III, títulos que contienen «se indulta», por año de publicación · extraído ${fecha(B.extraido)}. Cada real decreto suele corresponder a una persona. Para contrastar: ${link('https://civio.es/el-indultometro/', 'El Indultómetro (Civio)')}.`;
  selector('sel-dem', 'ch-dem', 'src-dem', 'democracia');
  document.getElementById('man-dem').innerHTML = ((O.manual && O.manual.manuales_democracia) || []).map(m => `<li><b>${m.nombre}</b>: ${m.estado === 'pendiente' ? '<span class="pend">pendiente</span> ' + m.motivo : m.valor} · ${link(m.url, 'fuente')}</li>`).join('');
})();

function selector(selId, cvId, srcId, cuadro) {
  const lst = ((O.indices && O.indices.indicadores) || []).filter(i => i.cuadro === cuadro && i.estado === 'ok');
  const sel = document.getElementById(selId); let ch = null;
  sel.innerHTML = lst.map((i, k) => `<option value="${k}">${i.nombre}</option>`).join('');
  const draw = () => { const i = lst[sel.value]; if (!i) return; if (ch) ch.destroy();
    const keys = ['Spain', 'Germany', 'France', 'Italy', 'Portugal'];
    ch = lineChart(document.getElementById(cvId), i.series, keys, {minYear: 1975});
    document.getElementById(srcId).innerHTML = `Fuente: ${link(i.web, i.fuente)} · ${link(i.url, 'descarga')} · extraído ${fecha(O.indices.extraido)}. Son índices de percepción o de expertos con metodología propia: se muestran tal cual, sin reescalar.`; };
  sel.onchange = draw; draw();
}

// 4 · CORRUPCIÓN
(function () {
  const C = O.cgpj || {}; const A = C.anual || {}; const ys = Object.keys(A).sort();
  new Chart(document.getElementById('ch-cgpj'), {data: {labels: ys.map(y => A[y].trimestres < 4 ? `${y} (${A[y].trimestres}T)` : y), datasets: [
    {type: 'bar', label: 'Sentencias condenatorias (total o parcial)', data: ys.map(y => A[y].cond_conformidad + A[y].cond_sin_conformidad + A[y].parc_condenatorias), backgroundColor: '#c62828', stack: 's'},
    {type: 'bar', label: 'Absolutorias', data: ys.map(y => A[y].absolutorias), backgroundColor: '#1a7f37', stack: 's'},
    {type: 'bar', label: 'Terminados por otras causas', data: ys.map(y => A[y].otras_causas), backgroundColor: '#90a4ae', stack: 's'},
    {type: 'line', label: 'Personas físicas procesadas o con juicio oral', data: ys.map(y => A[y].personas_fisicas), borderColor: '#14213d', backgroundColor: '#14213d'}]},
    options: {animation: false, plugins: {legend: {labels: {boxWidth: 10, font: {size: 11}}}}}});
  document.getElementById('src-cgpj').innerHTML = `Fuente: ${link(C.fuente, 'CGPJ, Repositorio de datos sobre procesos por corrupción')} (suma de los resúmenes nacionales trimestrales) · extraído ${fecha(C.extraido)}. Solo corrupción pública. El año marcado con «T» está incompleto.`;
  document.getElementById('tabla-cgpj').innerHTML = `<table><tr><th>Año</th><th>Trim.</th><th>Pers. físicas</th><th>Pers. jurídicas</th><th>Procedim.</th><th>Cond. con conformidad</th><th>Cond. sin conformidad</th><th>Parcialm. cond.</th><th>Absolutorias</th><th>Otras causas</th></tr>` +
    ys.map(y => { const r = A[y]; return `<tr><td>${y}</td><td class="n">${r.trimestres}</td><td class="n">${r.personas_fisicas}</td><td class="n">${r.personas_juridicas}</td><td class="n">${r.procedimientos}</td><td class="n">${r.cond_conformidad}</td><td class="n">${r.cond_sin_conformidad}</td><td class="n">${r.parc_condenatorias}</td><td class="n">${r.absolutorias}</td><td class="n">${r.otras_causas}</td></tr>`; }).join('') + '</table>';
  selector('sel-cor', 'ch-cor', 'src-cor', 'corrupcion');
  document.getElementById('man-cor').innerHTML = ((O.manual && O.manual.manuales_corrupcion) || []).map(m => `<li><b>${m.nombre}</b>: ${m.estado === 'pendiente' ? '<span class="pend">pendiente</span> ' + m.motivo : m.valor} · ${link(m.url, 'fuente')}</li>`).join('');
})();
