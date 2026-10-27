/* ── Quarky Frontend Logic (app.js) ────────────────────────────────────────── */

const API_BASE = 'http://localhost:7777';
let activeSlug = null;
let allProfiles = [];
let currentOutboxItems = [];
let activePlatformFilter = 'all';

// ── HTTP API Client ──────────────────────────────────────────────────────────
async function request(method, endpoint, payload) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };
  if (payload) options.body = JSON.stringify(payload);
  const resp = await fetch(`${API_BASE}${endpoint}`, options);
  return resp.json();
}

const GET  = (endpoint)          => request('GET',  endpoint);
const POST = (endpoint, payload) => request('POST', endpoint, payload);

// ── Toast Notification ───────────────────────────────────────────────────────
function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `toast show ${type}`;
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.classList.remove('show');
  }, 4200);
}

// ── Views & Tabs ─────────────────────────────────────────────────────────────
function switchView(viewName) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));

  const targetView = document.getElementById(`view-${viewName}`);
  const targetTab  = document.querySelector(`[data-view="${viewName}"]`);

  if (targetView) targetView.classList.add('active');
  if (targetTab)  targetTab.classList.add('active');

  if (viewName === 'outbox')   loadOutbox();
  if (viewName === 'strategy') renderStrategyView();
  if (viewName === 'leads')    loadAllLeads();
}

document.querySelectorAll('.nav-tab').forEach(tab => {
  tab.addEventListener('click', () => switchView(tab.dataset.view));
});

document.getElementById('btn-switch-to-queue')?.addEventListener('click', () => {
  switchView('outbox');
});

// ── Pipeline Stats ───────────────────────────────────────────────────────────
async function refreshStats() {
  try {
    const stats = await GET('/api/stats');
    document.getElementById('stat-total').textContent   = stats.total_leads ?? '0';
    document.getElementById('stat-pending').textContent = stats.pending     ?? '0';
    document.getElementById('stat-sent').textContent    = stats.sent        ?? '0';
  } catch (err) {
    console.error('Stats error:', err);
  }
}

// ── Product Switcher ─────────────────────────────────────────────────────────
async function loadProducts() {
  try {
    allProfiles = await GET('/api/profiles');
    const container = document.getElementById('product-tabs');
    container.innerHTML = '';

    if (!allProfiles || allProfiles.length === 0) {
      container.innerHTML = '<span class="muted" style="padding: 6px 12px; font-size: 11px;">No products yet</span>';
      return;
    }

    const icons = {
      utility_app: '📱',
      intimacy_app: '🤍',
      nonfiction_book: '📖',
      generic: '🚀'
    };

    allProfiles.forEach(p => {
      const btn = document.createElement('button');
      btn.className = `prod-pill ${p.slug === activeSlug ? 'active' : ''}`;
      const icon = icons[p.archetype] || '📦';
      btn.innerHTML = `<span>${icon}</span> <span>${p.slug}</span>`;
      btn.title = p.description || p.slug;
      btn.addEventListener('click', () => selectProduct(p.slug));
      container.appendChild(btn);
    });

    if (!activeSlug && allProfiles.length > 0) {
      selectProduct(allProfiles[0].slug);
    }
  } catch (err) {
    console.error('Load products error:', err);
  }
}

function selectProduct(slug) {
  activeSlug = slug;
  document.querySelectorAll('.prod-pill').forEach(btn => {
    btn.classList.toggle('active', btn.textContent.includes(slug));
  });

  renderStrategyView();
  loadOutbox();
  refreshStats();
}

// ── GTM Intelligence (Whom · Where · How) ───────────────────────────────────
function renderStrategyView() {
  const profile = allProfiles.find(p => p.slug === activeSlug);
  if (!profile) return;

  document.getElementById('strat-slug').textContent = profile.slug;
  document.getElementById('strat-desc').textContent = profile.description || 'GTM Intelligence';
  document.getElementById('strat-audience').textContent = profile.target_audience || 'Target early adopters';
  document.getElementById('strat-pain').textContent = (profile.pain_keywords || []).slice(0, 8).join(', ') || 'High-intent buying keywords';
  document.getElementById('strat-archetype').textContent = profile.archetype;
  
  // Platforms chips
  const platContainer = document.getElementById('strat-platforms');
  platContainer.innerHTML = '';
  (profile.platforms || []).forEach(pl => {
    const chip = document.createElement('span');
    chip.className = 'chip';
    chip.textContent = pl.toUpperCase();
    platContainer.appendChild(chip);
  });

  // Subreddits chips
  const subContainer = document.getElementById('strat-subreddits');
  subContainer.innerHTML = '';
  (profile.subreddits || []).forEach(sub => {
    const a = document.createElement('a');
    a.className = 'chip chip-link';
    a.href = `https://reddit.com/${sub}`;
    a.target = '_blank';
    a.textContent = sub;
    subContainer.appendChild(a);
  });

  // Threads & Facebook chips
  const commContainer = document.getElementById('strat-communities');
  commContainer.innerHTML = '';
  (profile.threads_queries || []).forEach(tq => {
    const chip = document.createElement('span');
    chip.className = 'chip';
    chip.textContent = `Threads: ${tq}`;
    commContainer.appendChild(chip);
  });
  (profile.facebook_groups || []).forEach(fbg => {
    const chip = document.createElement('span');
    chip.className = 'chip';
    chip.textContent = `FB: ${fbg}`;
    commContainer.appendChild(chip);
  });

  document.getElementById('strat-tone').textContent = profile.pitch_tone || 'Conversational & direct';
  document.getElementById('strat-angle').textContent = profile.pitch_angle || 'Direct solution to customer friction.';
  
  const linkEl = document.getElementById('strat-link');
  const targetUrl = profile.product_url || (profile.input.startsWith('http') ? profile.input : '#');
  linkEl.href = targetUrl;
  linkEl.textContent = targetUrl;
}

// ── Outbox / Lead Stream ────────────────────────────────────────────────────
async function loadOutbox() {
  const container = document.getElementById('outbox-cards');
  const countBadge = document.getElementById('badge-outbox-count');

  try {
    const url = activeSlug
      ? `/api/outbox?app=${activeSlug}&status=pending_approval`
      : `/api/outbox?status=pending_approval`;
    
    currentOutboxItems = await GET(url);
    countBadge.textContent = currentOutboxItems.length;

    renderFilteredOutbox();
  } catch (err) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">⚠️</div>
        <h3>Failed to Connect</h3>
        <p class="muted">Check if Quarky server is running on port 7777.</p>
      </div>`;
  }
}

function renderFilteredOutbox() {
  const container = document.getElementById('outbox-cards');
  
  let items = currentOutboxItems;
  if (activePlatformFilter !== 'all') {
    items = items.filter(it => it.source === activePlatformFilter);
  }

  if (items.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🎉</div>
        <h3>All Caught Up for ${activeSlug || 'this product'}!</h3>
        <p class="muted">No pending leads matching "${activePlatformFilter}". Click <strong>Scout More Leads</strong> or switch platforms.</p>
      </div>`;
    return;
  }

  container.innerHTML = '';
  items.forEach(item => {
    const card = document.createElement('div');
    card.className = 'lead-card';
    card.id = `card-${item.outbox_id}`;

    // Split title and body snippet from context
    const parts = (item.context_snippet || '').split('|');
    const title = parts[0]?.trim() || 'High Intent Discussion';
    const bodyText = parts.slice(1).join('|').trim();

    const platformBadgeClass = `tag-${item.source}`;
    const cleanUrl = escapeHtml(item.identifier || '');

    card.innerHTML = `
      <div class="card-top">
        <div class="card-badges">
          <span class="tag-platform ${platformBadgeClass}">${item.source}</span>
          <span class="tag-intent">🔥 High Intent Prospect</span>
          <span class="tag-unlocked">🔓 Unlocked & Active</span>
          <span class="tag-account-safe">🟢 3-Week Account Verified</span>
          <span class="tag-recency">⏱️ ${escapeHtml(item.recency_label || 'Recent Active')}</span>
        </div>
        <span class="card-time">${formatTimeAgo(item.queued_at)}</span>
      </div>

      <div class="prospect-quote">
        <div class="quote-title">${escapeHtml(title)}</div>
        <div class="quote-text">${escapeHtml(bodyText || title)}</div>
      </div>

      <div class="thread-link-row">
        <a class="thread-link" href="${cleanUrl}" target="_blank">
          <span>↗ View Live Thread</span>
          <span class="muted" style="font-size: 11px;">(${cleanUrl.substring(0, 60)}...)</span>
        </a>
      </div>

      <div class="pitch-container">
        <div class="pitch-label-bar">
          <span>Crafted 1-to-1 Peer Pitch</span>
          <span class="pitch-edit-tip">✏️ You can edit text before sending</span>
        </div>
        <textarea class="pitch-textarea" id="pitch-text-${item.outbox_id}">${escapeHtml(item.pitch_text || '')}</textarea>
      </div>

      <div class="card-actions">
        <button class="btn-push" data-id="${item.outbox_id}">
          <span>🚀 Approve & Open in Chrome</span>
        </button>
        <button class="btn-secondary btn-copy" data-id="${item.outbox_id}">
          📋 Copy Text
        </button>
        <button class="btn-dismiss" data-id="${item.outbox_id}">
          ✕ Dismiss
        </button>
      </div>
    `;

    container.appendChild(card);
  });

  // Attach card event listeners
  container.querySelectorAll('.btn-push').forEach(btn => {
    btn.addEventListener('click', () => pushLead(btn.dataset.id));
  });
  container.querySelectorAll('.btn-copy').forEach(btn => {
    btn.addEventListener('click', () => copyPitchOnly(btn.dataset.id));
  });
  container.querySelectorAll('.btn-dismiss').forEach(btn => {
    btn.addEventListener('click', () => dismissLead(btn.dataset.id));
  });
}

// ── Action Handlers ──────────────────────────────────────────────────────────
async function pushLead(outboxId) {
  const textarea = document.getElementById(`pitch-text-${outboxId}`);
  const customPitch = textarea ? textarea.value.trim() : null;

  const btn = document.querySelector(`.btn-push[data-id="${outboxId}"]`);
  if (btn) {
    btn.textContent = '⏳ Pushing to Chrome…';
    btn.disabled = true;
  }

  try {
    const res = await POST('/api/push', {
      outbox_id: parseInt(outboxId),
      pitch_text: customPitch
    });

    if (res.success) {
      showToast('🚀 Chrome opened to thread! Pitch is in your clipboard — just press Cmd+V to reply.', 'success');
      // Animate card removal
      const card = document.getElementById(`card-${outboxId}`);
      if (card) {
        card.style.opacity = '0.3';
        card.style.pointerEvents = 'none';
        setTimeout(() => loadOutbox(), 600);
      }
    } else {
      showToast(res.message || 'Push failed', 'error');
      if (btn) {
        btn.textContent = '🚀 Approve & Open in Chrome';
        btn.disabled = false;
      }
    }
  } catch (err) {
    showToast('Failed to push outbox item', 'error');
  }

  refreshStats();
}

function copyPitchOnly(outboxId) {
  const textarea = document.getElementById(`pitch-text-${outboxId}`);
  if (textarea) {
    navigator.clipboard.writeText(textarea.value);
    showToast('📋 Pitch copied to clipboard!', 'success');
  }
}

async function dismissLead(outboxId) {
  await POST('/api/reject', { outbox_id: parseInt(outboxId) });
  showToast('Lead dismissed and archived.', 'info');
  loadOutbox();
  refreshStats();
}

// ── Platform Filtering ───────────────────────────────────────────────────────
document.querySelectorAll('.filter-pill').forEach(pill => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    activePlatformFilter = pill.dataset.filter;
    renderFilteredOutbox();
  });
});

// ── Pipeline Scout & Draft Triggers ──────────────────────────────────────────
function setPipelineStatus(msg, type = '') {
  const el = document.getElementById('pipeline-status');
  el.textContent = msg;
  el.className = `status-indicator ${type}`;
}

document.getElementById('btn-scout').addEventListener('click', async () => {
  if (!activeSlug) return;
  setPipelineStatus('⚡ Scouting discussions across Reddit, Threads & Facebook…', 'running');
  const res = await POST('/api/scout', { app_slug: activeSlug });
  setPipelineStatus(`✓ Scout complete: ${res.new_leads} new leads discovered.`, 'done');
  await loadOutbox();
  refreshStats();
});

document.getElementById('btn-draft').addEventListener('click', async () => {
  if (!activeSlug) return;
  setPipelineStatus('✏️ Drafting personalized 1-to-1 pitches…', 'running');
  const res = await POST('/api/draft', { app_slug: activeSlug });
  setPipelineStatus(`✓ ${res.drafted} pitches drafted.`, 'done');
  await loadOutbox();
  refreshStats();
});

document.getElementById('btn-run-all').addEventListener('click', async () => {
  if (!activeSlug) return;
  setPipelineStatus('▶ Scouting high-intent threads…', 'running');
  const s = await POST('/api/scout', { app_slug: activeSlug });
  setPipelineStatus(`▶ Drafting conversion pitches for ${s.new_leads} leads…`, 'running');
  const d = await POST('/api/draft', { app_slug: activeSlug });
  setPipelineStatus(`✓ Done! ${s.new_leads} leads found, ${d.drafted} pitches queued.`, 'done');
  await loadOutbox();
  refreshStats();
});

// ── Analyze Product Form ─────────────────────────────────────────────────────
document.getElementById('btn-run-analyze').addEventListener('click', async () => {
  const inputVal = document.getElementById('product-input').value.trim();
  const slugVal  = document.getElementById('product-slug').value.trim();

  if (!inputVal) {
    showToast('Please enter a product description or URL.', 'error');
    return;
  }

  const btn = document.getElementById('btn-run-analyze');
  btn.textContent = 'Analyzing Whom · Where · How…';
  btn.disabled = true;

  try {
    const bp = await POST('/api/analyze', { product: inputVal, slug: slugVal || undefined });
    btn.textContent = '⚡ Generate GTM Blueprint & Scout Leads →';
    btn.disabled = false;

    if (bp.error) {
      showToast(bp.error, 'error');
      return;
    }

    showToast(`Blueprint for "${bp.slug}" generated! Auto-scouting leads…`, 'success');
    
    // Auto scout and draft for new product
    await POST('/api/scout', { app_slug: bp.slug });
    await POST('/api/draft', { app_slug: bp.slug });

    await loadProducts();
    selectProduct(bp.slug);
    switchView('outbox');
  } catch (err) {
    btn.textContent = '⚡ Generate GTM Blueprint & Scout Leads →';
    btn.disabled = false;
    showToast('Error analyzing product', 'error');
  }
});

// ── All Leads Table ──────────────────────────────────────────────────────────
async function loadAllLeads() {
  const tbody = document.getElementById('leads-table-body');
  const totalCountEl = document.getElementById('leads-total-count');

  try {
    const url = activeSlug ? `/api/leads?app=${activeSlug}` : '/api/leads';
    const leads = await GET(url);
    totalCountEl.textContent = `${leads.length} total leads for ${activeSlug || 'all products'}`;

    tbody.innerHTML = '';
    if (leads.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--text-muted)">No leads found.</td></tr>';
      return;
    }

    leads.forEach(l => {
      const tr = document.createElement('tr');
      const parts = (l.context_snippet || '').split('|');
      const snippet = parts[0]?.substring(0, 90) || '';

      tr.innerHTML = `
        <td><span class="tag-platform tag-${l.source}">${l.source}</span></td>
        <td style="max-width:320px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(snippet)}...</td>
        <td><span class="tag-intent" style="font-size:10px;">${l.status}</span></td>
        <td><a class="thread-link" href="${escapeHtml(l.identifier)}" target="_blank">Open ↗</a></td>
        <td style="color:var(--text-muted);font-size:11px;">${formatTimeAgo(l.created_at)}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Failed to load leads:', err);
  }
}

// ── Utility Helpers ──────────────────────────────────────────────────────────
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function formatTimeAgo(isoString) {
  if (!isoString) return '';
  const diffSec = (Date.now() - new Date(isoString + 'Z').getTime()) / 1000;
  if (diffSec < 60) return `${Math.max(1, Math.round(diffSec))}s ago`;
  if (diffSec < 3600) return `${Math.round(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.round(diffSec / 3600)}h ago`;
  return `${Math.round(diffSec / 86400)}d ago`;
}

// ── App Boot ─────────────────────────────────────────────────────────────────
(async () => {
  await loadProducts();
  await refreshStats();
  setInterval(refreshStats, 30000);
})();
