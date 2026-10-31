/**
 * RevOps AI - Command Center Web Dashboard Module
 * Strictly Anti-AI · Tactile UI · Zero Layout Shift · High-Density Architecture
 */

(() => {
  'use strict';

  // 1. Application Reactive State
  const state = {
    tenantId: localStorage.getItem('revops_tenant') || 'tenant_clinicas_madrid',
    leads: [],
    filteredLeads: [],
    stats: {},
    selectedLead: null,
    activeFilter: 'all',
    searchQuery: '',
    activeTab: 'tab-diagnosis',
    activeChannel: 'email',
    discardTargetLeadId: null,
    isLoading: false,
  };

  // 2. DOM Elements Cache
  const el = {
    // Header & Tenant
    tenantSelect: document.getElementById('tenant-select'),
    btnOpenAuditModal: document.getElementById('btn-open-audit-modal'),
    btnSeedDemo: document.getElementById('btn-seed-demo'),
    btnExportCsv: document.getElementById('btn-export-csv'),
    refreshBtn: document.getElementById('refresh-btn'),
    btnLogout: document.getElementById('btn-logout'),
    engineStatus: document.getElementById('engine-status'),

    // KPI Counters
    metricTotal: document.getElementById('stat-total'),
    metricPending: document.getElementById('stat-pending'),
    metricQualified: document.getElementById('stat-qualified'),
    metricRate: document.getElementById('stat-qual-rate') || document.getElementById('stat-rate'),
    metricInterested: document.getElementById('stat-interested'),
    metricDiscarded: document.getElementById('stat-discarded'),

    // Search & Filter Toolbar
    filterSearchInput: document.getElementById('filter-search-input'),
    searchClearBtn: document.getElementById('search-clear-btn'),
    filterChipsGroup: document.getElementById('filter-chips-group'),
    visibleLeadsCount: document.getElementById('visible-leads-counter') || document.getElementById('visible-leads-count'),

    // Kanban Columns
    colPending: document.getElementById('col-cards-pending'),
    colSent: document.getElementById('col-cards-sent'),
    colInterested: document.getElementById('col-cards-interested'),
    colDiscarded: document.getElementById('col-cards-discarded'),
    countPending: document.getElementById('count-pending'),
    countSent: document.getElementById('count-sent'),
    countInterested: document.getElementById('count-interested'),
    countDiscarded: document.getElementById('count-discarded'),

    // Slide-Over Drawer
    drawerBackdrop: document.getElementById('drawer-backdrop'),
    slideDrawer: document.getElementById('slide-drawer'),
    drawerClose: document.getElementById('drawer-close'),
    drawerTitle: document.getElementById('drawer-lead-name'),
    drawerScore: document.getElementById('drawer-score-badge') || document.getElementById('drawer-lead-score'),
    drawerUrl: document.getElementById('drawer-lead-url'),
    drawerTenant: document.getElementById('drawer-tenant') || document.getElementById('drawer-lead-tenant'),
    drawerStatus: document.getElementById('drawer-status') || document.getElementById('drawer-lead-status'),
    drawerGaps: document.getElementById('drawer-gaps') || document.getElementById('drawer-gaps-list'),
    drawerResearchText: document.getElementById('drawer-research-text'),
    drawerCopy: document.getElementById('drawer-copy') || document.getElementById('drawer-copy-textarea'),
    copyCharCounter: document.getElementById('copy-char-counter'),
    btnCopyOutreach: document.getElementById('btn-copy-outreach'),
    btnWhatsappDirect: document.getElementById('btn-whatsapp-direct'),
    drawerLogsList: document.getElementById('drawer-logs-list'),
    btnDrawerApprove: document.getElementById('btn-drawer-approve') || document.getElementById('btn-approve-lead'),
    btnDrawerReject: document.getElementById('btn-drawer-reject') || document.getElementById('btn-reject-lead'),
    tabLinks: document.querySelectorAll('.tab-link'),
    tabPanes: document.querySelectorAll('.tab-pane'),
    channelRadios: document.querySelectorAll('input[name="dispatch-channel"]'),

    // Live Audit Modal
    modalAudit: document.getElementById('modal-audit'),
    modalAuditClose: document.getElementById('modal-audit-close'),
    modalAuditCancel: document.getElementById('modal-audit-cancel'),
    formLiveAudit: document.getElementById('form-live-audit'),
    auditSector: document.getElementById('audit-sector'),
    auditClinicName: document.getElementById('audit-clinic-name'),
    auditClinicUrl: document.getElementById('audit-clinic-url'),
    auditTenantId: document.getElementById('audit-tenant-id'),
    auditStepper: document.getElementById('audit-stepper'),
    stepperFill: document.getElementById('stepper-fill'),
    stepperLabel: document.getElementById('stepper-label'),
    modalAuditSubmit: document.getElementById('modal-audit-submit'),
    modalPresetBtns: document.querySelectorAll('.modal-preset-btn'),

    // Discard Modal
    modalDiscard: document.getElementById('modal-discard'),
    modalDiscardClose: document.getElementById('modal-discard-close'),
    modalReasonInput: document.getElementById('modal-reason-input'),
    modalCancelBtn: document.getElementById('modal-cancel-btn'),
    modalConfirmBtn: document.getElementById('modal-confirm-btn'),

    // Toast Shelf
    toastContainer: document.getElementById('toast-container'),
  };

  /**
   * Toast notification helper
   */
  function showToast(message, type = 'success') {
    if (!el.toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    el.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(6px)';
      toast.style.transition = 'all 120ms ease';
      setTimeout(() => toast.remove(), 130);
    }, 3200);
  }

  /**
   * Determine score styling class
   */
  function getScoreClass(score) {
    if (score >= 80) return 'score-high';
    if (score >= 65) return 'score-mid';
    return 'score-low';
  }

  /**
   * Helper alias for complete data refresh
   */
  async function refreshAll() {
    await Promise.all([fetchLeads(), fetchStats()]);
  }

  /**
   * Parse microdiagnosis gaps from summary
   */
  function parseGapsFromLead(lead) {
    const gaps = [];
    const summary = lead.research_summary || '';

    if (summary.includes('Sin canal WhatsApp')) {
      gaps.push({
        category: 'CONVERSIÓN INMEDIATA',
        description: 'Ausencia de botón directo de WhatsApp para triaje rápido de citas.',
        impact: 'Alta pérdida de pacientes en tráfico móvil (estimado 25-35%).',
      });
    }
    if (summary.includes('Carece de sistema de cita')) {
      gaps.push({
        category: 'AUTOMATIZACIÓN DE AGENDA',
        description: 'Sin motor de reserva de citas en línea interactivo.',
        impact: 'Fricción en horarios fuera de atención telefónica de recepción.',
      });
    }

    if (gaps.length === 0) {
      gaps.push({
        category: 'OPTIMIZACIÓN DIGITAL',
        description: 'Infraestructura base detectada; oportunidad en secuencias de reactivación de presupuestos.',
        impact: 'Recuperación de pacientes no confirmados.',
      });
    }
    return gaps;
  }

  /**
   * Fetch KPI statistics
   */
  async function fetchStats() {
    try {
      const res = await fetch(`/api/v1/dashboard/stats?tenant_id=${encodeURIComponent(state.tenantId)}`);
      if (!res.ok) throw new Error('Error al consultar estadísticas');
      const data = await res.json();
      state.stats = data;

      if (el.metricTotal) el.metricTotal.textContent = data.total_leads ?? 0;
      if (el.metricPending) el.metricPending.textContent = data.pending_approval_count ?? 0;
      if (el.metricQualified) el.metricQualified.textContent = data.qualified_count ?? 0;
      if (el.metricRate) el.metricRate.textContent = `${data.qualification_rate ?? 0}%`;
      if (el.metricInterested) el.metricInterested.textContent = data.interested_count ?? 0;
      if (el.metricDiscarded) el.metricDiscarded.textContent = data.discarded_count ?? 0;
    } catch (err) {
      console.warn('Stats sync warning:', err.message);
    }
  }

  /**
   * Fetch leads from both database repository and approval store
   */
  async function fetchLeads() {
    state.isLoading = true;
    try {
      const [leadsRes, pendingRes] = await Promise.allSettled([
        fetch(`/api/v1/dashboard/leads?tenant_id=${encodeURIComponent(state.tenantId)}`),
        fetch(`/api/v1/approval/pending?tenant_id=${encodeURIComponent(state.tenantId)}`),
      ]);

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
      applyFilters();
    } catch (err) {
      console.error('Error fetching leads:', err);
      showToast('Error de comunicación con la API de leads', 'error');
    } finally {
      state.isLoading = false;
    }
  }

  /**
   * Apply search query and chip filters
   */
  function applyFilters() {
    const q = state.searchQuery.trim().toLowerCase();
    const filter = state.activeFilter;

    state.filteredLeads = state.leads.filter(lead => {
      // 1. Text Search Filter
      if (q) {
        const nameMatch = (lead.name || '').toLowerCase().includes(q);
        const urlMatch = (lead.url || '').toLowerCase().includes(q);
        const summaryMatch = (lead.research_summary || '').toLowerCase().includes(q);
        if (!nameMatch && !urlMatch && !summaryMatch) return false;
      }

      // 2. Chip Filter
      if (filter === 'high-score') {
        if ((lead.score || 0) < 80) return false;
      } else if (filter === 'no-whatsapp') {
        if (!(lead.research_summary || '').includes('Sin canal WhatsApp')) return false;
      } else if (filter === 'no-booking') {
        if (!(lead.research_summary || '').includes('Carece de sistema de cita')) return false;
      }

      return true;
    });

    if (el.visibleLeadsCount) {
      el.visibleLeadsCount.textContent = state.filteredLeads.length;
    }

    renderKanban();
  }

  /**
   * Render Kanban Columns
   */
  function renderKanban() {
    const buckets = {
      pending: [],
      sent: [],
      interested: [],
      discarded: [],
    };

    state.filteredLeads.forEach(lead => {
      const s = lead.state;
      if (s === 'PENDING_APPROVAL' || s === 'QUALIFIED' || s === 'DRAFTING' || s === 'INGESTED') {
        buckets.pending.push(lead);
      } else if (s === 'SENT' || s === 'APPROVED') {
        buckets.sent.push(lead);
      } else if (s === 'INTERESTED') {
        buckets.interested.push(lead);
      } else {
        buckets.discarded.push(lead);
      }
    });

    // Update Counters
    if (el.countPending) el.countPending.textContent = buckets.pending.length;
    if (el.countSent) el.countSent.textContent = buckets.sent.length;
    if (el.countInterested) el.countInterested.textContent = buckets.interested.length;
    if (el.countDiscarded) el.countDiscarded.textContent = buckets.discarded.length;

    // Render Cards in Each Column
    renderColumn(el.colPending, buckets.pending, true);
    renderColumn(el.colSent, buckets.sent, false);
    renderColumn(el.colInterested, buckets.interested, false);
    renderColumn(el.colDiscarded, buckets.discarded, false);
  }

  /**
   * Helper: Render single Kanban column cards
   */
  function renderColumn(container, leads, isPendingCol) {
    if (!container) return;
    container.innerHTML = '';

    if (leads.length === 0) {
      const emptyDiv = document.createElement('div');
      emptyDiv.className = 'log-meta';
      emptyDiv.style.textAlign = 'center';
      emptyDiv.style.padding = '24px 0';
      emptyDiv.textContent = 'Sin prospectos en esta sección';
      container.appendChild(emptyDiv);
      return;
    }

    leads.forEach(lead => {
      const card = document.createElement('article');
      card.className = 'prospect-card';
      card.dataset.id = lead.id;

      const scoreClass = getScoreClass(lead.score || 0);

      // Extract Micro Tags
      let tagPills = '';
      const summary = lead.research_summary || '';
      const matchServices = summary.match(/(\d+)\s+servicios/i);
      if (matchServices) {
        tagPills += `<span class="tag-pill">${matchServices[0]}</span>`;
      }
      if (summary.includes('Sin canal WhatsApp')) {
        tagPills += `<span class="tag-pill tag-warn">Sin WhatsApp</span>`;
      }
      if (summary.includes('Carece de sistema de cita')) {
        tagPills += `<span class="tag-pill tag-warn">Sin Cita Online</span>`;
      }
      if (!tagPills) {
        tagPills = `<span class="tag-pill">Lead Scored</span>`;
      }

      // Quick Actions for Pending Column
      let quickActionsHtml = '';
      if (isPendingCol) {
        quickActionsHtml = `
          <div class="card-actions">
            <button class="btn btn-card btn-danger quick-reject" data-id="${lead.id}">Descartar</button>
            <button class="btn btn-card btn-success quick-approve" data-id="${lead.id}">Aprobar</button>
          </div>
        `;
      }

      card.innerHTML = `
        <div class="card-top">
          <h4 class="card-title">${escapeHtml(lead.name)}</h4>
          <span class="score-badge ${scoreClass}">${lead.score || 0}</span>
        </div>
        <a class="card-url" href="${escapeHtml(lead.url)}" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation();">
          ${escapeHtml(lead.url)}
        </a>
        <div class="card-tags">
          ${tagPills}
        </div>
        ${quickActionsHtml}
      `;

      // Card click opens inspection drawer
      card.addEventListener('click', (e) => {
        if (e.target.closest('button') || e.target.closest('a')) return;
        openDrawer(lead);
      });

      // Quick Actions Handlers
      if (isPendingCol) {
        const btnApprove = card.querySelector('.quick-approve');
        const btnReject = card.querySelector('.quick-reject');
        if (btnApprove) {
          btnApprove.addEventListener('click', (e) => {
            e.stopPropagation();
            approveLead(lead.id);
          });
        }
        if (btnReject) {
          btnReject.addEventListener('click', (e) => {
            e.stopPropagation();
            openDiscardModal(lead.id);
          });
        }
      }

      container.appendChild(card);
    });
  }

  /**
   * Open Slide-Over Drawer
   */
  function openDrawer(lead) {
    state.selectedLead = lead;

    if (el.drawerTitle) el.drawerTitle.textContent = lead.name;
    if (el.drawerScore) {
      el.drawerScore.textContent = `${lead.score || 0}/100`;
      el.drawerScore.className = `score-pill ${getScoreClass(lead.score || 0)}`;
    }
    if (el.drawerUrl) {
      el.drawerUrl.textContent = lead.url;
      el.drawerUrl.href = lead.url;
    }
    if (el.drawerTenant) el.drawerTenant.textContent = lead.tenant_id;
    if (el.drawerStatus) el.drawerStatus.textContent = lead.state;
    if (el.drawerResearchText) {
      el.drawerResearchText.textContent = lead.research_summary || 'Investigación preliminar en curso...';
    }

    // Render Gaps List
    if (el.drawerGaps) {
      el.drawerGaps.innerHTML = '';
      const gaps = parseGapsFromLead(lead);
      gaps.forEach(g => {
        const gapItem = document.createElement('div');
        gapItem.className = 'gap-item';
        gapItem.innerHTML = `
          <span class="gap-desc"><strong>[${escapeHtml(g.category)}]</strong> ${escapeHtml(g.description)}</span>
          <span class="gap-impact">${escapeHtml(g.impact)}</span>
        `;
        el.drawerGaps.appendChild(gapItem);
      });
    }

    // Render Copywriter Text
    if (el.drawerCopy) {
      el.drawerCopy.value = lead.draft_message || '';
      updateCharCounter();
    }

    // Reset to tab 1
    switchTab('tab-diagnosis');

    // Drawer visibility
    if (el.drawerBackdrop) el.drawerBackdrop.classList.add('active');
    if (el.slideDrawer) el.slideDrawer.classList.add('open');
  }

  /**
   * Close Drawer
   */
  function closeDrawer() {
    state.selectedLead = null;
    if (el.drawerBackdrop) el.drawerBackdrop.classList.remove('active');
    if (el.slideDrawer) el.slideDrawer.classList.remove('open');
  }

  /**
   * Switch Drawer Tabs
   */
  function switchTab(targetTabId) {
    state.activeTab = targetTabId;

    el.tabLinks.forEach(link => {
      if (link.dataset.tab === targetTabId) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    el.tabPanes.forEach(pane => {
      if (pane.id === targetTabId) {
        pane.classList.add('active');
      } else {
        pane.classList.remove('active');
      }
    });

    if (targetTabId === 'tab-audit-logs' && state.selectedLead) {
      fetchAuditLogs(state.selectedLead.id);
    }
  }

  /**
   * Fetch Audit Logs for the Lead
   */
  async function fetchAuditLogs(leadId) {
    if (!el.drawerLogsList) return;
    el.drawerLogsList.innerHTML = '<div class="log-meta">Consultando registros inmutables...</div>';

    try {
      const res = await fetch(`/api/v1/audit/logs?tenant_id=${encodeURIComponent(state.tenantId)}&lead_id=${encodeURIComponent(leadId)}`);
      if (!res.ok) throw new Error('No se pudieron recuperar los registros');
      const logs = await res.json();

      el.drawerLogsList.innerHTML = '';
      if (logs.length === 0) {
        el.drawerLogsList.innerHTML = '<div class="log-meta">Sin eventos de auditoría previos registrados.</div>';
        return;
      }

      logs.forEach(item => {
        const row = document.createElement('div');
        row.className = 'log-entry';
        const dateStr = item.timestamp ? new Date(item.timestamp).toLocaleString() : 'Reciente';
        row.innerHTML = `
          <div class="log-meta">
            <span class="log-action">${escapeHtml(item.action)}</span>
            <span>${escapeHtml(dateStr)} · Actor: ${escapeHtml(item.actor)}</span>
          </div>
          <div class="log-text">${escapeHtml(item.reason || 'Acción de ciclo ejecutada.')}</div>
        `;
        el.drawerLogsList.appendChild(row);
      });
    } catch (err) {
      el.drawerLogsList.innerHTML = `<div class="log-meta text-crimson">Error: ${escapeHtml(err.message)}</div>`;
    }
  }

  /**
   * Update character counter in copy editor
   */
  function updateCharCounter() {
    if (!el.drawerCopy || !el.copyCharCounter) return;
    const len = el.drawerCopy.value.length;
    el.copyCharCounter.textContent = `${len.toLocaleString()} caracteres`;
  }

  /**
   * Approve Lead Action
   */
  async function approveLead(leadId) {
    try {
      const res = await fetch('/api/v1/approval/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: state.tenantId,
          lead_id: leadId,
          action: 'APPROVE',
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Fallo en la aprobación');
      }

      showToast('Prospecto aprobado y programado para despacho');
      closeDrawer();
      await fetchLeads();
      await fetchStats();
    } catch (err) {
      showToast(`Error al aprobar: ${err.message}`, 'error');
    }
  }

  /**
   * Open Discard Modal
   */
  function openDiscardModal(leadId) {
    state.discardTargetLeadId = leadId;
    if (el.modalReasonInput) el.modalReasonInput.value = '';
    if (el.modalDiscard) el.modalDiscard.classList.add('active');
  }

  /**
   * Close Discard Modal
   */
  function closeDiscardModal() {
    state.discardTargetLeadId = null;
    if (el.modalDiscard) el.modalDiscard.classList.remove('active');
  }

  /**
   * Confirm Discard Action
   */
  async function confirmDiscardLead() {
    const leadId = state.discardTargetLeadId;
    if (!leadId) return;

    const reason = el.modalReasonInput ? el.modalReasonInput.value.trim() : '';

    try {
      const res = await fetch('/api/v1/approval/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: state.tenantId,
          lead_id: leadId,
          action: 'REJECT',
          reason: reason || 'Descartado por operador en revisión manual.',
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Error al descartar prospecto');
      }

      showToast('Prospecto descartado y registrado en auditoría');
      closeDiscardModal();
      closeDrawer();
      await fetchLeads();
      await fetchStats();
    } catch (err) {
      showToast(`Error al descartar: ${err.message}`, 'error');
    }
  }

  /**
   * Live Audit Submission & Stepper Progress
   */
  async function handleLiveAudit(e) {
    e.preventDefault();
    const name = el.auditClinicName.value.trim();
    const url = el.auditClinicUrl.value.trim();
    const tenant = el.auditTenantId.value;
    const sector = el.auditSector ? el.auditSector.value : 'clinicas';

    if (!name || !url) {
      showToast('Por favor complete el nombre y URL de la empresa', 'error');
      return;
    }

    // Prepare Stepper UI
    if (el.auditStepper) el.auditStepper.style.display = 'flex';
    if (el.modalAuditSubmit) el.modalAuditSubmit.disabled = true;

    const updateStep = (pct, label) => {
      if (el.stepperFill) el.stepperFill.style.width = `${pct}%`;
      if (el.stepperLabel) el.stepperLabel.textContent = label;
    };

    updateStep(15, `1/5. Validando URL y cargando reglas del sector [${sector.toUpperCase()}]...`);

    try {
      const timer1 = setTimeout(() => updateStep(40, '2/5. Scraper Zero-Trust extrayendo DOM y sanitizando PII...'), 800);
      const timer2 = setTimeout(() => updateStep(65, '3/5. ResearchAgent analizando servicios y canales...'), 1600);
      const timer3 = setTimeout(() => updateStep(85, '4/5. CommercialAudit y Scoring calculando brechas...'), 2400);

      const res = await fetch('/api/v1/prospects/audit-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: tenant,
          name: name,
          url: url,
          sector: sector,
        }),
      });

      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Error HTTP ${res.status}`);
      }

      const data = await res.json();
      updateStep(100, '5/5. Auditoría completada. Guardando en PostgreSQL...');

      setTimeout(async () => {
        closeAuditModal();
        showToast(`Auditoría completada para "${name}". Score: ${data.prospect.score}/100`);

        // If target tenant is current, refresh; else switch to that tenant
        if (state.tenantId !== tenant) {
          state.tenantId = tenant;
          if (el.tenantSelect) el.tenantSelect.value = tenant;
          localStorage.setItem('revops_tenant', tenant);
        }

        await fetchLeads();
        await fetchStats();

        // Highlight/Open lead immediately
        if (data.prospect) {
          openDrawer(data.prospect);
        }
      }, 500);

    } catch (err) {
      updateStep(0, `Fallo en auditoría: ${err.message}`);
      showToast(`Error en auditoría en vivo: ${err.message}`, 'error');
      if (el.modalAuditSubmit) el.modalAuditSubmit.disabled = false;
    }
  }

  /**
   * Seed Demo Data for Current Tenant
   */
  async function seedDemoTenant() {
    if (el.btnSeedDemo) el.btnSeedDemo.disabled = true;
    try {
      const res = await fetch(`/api/v1/dashboard/seed?tenant_id=${encodeURIComponent(state.tenantId)}`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('No se pudo poblar el tenant');
      const data = await res.json();
      await Promise.all([fetchLeads(), fetchStats()]);
      showToast(`Cargados ${data.seeded_count} prospectos de demostración en ${state.tenantId}`);
    } catch (err) {
      showToast(`Error al cargar demo: ${err.message}`, 'error');
    } finally {
      if (el.btnSeedDemo) el.btnSeedDemo.disabled = false;
    }
  }

  function openAuditModal() {
    if (el.modalAudit) el.modalAudit.classList.add('active');
    if (el.auditStepper) el.auditStepper.style.display = 'none';
    if (el.modalAuditSubmit) el.modalAuditSubmit.disabled = false;
    if (el.auditTenantId) el.auditTenantId.value = state.tenantId;
    if (el.auditClinicName) el.auditClinicName.focus();
  }

  function closeAuditModal() {
    if (el.modalAudit) el.modalAudit.classList.remove('active');
  }

  /**
   * Export Visible Pipeline to CSV
   */
  function exportPipelineCsv() {
    if (state.filteredLeads.length === 0) {
      showToast('No hay prospectos para exportar con los filtros actuales', 'error');
      return;
    }

    const headers = ['ID', 'Nombre', 'URL', 'Tenant', 'Estado', 'Score', 'Resumen_Investigacion', 'Propuesta_Outreach'];
    const rows = state.filteredLeads.map(l => [
      l.id,
      `"${(l.name || '').replace(/"/g, '""')}"`,
      `"${(l.url || '').replace(/"/g, '""')}"`,
      l.tenant_id,
      l.state,
      l.score || 0,
      `"${(l.research_summary || '').replace(/"/g, '""')}"`,
      `"${(l.draft_message || '').replace(/"/g, '""')}"`,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `revops_pipeline_${state.tenantId}_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast(`Exportados ${state.filteredLeads.length} prospectos a CSV`);
  }

  /**
   * Utility to escape HTML entities
   */
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /**
   * Bind DOM Events
   */
  /**
   * Bind DOM Events
   */
  function bindEvents() {
    // Tenant Custom Selector Setup
    const customDropdown = document.getElementById('tenant-custom-dropdown');
    const triggerBtn = document.getElementById('tenant-select-btn');
    const triggerLabel = document.getElementById('tenant-select-label');
    const options = document.querySelectorAll('.custom-select-option');

    function updateDropdownDisplay(val) {
      let matchedLabel = '';
      options.forEach(opt => {
        if (opt.getAttribute('data-value') === val) {
          opt.classList.add('selected');
          matchedLabel = opt.textContent.trim();
        } else {
          opt.classList.remove('selected');
        }
      });
      if (triggerLabel && matchedLabel) {
        triggerLabel.textContent = matchedLabel;
      }
      return matchedLabel;
    }

    if (triggerBtn && customDropdown) {
      // Set initial selection
      updateDropdownDisplay(state.tenantId);

      triggerBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = customDropdown.classList.contains('active');
        customDropdown.classList.toggle('active', !isOpen);
        triggerBtn.setAttribute('aria-expanded', !isOpen);
      });

      options.forEach(opt => {
        opt.addEventListener('click', async (e) => {
          e.stopPropagation();
          const newVal = opt.getAttribute('data-value');
          if (newVal === state.tenantId) {
            customDropdown.classList.remove('active');
            triggerBtn.setAttribute('aria-expanded', 'false');
            return;
          }

          state.tenantId = newVal;
          localStorage.setItem('revops_tenant', state.tenantId);
          const friendlyName = updateDropdownDisplay(state.tenantId);

          if (el.tenantSelect) {
            el.tenantSelect.value = state.tenantId;
          }

          customDropdown.classList.remove('active');
          triggerBtn.setAttribute('aria-expanded', 'false');

          showToast(`Unidad activa: ${friendlyName || state.tenantId}`);
          await fetchLeads();
          await fetchStats();
        });
      });

      // Close dropdown if clicked outside or Escape
      document.addEventListener('click', (e) => {
        if (!customDropdown.contains(e.target)) {
          customDropdown.classList.remove('active');
          triggerBtn.setAttribute('aria-expanded', 'false');
        }
      });

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && customDropdown.classList.contains('active')) {
          customDropdown.classList.remove('active');
          triggerBtn.setAttribute('aria-expanded', 'false');
          triggerBtn.focus();
        }
      });
    }

    // Native Fallback / Programmatic Tenant Selector
    if (el.tenantSelect) {
      el.tenantSelect.value = state.tenantId;
      el.tenantSelect.addEventListener('change', async (e) => {
        state.tenantId = e.target.value;
        localStorage.setItem('revops_tenant', state.tenantId);
        const friendlyName = updateDropdownDisplay(state.tenantId);
        showToast(`Unidad activa: ${friendlyName || state.tenantId}`);
        await fetchLeads();
        await fetchStats();
      });
    }

    // Refresh Button
    if (el.refreshBtn) {
      el.refreshBtn.addEventListener('click', async () => {
        el.refreshBtn.disabled = true;
        await Promise.all([fetchLeads(), fetchStats()]);
        el.refreshBtn.disabled = false;
        showToast('Datos actualizados');
      });
    }

    // Logout Button
    if (el.btnLogout) {
      el.btnLogout.addEventListener('click', async () => {
        try {
          await fetch('/api/v1/auth/logout', { method: 'POST' });
        } catch (_) {
          // ignore network error
        }
        window.location.href = '/login';
      });
    }

    // Search and Filter Toolbar
    if (el.filterSearchInput) {
      el.filterSearchInput.addEventListener('input', (e) => {
        state.searchQuery = e.target.value;
        if (el.searchClearBtn) {
          el.searchClearBtn.style.display = state.searchQuery ? 'block' : 'none';
        }
        applyFilters();
      });
    }

    if (el.searchClearBtn) {
      el.searchClearBtn.addEventListener('click', () => {
        state.searchQuery = '';
        if (el.filterSearchInput) el.filterSearchInput.value = '';
        el.searchClearBtn.style.display = 'none';
        applyFilters();
      });
    }

    if (el.filterChipsGroup) {
      el.filterChipsGroup.addEventListener('click', (e) => {
        const btn = e.target.closest('.chip-btn');
        if (!btn) return;
        el.filterChipsGroup.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeFilter = btn.dataset.filter;
        applyFilters();
      });
    }

    // Live Audit Modal Controls
    if (el.btnOpenAuditModal) el.btnOpenAuditModal.addEventListener('click', openAuditModal);
    if (el.modalAuditClose) el.modalAuditClose.addEventListener('click', closeAuditModal);
    if (el.modalAuditCancel) el.modalAuditCancel.addEventListener('click', closeAuditModal);
    if (el.formLiveAudit) el.formLiveAudit.addEventListener('submit', handleLiveAudit);

    if (el.modalPresetBtns) {
      el.modalPresetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
          if (el.auditClinicName) el.auditClinicName.value = btn.dataset.name || '';
          if (el.auditClinicUrl) el.auditClinicUrl.value = btn.dataset.url || '';
          if (el.auditSector && btn.dataset.sector) el.auditSector.value = btn.dataset.sector;
          showToast(`Caso cargado: ${btn.dataset.name}`);
        });
      });
    }

    // Seed Demo Tenant Data
    if (el.btnSeedDemo) el.btnSeedDemo.addEventListener('click', seedDemoTenant);

    // Export CSV
    if (el.btnExportCsv) el.btnExportCsv.addEventListener('click', exportPipelineCsv);

    // Copy Outreach & Direct WhatsApp Dispatch inside Drawer
    if (el.btnCopyOutreach) {
      el.btnCopyOutreach.addEventListener('click', async () => {
        const text = el.drawerCopy ? el.drawerCopy.value.trim() : '';
        if (!text) {
          showToast('No hay propuesta redactada para copiar', 'error');
          return;
        }
        try {
          await navigator.clipboard.writeText(text);
          showToast('Propuesta copiada al portapapeles');
        } catch (_) {
          if (el.drawerCopy) {
            el.drawerCopy.select();
            document.execCommand('copy');
            showToast('Propuesta copiada al portapapeles');
          }
        }
      });
    }

    if (el.btnWhatsappDirect) {
      el.btnWhatsappDirect.addEventListener('click', () => {
        const text = el.drawerCopy ? el.drawerCopy.value.trim() : '';
        if (!text) {
          showToast('No hay propuesta para enviar por WhatsApp', 'error');
          return;
        }
        const encoded = encodeURIComponent(text);
        window.open(`https://wa.me/?text=${encoded}`, '_blank', 'noopener');
        showToast('Abriendo WhatsApp con la propuesta lista para enviar');
      });
    }

    // Slide-Over Drawer Controls
    if (el.drawerClose) el.drawerClose.addEventListener('click', closeDrawer);
    if (el.drawerBackdrop) el.drawerBackdrop.addEventListener('click', closeDrawer);

    el.tabLinks.forEach(link => {
      link.addEventListener('click', () => switchTab(link.dataset.tab));
    });

    if (el.drawerCopy) {
      el.drawerCopy.addEventListener('input', () => {
        updateCharCounter();
        if (state.selectedLead) {
          state.selectedLead.draft_message = el.drawerCopy.value;
        }
      });
    }

    el.channelRadios.forEach(radio => {
      radio.addEventListener('change', (e) => {
        state.activeChannel = e.target.value;
        showToast(`Canal de despacho fijado a: ${state.activeChannel.toUpperCase()}`);
      });
    });

    if (el.btnDrawerApprove) {
      el.btnDrawerApprove.addEventListener('click', () => {
        if (state.selectedLead) approveLead(state.selectedLead.id);
      });
    }

    if (el.btnDrawerReject) {
      el.btnDrawerReject.addEventListener('click', () => {
        if (state.selectedLead) openDiscardModal(state.selectedLead.id);
      });
    }

    // Discard Modal Controls
    if (el.modalDiscardClose) el.modalDiscardClose.addEventListener('click', closeDiscardModal);
    if (el.modalCancelBtn) el.modalCancelBtn.addEventListener('click', closeDiscardModal);
    if (el.modalConfirmBtn) el.modalConfirmBtn.addEventListener('click', confirmDiscardLead);

    // Keyboard Shortcuts (Esc closes panels)
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeDrawer();
        closeAuditModal();
        closeDiscardModal();
      }
    });
  }

  /**
   * Application Bootstrapping
   */
  async function init() {
    bindEvents();
    await Promise.all([fetchLeads(), fetchStats()]);
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
