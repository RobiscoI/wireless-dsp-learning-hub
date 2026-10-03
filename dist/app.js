'use strict';
const weeksEl = document.getElementById('weeks');
const detail = document.getElementById('detail');
function el(tag, text, className) { const node = document.createElement(tag); if(text) node.textContent = text; if(className) node.className = className; return node; }
fetch('roadmap.json').then(r => { if(!r.ok) throw Error('load'); return r.json(); }).then(weeks => {
    function show(index) {
        const week = weeks[index]; detail.replaceChildren();
        detail.append(el('div', `WEEK ${String(index + 1).padStart(2, '0')} / 24`, 'eyebrow'), el('h2', week.title.split(' | ')[1]), el('p', week.date, 'meta'), el('p', week.purpose, 'purpose'), el('div', week.theory, 'theory'));
        week.sessions.forEach(session => { const d = el('details'); const summary = el('summary'); summary.append(el('span', session.id), document.createTextNode(session.title)); d.append(summary, el('div', session.body, 'session-body')); detail.append(d); });
        [...weeksEl.children].forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
    }
    weeks.forEach((week, index) => { const button = el('button'); button.type = 'button'; button.append(el('strong', `${String(index + 1).padStart(2, '0')}주`), document.createTextNode(week.title.split(' | ')[1])); button.addEventListener('click', () => show(index)); weeksEl.append(button); });
    show(0);
}).catch(() => { detail.replaceChildren(el('p', '로드맵을 불러오지 못했습니다. 페이지를 새로고침해 주세요.')); });
