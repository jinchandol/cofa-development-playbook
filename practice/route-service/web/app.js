'use strict';
const $ = id => document.getElementById(id);
let selected = null;
async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || '요청 실패');
  return data;
}
function notify(text) { $('message').textContent = text; }
function element(tag, text) { const node = document.createElement(tag); node.textContent = text; return node; }
async function loadRoutes() {
  const params = new URLSearchParams({q: $('query').value, active: $('active').value});
  const routes = await api('/api/routes?' + params);
  $('routes').replaceChildren();
  for (const route of routes) {
    const row = document.createElement('tr');
    for (const value of [route.route_id, route.name, route.active ? '운행' : '운휴', route.stop_count, route.blocked ? '경유 확인 필요' : '확인']) row.append(element('td', value));
    const cell = document.createElement('td');
    const button = element('button', '상세');
    button.setAttribute('aria-label', route.route_id + ' 상세');
    button.addEventListener('click', () => showRoute(route.route_id).catch(e => notify(e.message)));
    cell.append(button); row.append(cell); $('routes').append(row);
  }
  if (!routes.length) { const row = document.createElement('tr'); const cell = element('td', '검색 결과 없음'); cell.colSpan = 6; row.append(cell); $('routes').append(row); }
}
async function showRoute(id) {
  const route = await api('/api/routes/' + encodeURIComponent(id));
  selected = id;
  $('selection').textContent = `${id} · ${route.name}${route.blocked ? ' · 순서 충돌로 전체 경유 격리' : ''}`;
  $('stops').replaceChildren();
  for (const stop of route.stops) $('stops').append(element('li', `순번 ${stop.sequence}: ${stop.stop_id} · ${stop.name}`));
  $('name').value = route.name; $('running').checked = route.active; $('edit').hidden = false;
}
$('search').addEventListener('submit', event => {event.preventDefault(); loadRoutes().then(() => notify('')).catch(e => notify(e.message));});
$('edit').addEventListener('submit', async event => {
  event.preventDefault();
  const id = selected;
  try {
    await api('/api/routes/' + encodeURIComponent(id), {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name: $('name').value, active: $('running').checked})});
    await loadRoutes(); await showRoute(id);
    // Refresh visible reverse membership after a rename/active edit.
    $('members').replaceChildren();
    notify('저장했습니다. 원본 CSV는 변경되지 않았습니다.');
  } catch (error) { notify(error.message); }
});
$('reverse').addEventListener('submit', async event => {
  event.preventDefault(); $('members').replaceChildren();
  try {
    const data = await api('/api/stops/' + encodeURIComponent($('stop-id').value.trim()) + '/routes');
    for (const route of data.routes) $('members').append(element('li', `${route.route_id} · ${route.name} · ${route.active ? '운행' : '운휴'}`));
    if (!data.routes.length) $('members').append(element('li', '유효 경유 노선 없음'));
    notify('');
  } catch (error) { notify(error.message); }
});
async function loadQuality() {
  const data = await api('/api/quality');
  for (const [filename, count] of Object.entries(data.counts)) $('counts').append(element('div', `${filename}: 원본 ${count.input} = 수용 ${count.accepted} + 중복제거 ${count.deduplicated} + 격리 ${count.quarantined}`));
  $('quality').textContent = JSON.stringify({issues: data.issues, ledger: data.ledger}, null, 2);
}
Promise.all([loadRoutes(), loadQuality()]).catch(error => notify(error.message));
