async function uploadFile() {
  const fileInput = document.getElementById('file');
  const file = fileInput.files[0];
  if (!file) {
    alert('Select a file first');
    return;
  }
  const fd = new FormData();
  fd.append('file', file);
  document.getElementById('uploadStatus').innerText = 'Uploading...';
  try {
    const res = await fetch('/upload-news', { method: 'POST', body: fd });
    const j = await res.json();
    document.getElementById('uploadStatus').innerText = `Uploaded: ${j.status}, ${j.count || 0} items`;
  } catch (e) {
    document.getElementById('uploadStatus').innerText = 'Upload failed';
    console.error(e);
  }
}

async function runPipeline() {
  document.getElementById('output').innerText = 'Running pipeline...';
  try {
    const res = await fetch('/run-pipeline', { method: 'POST' });
    const j = await res.json();
    document.getElementById('output').innerText = JSON.stringify(j, null, 2);
  } catch (e) {
    document.getElementById('output').innerText = 'Pipeline failed';
    console.error(e);
  }
}

document.getElementById('uploadBtn').addEventListener('click', validateAndUploadFile);
document.getElementById('runBtn').addEventListener('click', runPipeline);
document.getElementById('resetBtn').addEventListener('click', resetIndex);

async function askQuery() {
  const q = document.getElementById('queryInput').value.trim();
  if (!q) {
    alert('Enter a question');
    return;
  }
  if (q.length < 3) {
    alert('Query is too short');
    return;
  }
  const out = document.getElementById('qaOutput');
  out.textContent = 'Querying...';
  try {
    const res = await fetch(`/financial-qa?q=${encodeURIComponent(q)}`);
    const j = await res.json();
    if (j.status !== 'ok') {
      out.textContent = j.message || 'Query failed';
      return;
    }
    const a = j.answer;
    // Render structured HTML instead of raw JSON
    const parts = [];
    parts.push(`<div><strong>Question:</strong> ${escapeHtml(a.summary?.question || '')}</div>`);
    parts.push(`<div><strong>Top Tickers:</strong> ${(a.summary?.top_tickers || []).join(', ')}</div>`);
    parts.push(`<div><strong>Confidence:</strong> ${a.confidence}</div>`);
    if (a.risks && a.risks.length) {
      parts.push('<div style="margin-top:8px"><strong>Risks</strong><ul>' + a.risks.map(r => `<li>${escapeHtml(r)}</li>`).join('') + '</ul></div>');
    }
    if (a.opportunities && a.opportunities.length) {
      parts.push('<div style="margin-top:8px"><strong>Opportunities</strong><ul>' + a.opportunities.map(r => `<li>${escapeHtml(r)}</li>`).join('') + '</ul></div>');
    }
    if (a.context && a.context.length) {
      const items = a.context.map(c => {
        const s = typeof c.sentiment === 'number' ? c.sentiment : 0;
        const cls = s > 0.05 ? 'pos' : (s < -0.05 ? 'neg' : 'neu');
        return `<li><span class="chip">${escapeHtml(c.ticker || '')}</span>${escapeHtml(c.title || '')}<span class="badge ${cls}">${s.toFixed(2)}</span></li>`;
      }).join('');
      parts.push('<div style="margin-top:8px"><strong>Context</strong><ul>' + items + '</ul></div>');
    }
    out.innerHTML = parts.join('');
  } catch (e) {
    out.textContent = 'Query failed';
    console.error(e);
  }
}

// Reset index
async function resetIndex() {
  const out = document.getElementById('output');
  out.innerText = 'Resetting index...';
  try {
    const res = await fetch('/reset-index', { method: 'POST' });
    const j = await res.json();
    out.innerText = JSON.stringify(j, null, 2);
  } catch (e) {
    out.innerText = 'Reset failed';
    console.error(e);
  }
}

// Validate and upload file
async function validateAndUploadFile() {
  const fileInput = document.getElementById('file');
  const file = fileInput.files[0];
  if (!file) {
    alert('Select a file first');
    return;
  }
  const allowed = ['.jsonl', '.txt'];
  const dot = file.name.lastIndexOf('.');
  const ext = dot >= 0 ? file.name.slice(dot).toLowerCase() : '';
  if (!allowed.includes(ext)) {
    alert('Only .jsonl or .txt files are allowed');
    return;
  }
  const maxSize = 5 * 1024 * 1024; // 5MB
  if (file.size > maxSize) {
    alert('File too large (max 5MB)');
    return;
  }
  await uploadFile();
}

document.getElementById('askBtn').addEventListener('click', askQuery);

// Theme toggle
function escapeHtml(s) {
  return String(s).replace(/[&<>"]+/g, (m) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
}

function applyTheme(t) {
  const body = document.body;
  if (t === 'dark') body.classList.add('dark');
  else body.classList.remove('dark');
}

function initTheme() {
  const saved = localStorage.getItem('theme');
  if (saved) { applyTheme(saved); return; }
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(prefersDark ? 'dark' : 'light');
}

document.getElementById('themeToggle').addEventListener('click', () => {
  const isDark = document.body.classList.contains('dark');
  const next = isDark ? 'light' : 'dark';
  applyTheme(next);
  localStorage.setItem('theme', next);
});

initTheme();
