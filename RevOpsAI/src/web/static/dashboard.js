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
    activeCity: 'all',
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
    btnClearDemo: document.getElementById('btn-clear-demo'),
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
    cityChipsGroup: document.getElementById('city-chips-group'),
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
    drawerContactName: document.getElementById('drawer-contact-name'),
    drawerContactPhone: document.getElementById('drawer-contact-phone'),
    btnSaveContactInfo: document.getElementById('btn-save-contact-info'),
    contactSaveStatus: document.getElementById('contact-save-status'),
    drawerCityInput: document.getElementById('drawer-city-input'),
    drawerFollowupSelect: document.getElementById('drawer-followup-select'),
    drawerInternalNotes: document.getElementById('drawer-internal-notes'),
    btnSaveNotes: document.getElementById('btn-save-notes'),
    notesSaveStatus: document.getElementById('notes-save-status'),
    drawerLogsList: document.getElementById('drawer-logs-list'),
    btnDrawerApprove: document.getElementById('btn-drawer-approve') || document.getElementById('btn-approve-lead'),
    btnDrawerReject: document.getElementById('btn-drawer-reject') || document.getElementById('btn-reject-lead'),
    tabLinks: document.querySelectorAll('.tab-link'),
    tabPanes: document.querySelectorAll('.tab-pane'),
    channelRadios: document.querySelectorAll('input[name="dispatch-channel"]'),

    // Autonomous Scout Bot Modal Cache
    btnOpenAutoModal: document.getElementById('btn-open-auto-modal'),
    modalAutoScout: document.getElementById('modal-auto-scout'),
    modalScoutClose: document.getElementById('modal-scout-close'),
    modalScoutCancel: document.getElementById('modal-scout-cancel'),
    formAutoScout: document.getElementById('form-auto-scout'),
    scoutCity: document.getElementById('scout-city'),
    scoutSector: document.getElementById('scout-sector'),
    scoutLimit: document.getElementById('scout-limit'),
    scoutTenant: document.getElementById('scout-tenant'),
    scoutStepper: document.getElementById('scout-stepper'),
    scoutStepperFill: document.getElementById('scout-stepper-fill'),
    scoutStepperLabel: document.getElementById('scout-stepper-label'),
    modalScoutSubmit: document.getElementById('modal-scout-submit'),

    // Batch Audit Modal
    btnOpenBatchModal: document.getElementById('btn-open-batch-modal'),
    modalBatchAudit: document.getElementById('modal-batch-audit'),
    modalBatchClose: document.getElementById('modal-batch-close'),
    modalBatchCancel: document.getElementById('modal-batch-cancel'),
    formBatchAudit: document.getElementById('form-batch-audit'),
    batchAuditSector: document.getElementById('batch-audit-sector'),
    batchAuditTenant: document.getElementById('batch-audit-tenant'),
    batchUrlsInput: document.getElementById('batch-urls-input'),
    batchStepper: document.getElementById('batch-stepper'),
    batchStepperFill: document.getElementById('batch-stepper-fill'),
    batchStepperLabel: document.getElementById('batch-stepper-label'),
    modalBatchSubmit: document.getElementById('modal-batch-submit'),

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

      updateTelemetryCharts();
    } catch (err) {
      console.warn('Stats sync warning:', err.message);
    }
  }

  /**
   * Update Real-Time Operational Telemetry Charts
   */
  function updateTelemetryCharts() {
    const leads = state.leads || [];
    const total = state.stats.total_leads || leads.length || 0;
    const qualified = state.stats.qualified_count || 0;
    const sent = (state.stats.total_leads ? (leads.filter(l => l.state === 'SENT' || l.state === 'APPROVED').length) : 0);
    const interested = state.stats.interested_count || 0;

    // 1. Funnel Bars
    const fTotalVal = document.getElementById('funnel-val-total');
    const fQualVal = document.getElementById('funnel-val-qual');
    const fSentVal = document.getElementById('funnel-val-sent');
    const fInterVal = document.getElementById('funnel-val-inter');

    const fBarTotal = document.getElementById('funnel-bar-total');
    const fBarQual = document.getElementById('funnel-bar-qual');
    const fBarSent = document.getElementById('funnel-bar-sent');
    const fBarInter = document.getElementById('funnel-bar-inter');

    if (fTotalVal) fTotalVal.textContent = total;
    if (fQualVal) fQualVal.textContent = `${qualified} (${total > 0 ? Math.round((qualified / total) * 100) : 0}%)`;
    if (fSentVal) fSentVal.textContent = `${sent} (${total > 0 ? Math.round((sent / total) * 100) : 0}%)`;
    if (fInterVal) fInterVal.textContent = `${interested} (${total > 0 ? Math.round((interested / total) * 100) : 0}%)`;

    if (fBarTotal) fBarTotal.style.width = '100%';
    if (fBarQual) fBarQual.style.width = total > 0 ? `${Math.min(100, Math.round((qualified / total) * 100))}%` : '0%';
    if (fBarSent) fBarSent.style.width = total > 0 ? `${Math.min(100, Math.round((sent / total) * 100))}%` : '0%';
    if (fBarInter) fBarInter.style.width = total > 0 ? `${Math.min(100, Math.round((interested / total) * 100))}%` : '0%';

    // 2. Gaps & Audit Heatmap
    const telAudited = document.getElementById('telemetry-audited-units');
    if (telAudited) telAudited.textContent = `${leads.length} entidades analizadas`;

    let waGaps = 0;
    let bookingGaps = 0;
    leads.forEach(l => {
      const summary = l.research_summary || '';
      if (summary.includes('Sin canal WhatsApp') || summary.includes('WhatsApp')) waGaps++;
      if (summary.includes('Carece de sistema de cita') || summary.includes('agendamiento') || summary.includes('cita online')) bookingGaps++;
    });

    const waPct = leads.length > 0 ? Math.round((waGaps / leads.length) * 100) : 0;
    const bookingPct = leads.length > 0 ? Math.round((bookingGaps / leads.length) * 100) : 0;

    const gapPctWa = document.getElementById('gap-pct-wa');
    const gapBarWa = document.getElementById('gap-bar-wa');
    const gapPctBooking = document.getElementById('gap-pct-booking');
    const gapBarBooking = document.getElementById('gap-bar-booking');

    if (gapPctWa) gapPctWa.textContent = `${waPct}% (${waGaps})`;
    if (gapBarWa) gapBarWa.style.width = `${waPct}%`;
    if (gapPctBooking) gapPctBooking.textContent = `${bookingPct}% (${bookingGaps})`;
    if (gapBarBooking) gapBarBooking.style.width = `${bookingPct}%`;

    // 3. Score Spectrum Histogram
    let high = 0;
    let mid = 0;
    let low = 0;

    leads.forEach(l => {
      const s = l.score || 0;
      if (s >= 80) high++;
      else if (s >= 65) mid++;
      else low++;
    });

    const maxCount = Math.max(high, mid, low, 1);

    const specCountHigh = document.getElementById('spec-count-high');
    const specCountMid = document.getElementById('spec-count-mid');
    const specCountLow = document.getElementById('spec-count-low');

    const specBarHigh = document.getElementById('spec-bar-high');
    const specBarMid = document.getElementById('spec-bar-mid');
    const specBarLow = document.getElementById('spec-bar-low');

    if (specCountHigh) specCountHigh.textContent = high;
    if (specCountMid) specCountMid.textContent = mid;
    if (specCountLow) specCountLow.textContent = low;

    if (specBarHigh) specBarHigh.style.height = `${Math.round((high / maxCount) * 100)}%`;
    if (specBarMid) specBarMid.style.height = `${Math.round((mid / maxCount) * 100)}%`;
    if (specBarLow) specBarLow.style.height = `${Math.round((low / maxCount) * 100)}%`;
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
      updateTelemetryCharts();
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

      // 3. City / Territory Filter
      if (state.activeCity && state.activeCity !== 'all') {
        const leadCity = (lead.city || '').toLowerCase();
        const targetCity = state.activeCity.toLowerCase();
        if (!leadCity.includes(targetCity)) return false;
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
      if (lead.city) {
        tagPills += `<span class="tag-pill tag-city">${escapeHtml(lead.city)}</span>`;
      }
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
      if (lead.state === 'SENT' || lead.state === 'APPROVED') {
        const day = lead.followup_day || 1;
        const bumpLabel = day >= 7 ? 'Día 7 (Cierre)' : (day >= 3 ? 'Día 3 (Bump)' : 'Día 1');
        tagPills += `<span class="tag-pill tag-cadence">${bumpLabel}</span>`;
      }
      if (!tagPills) {
        tagPills = `<span class="tag-pill">Lead Scored</span>`;
      }

      // Quick Actions for Pending Column & Follow-Up Column
      let quickActionsHtml = '';
      if (isPendingCol) {
        quickActionsHtml = `
          <div class="card-actions">
            <button class="btn btn-card btn-danger quick-reject" data-id="${lead.id}">Descartar</button>
            <button class="btn btn-card btn-success quick-approve" data-id="${lead.id}">Aprobar</button>
          </div>
        `;
      } else if (lead.state === 'SENT' || lead.state === 'APPROVED') {
        quickActionsHtml = `
          <div class="card-actions card-actions-single">
            <button class="btn btn-card btn-interested quick-mark-interested" data-id="${lead.id}">Marcar Interesado</button>
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
      } else {
        const btnInterested = card.querySelector('.quick-mark-interested');
        if (btnInterested) {
          btnInterested.addEventListener('click', (e) => {
            e.stopPropagation();
            markLeadInterested(lead.id);
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

    // Render Copywriter Text & Contact Info
    if (el.drawerCopy) {
      el.drawerCopy.value = lead.draft_message || '';
      updateCharCounter();
    }
    if (el.drawerContactName) {
      el.drawerContactName.value = lead.contact_name || '';
    }
    if (el.drawerContactPhone) {
      el.drawerContactPhone.value = lead.contact_phone || '';
    }
    if (el.contactSaveStatus) {
      el.contactSaveStatus.textContent = '';
    }

    // Render Internal Notes & Cadence
    if (el.drawerCityInput) {
      el.drawerCityInput.value = lead.city || '';
    }
    if (el.drawerFollowupSelect) {
      el.drawerFollowupSelect.value = String(lead.followup_day || 1);
    }
    if (el.drawerInternalNotes) {
      el.drawerInternalNotes.value = lead.internal_notes || '';
    }
    if (el.notesSaveStatus) {
      el.notesSaveStatus.textContent = '';
    }

    // Discard & Approve button visibility in Drawer based on state
    if (el.btnDrawerReject) {
      el.btnDrawerReject.style.display = (lead.state === 'DISCARDED') ? 'none' : 'inline-flex';
    }
    if (el.btnDrawerApprove) {
      el.btnDrawerApprove.style.display = (lead.state === 'DISCARDED') ? 'none' : 'inline-flex';
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
   * Save Contact Details (Name, Phone, Copy)
   */
  async function saveContactInfo() {
    if (!state.selectedLead) return;
    const leadId = state.selectedLead.id;
    const contactName = el.drawerContactName ? el.drawerContactName.value.trim() : '';
    const contactPhone = el.drawerContactPhone ? el.drawerContactPhone.value.trim() : '';
    const draftMessage = el.drawerCopy ? el.drawerCopy.value : '';

    if (el.btnSaveContactInfo) el.btnSaveContactInfo.disabled = true;
    if (el.contactSaveStatus) el.contactSaveStatus.textContent = 'Guardando…';

    try {
      const res = await fetch(`/api/v1/prospects/${encodeURIComponent(leadId)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: state.tenantId,
          contact_name: contactName,
          contact_phone: contactPhone,
          draft_message: draftMessage,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Fallo al actualizar contacto');
      }

      const updated = await res.json();
      state.selectedLead.contact_name = updated.contact_name;
      state.selectedLead.contact_phone = updated.contact_phone;
      state.selectedLead.draft_message = updated.draft_message;

      // Update in local state
      const targetInState = state.leads.find(l => l.id === leadId);
      if (targetInState) {
        targetInState.contact_name = updated.contact_name;
        targetInState.contact_phone = updated.contact_phone;
        targetInState.draft_message = updated.draft_message;
      }

      if (el.contactSaveStatus) el.contactSaveStatus.textContent = 'Guardado ✓';
      showToast('Datos de contacto actualizados correctamente');
      setTimeout(() => {
        if (el.contactSaveStatus) el.contactSaveStatus.textContent = '';
      }, 2500);
    } catch (err) {
      if (el.contactSaveStatus) el.contactSaveStatus.textContent = 'Error';
      showToast(`Error al guardar: ${err.message}`, 'error');
    } finally {
      if (el.btnSaveContactInfo) el.btnSaveContactInfo.disabled = false;
    }
  }

  /**
   * Save Lead Internal Notes and Follow-up Cadence
   */
  async function saveLeadNotes() {
    if (!state.selectedLead) return;
    const leadId = state.selectedLead.id;
    const notes = el.drawerInternalNotes ? el.drawerInternalNotes.value : '';
    const city = el.drawerCityInput ? el.drawerCityInput.value.trim() : '';
    const followupDay = el.drawerFollowupSelect ? parseInt(el.drawerFollowupSelect.value, 10) : 1;

    if (el.btnSaveNotes) el.btnSaveNotes.disabled = true;
    if (el.notesSaveStatus) el.notesSaveStatus.textContent = 'Guardando...';

    try {
      const res = await fetch(`/api/v1/prospects/${encodeURIComponent(leadId)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: state.tenantId,
          internal_notes: notes,
          city: city,
          followup_day: followupDay,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Fallo al actualizar notas');
      }

      const updated = await res.json();
      state.selectedLead.internal_notes = updated.internal_notes;
      state.selectedLead.city = updated.city;
      state.selectedLead.followup_day = updated.followup_day;

      const targetInState = state.leads.find(l => l.id === leadId);
      if (targetInState) {
        targetInState.internal_notes = updated.internal_notes;
        targetInState.city = updated.city;
        targetInState.followup_day = updated.followup_day;
      }

      if (el.notesSaveStatus) el.notesSaveStatus.textContent = 'Guardado ✓';
      showToast('Notas internas y cadencia actualizadas');
      renderKanban();
      setTimeout(() => {
        if (el.notesSaveStatus) el.notesSaveStatus.textContent = '';
      }, 2500);
    } catch (err) {
      if (el.notesSaveStatus) el.notesSaveStatus.textContent = 'Error';
      showToast(`Error al guardar notas: ${err.message}`, 'error');
    } finally {
      if (el.btnSaveNotes) el.btnSaveNotes.disabled = false;
    }
  }

  /**
   * Mark Lead as Interested Action (One-click state progression)
   */
  async function markLeadInterested(leadId) {
    try {
      const res = await fetch('/api/v1/approval/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: state.tenantId,
          lead_id: leadId,
          action: 'MARK_INTERESTED',
          reason: 'Oportunidad confirmada por operador comercial',
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Fallo en la transición');
      }

      showToast('Prospecto marcado como INTERESADO ✓');
      closeDrawer();
      await fetchLeads();
      await fetchStats();
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
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
    const lead = state.leads.find(l => l.id === leadId) || state.selectedLead;
    if (lead && lead.state === 'DISCARDED') {
      showToast('Este prospecto ya se encuentra descartado', 'info');
      return;
    }
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

  /**
   * Clear Demo Data for Current Tenant
   */
  async function clearDemoTenant() {
    if (!confirm('¿Deseas vaciar y desactivar los datos de prueba en esta unidad de negocio? La bandeja quedará limpia.')) {
      return;
    }
    if (el.btnClearDemo) el.btnClearDemo.disabled = true;
    try {
      const res = await fetch(`/api/v1/dashboard/clear?tenant_id=${encodeURIComponent(state.tenantId)}`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('No se pudo limpiar el tenant');
      const data = await res.json();
      closeDrawer();
      await Promise.all([fetchLeads(), fetchStats()]);
      showToast(`Datos de prueba desactivados (${data.deleted_count} prospectos removidos)`);
    } catch (err) {
      showToast(`Error al limpiar datos: ${err.message}`, 'error');
    } finally {
      if (el.btnClearDemo) el.btnClearDemo.disabled = false;
    }
  }

  function openAutoScoutModal() {
    if (el.modalAutoScout) el.modalAutoScout.classList.add('active');
    if (el.scoutStepper) el.scoutStepper.style.display = 'none';
    if (el.modalScoutSubmit) el.modalScoutSubmit.disabled = false;
    if (el.scoutTenant) el.scoutTenant.value = state.tenantId;
  }

  function closeAutoScoutModal() {
    if (el.modalAutoScout) el.modalAutoScout.classList.remove('active');
  }

  /**
   * Handle Autonomous Scout Bot Execution
   */
  async function handleAutoScout(e) {
    e.preventDefault();
    const city = el.scoutCity ? el.scoutCity.value : 'Montería';
    const sector = el.scoutSector ? el.scoutSector.value : 'clinicas';
    const limit = el.scoutLimit ? parseInt(el.scoutLimit.value, 10) : 5;
    const tenant = el.scoutTenant ? el.scoutTenant.value : state.tenantId;

    if (el.scoutStepper) el.scoutStepper.style.display = 'grid';
    if (el.modalScoutSubmit) el.modalScoutSubmit.disabled = true;

    if (el.scoutStepperFill) el.scoutStepperFill.style.width = '30%';
    if (el.scoutStepperLabel) el.scoutStepperLabel.textContent = `1/3. Rastreando empresas en ${city} para [${sector.toUpperCase()}]...`;

    try {
      const stepTimer1 = setTimeout(() => {
        if (el.scoutStepperFill) el.scoutStepperFill.style.width = '65%';
        if (el.scoutStepperLabel) el.scoutStepperLabel.textContent = `2/3. Extrayendo sitios web y evaluando brechas digitales...`;
      }, 1200);

      const res = await fetch('/api/v1/prospecting/auto-discover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: tenant,
          city: city,
          sector: sector,
          limit: limit,
        }),
      });

      clearTimeout(stepTimer1);

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Fallo en la prospección autónoma');
      }

      const data = await res.json();
      if (el.scoutStepperFill) el.scoutStepperFill.style.width = '100%';
      if (el.scoutStepperLabel) el.scoutStepperLabel.textContent = `3/3. Descubrimiento completado: ${data.audited_count} prospectos generados en ${city}.`;

      setTimeout(async () => {
        closeAutoScoutModal();
        showToast(`Bot autónomo: ${data.audited_count} empresas auditadas en ${city}`);

        if (state.tenantId !== tenant) {
          state.tenantId = tenant;
          if (el.tenantSelect) el.tenantSelect.value = tenant;
          localStorage.setItem('revops_tenant', tenant);
        }

        await fetchLeads();
        await fetchStats();
      }, 800);
    } catch (err) {
      if (el.scoutStepperLabel) el.scoutStepperLabel.textContent = `Error: ${err.message}`;
      showToast(`Error en bot: ${err.message}`, 'error');
      if (el.modalScoutSubmit) el.modalScoutSubmit.disabled = false;
    }
  }

  function openBatchModal() {
    if (el.modalBatchAudit) el.modalBatchAudit.classList.add('active');
    if (el.batchStepper) el.batchStepper.style.display = 'none';
    if (el.modalBatchSubmit) el.modalBatchSubmit.disabled = false;
    if (el.batchAuditTenant) el.batchAuditTenant.value = state.tenantId;
    if (el.batchUrlsInput) {
      el.batchUrlsInput.value = '';
      el.batchUrlsInput.focus();
    }
  }

  function closeBatchModal() {
    if (el.modalBatchAudit) el.modalBatchAudit.classList.remove('active');
  }

  /**
   * Handle Batch Audit Submission
   */
  async function handleBatchAudit(e) {
    e.preventDefault();
    const rawUrls = el.batchUrlsInput ? el.batchUrlsInput.value : '';
    const sector = el.batchAuditSector ? el.batchAuditSector.value : 'clinicas';
    const tenant = el.batchAuditTenant ? el.batchAuditTenant.value : state.tenantId;

    const urls = rawUrls
      .split('\n')
      .map(u => u.trim())
      .filter(u => u.length > 0);

    if (urls.length === 0) {
      showToast('Ingresa al menos una URL para auditar', 'error');
      return;
    }
    if (urls.length > 20) {
      showToast('Máximo 20 URLs por lote de auditoría', 'error');
      return;
    }

    if (el.batchStepper) el.batchStepper.style.display = 'grid';
    if (el.modalBatchSubmit) el.modalBatchSubmit.disabled = true;

    if (el.batchStepperFill) el.batchStepperFill.style.width = '35%';
    if (el.batchStepperLabel) el.batchStepperLabel.textContent = `Procesando lote de ${urls.length} URLs en sector [${sector}]...`;

    try {
      const res = await fetch('/api/v1/prospects/batch-audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: tenant,
          sector: sector,
          urls: urls,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Fallo en la auditoría en lote');
      }

      const data = await res.json();
      if (el.batchStepperFill) el.batchStepperFill.style.width = '100%';
      if (el.batchStepperLabel) el.batchStepperLabel.textContent = `Lote finalizado: ${data.processed_count} prospectos generados.`;

      setTimeout(async () => {
        closeBatchModal();
        showToast(`Lote completado: ${data.processed_count} prospectos procesados con éxito`);

        if (state.tenantId !== tenant) {
          state.tenantId = tenant;
          if (el.tenantSelect) el.tenantSelect.value = tenant;
          localStorage.setItem('revops_tenant', tenant);
        }

        await fetchLeads();
        await fetchStats();
      }, 700);
    } catch (err) {
      if (el.batchStepperLabel) el.batchStepperLabel.textContent = `Error: ${err.message}`;
      showToast(`Error en lote: ${err.message}`, 'error');
      if (el.modalBatchSubmit) el.modalBatchSubmit.disabled = false;
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
   * Export Visible Pipeline to Excel-Compliant CSV (UTF-8 BOM + Sanitized Multi-line)
   */
  function exportPipelineCsv() {
    if (state.filteredLeads.length === 0) {
      showToast('No hay prospectos para exportar con los filtros actuales', 'error');
      return;
    }

    // Build genuine Excel HTML table that Excel renders with zero encoding or column splitting issues
    const escapeExcelXml = (val) => {
      if (val === null || val === undefined) return '';
      return String(val)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;')
        .replace(/\r\n/g, '<br style="mso-data-placement:same-cell;"/>')
        .replace(/[\r\n]/g, '<br style="mso-data-placement:same-cell;"/>')
        .trim();
    };

    const headers = [
      'ID Prospecto',
      'Nombre Empresa',
      'Sitio Web',
      'Unidad / Tenant',
      'Estado Pipeline',
      'Score Calificación',
      'Resumen de Investigación y Brechas',
      'Propuesta de Comunicación (Outreach)'
    ];

    const thead = `<tr>${headers.map(h => `<th style="background-color:#18181b;color:#f4f4f5;font-weight:bold;border:1px solid #3f3f46;padding:8px;font-family:Calibri,sans-serif;">${escapeExcelXml(h)}</th>`).join('')}</tr>`;

    const tbody = state.filteredLeads.map((l, idx) => {
      const bg = idx % 2 === 0 ? '#ffffff' : '#f9fafb';
      return `<tr>
        <td style="background-color:${bg};border:1px solid #e4e4e7;padding:6px 8px;font-family:Calibri,sans-serif;">${escapeExcelXml(l.id)}</td>
        <td style="background-color:${bg};border:1px solid #e4e4e7;padding:6px 8px;font-weight:600;font-family:Calibri,sans-serif;">${escapeExcelXml(l.name)}</td>
        <td style="background-color:${bg};border:1px solid #e4e4e7;padding:6px 8px;font-family:Calibri,sans-serif;">${escapeExcelXml(l.url)}</td>
        <td style="background-color:${bg};border:1px solid #e4e4e7;padding:6px 8px;font-family:Calibri,sans-serif;">${escapeExcelXml(l.tenant_id)}</td>
        <td style="background-color:${bg};border:1px solid #e4e4e7;padding:6px 8px;font-family:Calibri,sans-serif;">${escapeExcelXml(l.state)}</td>
        <td style="background-color:${bg};border:1px solid #e4e4e7;padding:6px 8px;text-align:center;font-weight:bold;font-family:Calibri,sans-serif;">${l.score || 0}</td>
        <td style="background-color:${bg};border:1px solid #e4e4e7;padding:6px 8px;font-family:Calibri,sans-serif;white-space:normal;">${escapeExcelXml(l.research_summary)}</td>
        <td style="background-color:${bg};border:1px solid #e4e4e7;padding:6px 8px;font-family:Calibri,sans-serif;white-space:normal;">${escapeExcelXml(l.draft_message)}</td>
      </tr>`;
    }).join('');

    const excelHtml = `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <!--[if gte mso 9]>
  <xml>
    <x:ExcelWorkbook>
      <x:ExcelWorksheets>
        <x:ExcelWorksheet>
          <x:Name>RevOps Pipeline</x:Name>
          <x:WorksheetOptions>
            <x:DisplayGridlines/>
          </x:WorksheetOptions>
        </x:ExcelWorksheet>
      </x:ExcelWorksheets>
    </x:ExcelWorkbook>
  </xml>
  <![endif]-->
  <style>
    br { mso-data-placement: same-cell; }
  </style>
</head>
<body>
  <table>
    <thead>${thead}</thead>
    <tbody>${tbody}</tbody>
  </table>
</body>
</html>`;

    const blob = new Blob([excelHtml], { type: 'application/vnd.ms-excel;charset=utf-8;' });
    const blobUrl = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.setAttribute('download', `revops_pipeline_${state.tenantId}_${Date.now()}.xls`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(blobUrl);

    showToast(`Exportados ${state.filteredLeads.length} prospectos en formato nativo para Excel`);
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
      el.refreshBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        el.refreshBtn.disabled = true;
        try {
          await Promise.all([fetchLeads(), fetchStats()]);
          showToast('Datos actualizados');
        } catch (err) {
          showToast('Error al refrescar datos', 'error');
        } finally {
          el.refreshBtn.disabled = false;
        }
      });
    }

    // Logout Button
    if (el.btnLogout) {
      el.btnLogout.addEventListener('click', async (e) => {
        e.preventDefault();
        try {
          await fetch('/api/v1/auth/logout', { method: 'POST' });
        } catch (_) {
          // ignore network error
        }
        // Remove cookie on client side as well for instant UX feedback
        document.cookie = 'hzsaas_session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
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

    if (el.cityChipsGroup) {
      el.cityChipsGroup.addEventListener('click', (e) => {
        const btn = e.target.closest('.chip-btn');
        if (!btn) return;
        el.cityChipsGroup.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeCity = btn.dataset.city;
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
    if (el.btnClearDemo) el.btnClearDemo.addEventListener('click', clearDemoTenant);

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

    // Autonomous Scout Bot Controls
    if (el.btnOpenAutoModal) el.btnOpenAutoModal.addEventListener('click', openAutoScoutModal);
    if (el.modalScoutClose) el.modalScoutClose.addEventListener('click', closeAutoScoutModal);
    if (el.modalScoutCancel) el.modalScoutCancel.addEventListener('click', closeAutoScoutModal);
    if (el.formAutoScout) el.formAutoScout.addEventListener('submit', handleAutoScout);

    // Batch Audit Modal Controls
    if (el.btnOpenBatchModal) el.btnOpenBatchModal.addEventListener('click', openBatchModal);
    if (el.modalBatchClose) el.modalBatchClose.addEventListener('click', closeBatchModal);
    if (el.modalBatchCancel) el.modalBatchCancel.addEventListener('click', closeBatchModal);
    if (el.formBatchAudit) el.formBatchAudit.addEventListener('submit', handleBatchAudit);

    // Save Contact Info inside Drawer
    if (el.btnSaveContactInfo) {
      el.btnSaveContactInfo.addEventListener('click', saveContactInfo);
    }

    // Save Internal Notes & Cadence inside Drawer
    if (el.btnSaveNotes) {
      el.btnSaveNotes.addEventListener('click', saveLeadNotes);
    }

    // Direct WhatsApp Dispatch inside Drawer (Smart Phone Targeting)
    if (el.btnWhatsappDirect) {
      el.btnWhatsappDirect.addEventListener('click', () => {
        const text = el.drawerCopy ? el.drawerCopy.value.trim() : '';
        if (!text) {
          showToast('No hay propuesta para enviar por WhatsApp', 'error');
          return;
        }

        let phone = el.drawerContactPhone ? el.drawerContactPhone.value.trim().replace(/\D/g, '') : '';
        // If 10 digits starting with 3 (Colombia mobile format: 300xxxxxxx), prepend country code 57
        if (phone.length === 10 && phone.startsWith('3')) {
          phone = `57${phone}`;
        }

        const encoded = encodeURIComponent(text);
        const url = phone ? `https://wa.me/${phone}?text=${encoded}` : `https://wa.me/?text=${encoded}`;
        window.open(url, '_blank', 'noopener');
        showToast(phone ? `Abriendo WhatsApp directo con +${phone}` : 'Abriendo WhatsApp con propuesta lista');
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
