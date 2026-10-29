/**
 * RevOps AI - Human-in-the-Loop Web Dashboard Frontend
 * Bespoke Vanilla JS with Tactile UI, Fast Kanban, & Slide-Over Drawer
 */

(() => {
  'use strict';

  // Global State
  const state = {
    tenantId: 'tenant_clinicas_madrid',
    leads: [],
    stats: {},
    selectedLead: null,
    isLoading: false,
  };

  // DOM Elements
  const elements = {
    tenantSelect: document.getElementById('tenant-select'),
    refreshBtn: document.getElementById('refresh-btn'),
    // KPI Badges
    metricTotal: document.getElementById('stat-total'),
    metricPending: document.getElementById('stat-pending'),
    metricQualified: document.getElementById('stat-qualified'),
    metricRate: document.getElementById('stat-rate'),
    metricInterested: document.getElementById('stat-interested'),
    metricDiscarded: document.getElementById('stat-discarded'),
    // Kanban Columns
    colPending: document.getElementById('col-cards-pending'),
    colSent: document.getElementById('col-cards-sent'),
    colInterested: document.getElementById('col-cards-interested'),
    colDiscarded: document.getElementById('col-cards-discarded'),
    countPending: document.getElementById('count-pending'),
    countSent: document.getElementById('count-sent'),
    countInterested: document.getElementById('count-interested'),
    countDiscarded: document.getElementById('count-discarded'),
    // Drawer
    drawerBackdrop: document.getElementById('drawer-backdrop'),
    slideDrawer: document.getElementById('slide-drawer'),
    drawerClose: document.getElementById('drawer-close'),
    drawerTitle: document.getElementById('drawer-lead-name'),
    drawerScore: document.getElementById('drawer-lead-score'),
    drawerUrl: document.getElementById('drawer-lead-url'),
    drawerTenant: document.getElementById('drawer-lead-tenant'),
    drawerStatus: document.getElementById('drawer-lead-status'),
    drawerGaps: document.getElementById('drawer-gaps-list'),
    drawerCopy: document.getElementById('drawer-copy-textarea'),
    btnApprove: document.getElementById('btn-approve-lead'),
    btnReject: document.getElementById('btn-reject-lead'),
    // Modal Discard Reason
    modalBackdrop: document.getElementById('modal-discard'),
    modalReasonInput: document.getElementById('modal-reason-input'),
    modalCancelBtn: document.getElementById('modal-cancel-btn'),
    modalConfirmBtn: document.getElementById('modal-confirm-btn'),
    // Toast Container
    toastContainer: document.getElementById('toast-container'),
  };

  /**
   * Helper: Show Toast Notification
   */
  function showToast(message, type = 'success') {
    if (!elements.toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 150ms ease';
      setTimeout(() => toast.remove(), 160);
    }, 3200);
  }

  /**
   * Extract microdiagnosis gaps from lead summary
   */
  function parseMicrodiagnosisGaps(summary) {
    if (!summary || typeof summary !== 'string') {
      return ['Auditoría general completada'];
    }
    const lines = summary.split('\n').map(s => s.trim()).filter(Boolean);
    if (lines.length > 0) {
      return lines;
    }
    return [summary];
  }

  /**
   * Determine score class (anti-ai semantic color scale)
   */
  function getScoreClass(score) {
    if (score >= 75) return 'high';
    if (score >= 50) return 'medium';
    return 'low';
  }

  /**
   * Fetch KPI statistics
   */
  async function fetchStats() {
    try {
      const res = await fetch(`/api/v1/dashboard/stats?tenant_id=${encodeURIComponent(state.tenantId)}`);
      if (!res.ok) throw new Error('Error al cargar métricas');
      const data = await res.json();
      state.stats = data;

      if (elements.metricTotal) elements.metricTotal.textContent = data.total_leads ?? 0;
      if (elements.metricPending) elements.metricPending.textContent = data.pending_approval_count ?? 0;
      if (elements.metricQualified) elements.metricQualified.textContent = data.qualified_count ?? 0;
      if (elements.metricRate) elements.metricRate.textContent = `${data.qualification_rate ?? 0}%`;
      if (elements.metricInterested) elements.metricInterested.textContent = data.interested_count ?? 0;
      if (elements.metricDiscarded) elements.metricDiscarded.textContent = data.discarded_count ?? 0;
    } catch (err) {
      console.warn('Stats fetch notice:', err.message);
    }
  }

  /**
   * Fetch leads from API (combines DB leads and approval store pending leads)
   */
  async function fetchLeads() {
    try {
      // 1. Fetch from repository dashboard/leads
      const [leadsRes, pendingRes] = await Promise.allSettled([
        fetch(`/api/v1/dashboard/leads?tenant_id=${encodeURIComponent(state.tenantId)}`),
        fetch(`/api/v1/approval/pending?tenant_id=${encodeURIComponent(state.tenantId)}`),
      ]);

      let allLeads = [];
      const leadMap = new Map();

      if (leadsRes.status === 'fulfilled' && leadsRes.value.ok) {
        const repoLeads = await leadsRes.value.json();
        repoLeads.forEach(lead => leadMap.set(lead.id, lead));
      }

      if (pendingRes.status === 'fulfilled' && pendingRes.value.ok) {
        const pendingLeads = await pendingRes.value.json();
        pendingLeads.forEach(lead => leadMap.set(lead.id, lead));
      }

      state.leads = Array.from(leadMap.values());
      renderKanban();
    } catch (err) {
      console.error('Error fetching leads:', err);
      showToast('Error al conectar con la API de leads', 'error');
    }
  }

  /**
   * Render Kanban Board
   */
  function renderKanban() {
    const buckets = {
      pending: [],
      sent: [],
      interested: [],
      discarded: [],
    };

    state.leads.forEach(lead => {
      const s = (lead.state || '').toUpperCase();
      if (s === 'PENDING_APPROVAL' || s === 'DRAFTING' || s === 'QUALIFIED') {
        buckets.pending.push(lead);
      } else if (s === 'SENT' || s === 'APPROVED') {
        buckets.sent.push(lead);
      } else if (s === 'INTERESTED') {
        buckets.interested.push(lead);
      } else if (s === 'DISCARDED' || s === 'OPT_OUT') {
        buckets.discarded.push(lead);
      } else {
        buckets.pending.push(lead);
      }
    });

    // Update Counter Badges
    if (elements.countPending) elements.countPending.textContent = buckets.pending.length;
    if (elements.countSent) elements.countSent.textContent = buckets.sent.length;
    if (elements.countInterested) elements.countInterested.textContent = buckets.interested.length;
    if (elements.countDiscarded) elements.countDiscarded.textContent = buckets.discarded.length;

    renderColumn(elements.colPending, buckets.pending, 'Sin prospectos pendientes');
    renderColumn(elements.colSent, buckets.sent, 'Sin despachos registrados');
    renderColumn(elements.colInterested, buckets.interested, 'Sin respuestas interesadas');
    renderColumn(elements.colDiscarded, buckets.discarded, 'Sin descartes registrados');
  }

  /**
   * Render cards inside a specific Kanban column
   */
  function renderColumn(colElement, list, emptyText) {
    if (!colElement) return;
    colElement.innerHTML = '';

    if (list.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'empty-state';
      empty.textContent = emptyText;
      colElement.appendChild(empty);
      return;
    }

    list.forEach(lead => {
      const card = document.createElement('div');
      card.className = 'prospect-card';
      card.dataset.leadId = lead.id;

      const scoreClass = getScoreClass(lead.score || 0);
      const gaps = parseMicrodiagnosisGaps(lead.research_summary);
      const cleanUrl = (lead.url || '').replace(/^https?:\/\//, '').replace(/\/$/, '');

      let statusBadgeClass = 'status-badge-pending';
      const s = (lead.state || '').toUpperCase();
      if (s === 'APPROVED' || s === 'SENT') statusBadgeClass = 'status-badge-sent';
      else if (s === 'INTERESTED') statusBadgeClass = 'status-badge-interested';
      else if (s === 'DISCARDED' || s === 'OPT_OUT') statusBadgeClass = 'status-badge-discarded';

      card.innerHTML = `
        <div class="card-top">
          <div class="card-title">${escapeHtml(lead.name || 'Prospecto sin nombre')}</div>
          <span class="card-score ${scoreClass}">${lead.score || 0} pts</span>
        </div>
        <div class="card-domain">${escapeHtml(cleanUrl)}</div>
        <div class="card-tags">
          ${gaps.slice(0, 2).map(g => `<span class="card-tag gap">${escapeHtml(g.substring(0, 36))}</span>`).join('')}
        </div>
        <div class="card-footer">
          <span class="card-status-badge ${statusBadgeClass}">${s || 'PENDIENTE'}</span>
          <span>ID: ${lead.id.substring(0, 8)}</span>
        </div>
      `;

      card.addEventListener('click', () => openInspectionDrawer(lead));
      colElement.appendChild(card);
    });
  }

  /**
   * Open Slide-Over Drawer for Inspection & Proposal Copy Review
   */
  function openInspectionDrawer(lead) {
    state.selectedLead = lead;
    if (!elements.slideDrawer || !elements.drawerBackdrop) return;

    elements.drawerTitle.textContent = lead.name || 'Prospecto';
    elements.drawerScore.textContent = `${lead.score || 0}/100`;
    elements.drawerScore.className = `card-score ${getScoreClass(lead.score || 0)}`;

    elements.drawerUrl.textContent = lead.url || '-';
    elements.drawerUrl.href = lead.url && lead.url.startsWith('http') ? lead.url : `https://${lead.url}`;
    elements.drawerTenant.textContent = lead.tenant_id || state.tenantId;
    elements.drawerStatus.textContent = lead.state || 'PENDING_APPROVAL';

    // Microdiagnosis gaps
    elements.drawerGaps.innerHTML = '';
    const gaps = parseMicrodiagnosisGaps(lead.research_summary);
    gaps.forEach((gap, idx) => {
      const gapCard = document.createElement('div');
      gapCard.className = `gap-card ${idx === 0 ? 'critical' : 'warning'}`;
      gapCard.innerHTML = `
        <span class="gap-name">${escapeHtml(gap)}</span>
        <span class="gap-badge">Hallazgo ${idx + 1}</span>
      `;
      elements.drawerGaps.appendChild(gapCard);
    });

    // Proposal copy
    elements.drawerCopy.value = lead.draft_message || '';

    // Action button states: enable approval if pending
    const isPending = (lead.state || '').toUpperCase() === 'PENDING_APPROVAL' || (lead.state || '').toUpperCase() === 'QUALIFIED';
    if (elements.btnApprove) elements.btnApprove.style.display = isPending ? 'inline-flex' : 'none';
    if (elements.btnReject) elements.btnReject.style.display = isPending ? 'inline-flex' : 'none';

    elements.drawerBackdrop.classList.add('open');
    elements.slideDrawer.classList.add('open');
  }

  /**
   * Close Slide-Over Drawer
   */
  function closeDrawer() {
    if (!elements.slideDrawer || !elements.drawerBackdrop) return;
    elements.drawerBackdrop.classList.remove('open');
    elements.slideDrawer.classList.remove('open');
    state.selectedLead = null;
  }

  /**
   * Approve and Dispatch Selected Prospect
   */
  async function handleApprove() {
    if (!state.selectedLead) return;
    const leadId = state.selectedLead.id;

    try {
      if (elements.btnApprove) elements.btnApprove.disabled = true;

      const payload = {
        tenant_id: state.tenantId,
        lead_id: leadId,
        action: 'APPROVE',
        reason: '',
      };

      const res = await fetch('/api/v1/approval/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Error al aprobar prospecto');
      }

      showToast(`Prospecto "${state.selectedLead.name}" aprobado y despachado con éxito`, 'success');
      closeDrawer();
      await refreshAll();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      if (elements.btnApprove) elements.btnApprove.disabled = false;
    }
  }

  /**
   * Prompt discard modal
   */
  function openDiscardModal() {
    if (!state.selectedLead) return;
    if (elements.modalBackdrop) {
      elements.modalReasonInput.value = '';
      elements.modalBackdrop.classList.add('open');
      elements.modalReasonInput.focus();
    }
  }

  function closeDiscardModal() {
    if (elements.modalBackdrop) {
      elements.modalBackdrop.classList.remove('open');
    }
  }

  /**
   * Confirm Discard Action
   */
  async function handleConfirmDiscard() {
    if (!state.selectedLead) return;
    const reason = elements.modalReasonInput.value.trim() || 'Descartado manualmente por operador';

    try {
      const payload = {
        tenant_id: state.tenantId,
        lead_id: state.selectedLead.id,
        action: 'REJECT',
        reason: reason,
      };

      const res = await fetch('/api/v1/approval/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Error al descartar prospecto');
      }

      showToast(`Prospecto descartado: ${reason}`, 'success');
      closeDiscardModal();
      closeDrawer();
      await refreshAll();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  /**
   * Refresh all components
   */
  async function refreshAll() {
    await Promise.all([fetchStats(), fetchLeads()]);
  }

  /**
   * Escape HTML utility
   */
  function escapeHtml(text) {
    if (!text) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  /**
   * Event Listeners Setup
   */
  function initEventListeners() {
    // Tenant Selector
    if (elements.tenantSelect) {
      elements.tenantSelect.addEventListener('change', (e) => {
        state.tenantId = e.target.value;
        refreshAll();
      });
    }

    // Refresh Button
    if (elements.refreshBtn) {
      elements.refreshBtn.addEventListener('click', () => refreshAll());
    }

    // Drawer Close
    if (elements.drawerClose) {
      elements.drawerClose.addEventListener('click', closeDrawer);
    }
    if (elements.drawerBackdrop) {
      elements.drawerBackdrop.addEventListener('click', closeDrawer);
    }

    // Drawer Actions
    if (elements.btnApprove) {
      elements.btnApprove.addEventListener('click', handleApprove);
    }
    if (elements.btnReject) {
      elements.btnReject.addEventListener('click', openDiscardModal);
    }

    // Modal Actions
    if (elements.modalCancelBtn) {
      elements.modalCancelBtn.addEventListener('click', closeDiscardModal);
    }
    if (elements.modalConfirmBtn) {
      elements.modalConfirmBtn.addEventListener('click', handleConfirmDiscard);
    }

    // Keyboard Shortcuts (ESC to close drawer/modal)
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (elements.modalBackdrop && elements.modalBackdrop.classList.contains('open')) {
          closeDiscardModal();
        } else if (elements.slideDrawer && elements.slideDrawer.classList.contains('open')) {
          closeDrawer();
        }
      }
    });
  }

  // Initialization
  document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    refreshAll();
  });
})();
