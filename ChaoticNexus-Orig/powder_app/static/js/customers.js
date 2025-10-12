/**
 * Customers List Page - Quick Reference Cards + Mini Dashboard
 * Handles expand/collapse, lazy loading dashboard data, and search
 */

(function() {
  'use strict';

  // State
  let allCustomers = [];
  let expandedCustomers = new Set();

  // DOM Elements
  const customerList = document.getElementById('customerList');
  const customerCount = document.getElementById('customerCount');
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const emptyState = document.getElementById('emptyState');
  const newCustomerBtn = document.getElementById('newCustomerBtn');
  const newCustomerModal = document.getElementById('newCustomerModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const cancelModalBtn = document.getElementById('cancelModalBtn');

  // Initialize
  init();

  function init() {
    loadCustomers();
    setupEventListeners();
  }

  function setupEventListeners() {
    // Search
    if (searchInput) {
      searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    if (clearSearchBtn) {
      clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        handleSearch();
      });
    }

    // Modal
    if (newCustomerBtn) {
      newCustomerBtn.addEventListener('click', () => {
        newCustomerModal.classList.remove('hidden');
      });
    }
    if (closeModalBtn) {
      closeModalBtn.addEventListener('click', () => {
        newCustomerModal.classList.add('hidden');
      });
    }
    if (cancelModalBtn) {
      cancelModalBtn.addEventListener('click', () => {
        newCustomerModal.classList.add('hidden');
      });
    }
    // Close modal on backdrop click
    if (newCustomerModal) {
      newCustomerModal.addEventListener('click', (e) => {
        if (e.target === newCustomerModal) {
          newCustomerModal.classList.add('hidden');
        }
      });
    }
  }

  async function loadCustomers() {
    try {
      const response = await fetch('/api/customers');
      if (!response.ok) throw new Error('Failed to load customers');
      
      allCustomers = await response.json();
      renderCustomers(allCustomers);
      updateCount(allCustomers.length);
    } catch (error) {
      console.error('Error loading customers:', error);
      customerList.innerHTML = `
        <div class="text-center py-12 text-red-400">
          <p class="text-lg font-medium">Failed to load customers</p>
          <p class="text-sm mt-1">${error.message}</p>
        </div>
      `;
    }
  }

  function renderCustomers(customers) {
    if (customers.length === 0) {
      customerList.classList.add('hidden');
      emptyState.classList.remove('hidden');
      return;
    }

    customerList.classList.remove('hidden');
    emptyState.classList.add('hidden');

    customerList.innerHTML = customers.map(c => createCustomerCard(c)).join('');

    // Attach event listeners
    customers.forEach(c => {
      const card = document.getElementById(`customer-${c.id}`);
      const chevron = document.getElementById(`chevron-${c.id}`);
      const viewMoreBtn = document.getElementById(`viewmore-${c.id}`);

      if (card) {
        // Card click (except buttons)
        card.addEventListener('click', (e) => {
          if (!e.target.closest('a, button')) {
            toggleExpand(c.id);
          }
        });

        // Keyboard support
        card.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleExpand(c.id);
          }
        });
      }

      if (chevron) {
        chevron.addEventListener('click', (e) => {
          e.stopPropagation();
          toggleExpand(c.id);
        });
      }
    });
  }

  function createCustomerCard(customer) {
    const { id, company, contact_name, phone, email, stats, address_short } = customer;
    const isExpanded = expandedCustomers.has(id);

    return `
      <article 
        id="customer-${id}"
        class="bg-dark-panel rounded-xl border border-dark-border p-4 cursor-pointer hover:border-blue-700/50 transition-all focus:outline-none focus:ring-2 focus:ring-blue-600"
        tabindex="0"
        role="button"
        aria-expanded="${isExpanded}"
      >
        <!-- Collapsed View -->
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-dark-text truncate">${escapeHtml(company)}</h3>
              ${contact_name ? `<span class="text-sm text-dark-muted truncate">${escapeHtml(contact_name)}</span>` : ''}
            </div>
            
            <div class="flex flex-wrap items-center gap-2 mb-2">
              ${phone ? `<a href="tel:${phone}" class="text-sm text-blue-400 hover:text-blue-300 transition-colors" onclick="event.stopPropagation()">📞 ${escapeHtml(phone)}</a>` : ''}
              ${email ? `<a href="mailto:${email}" class="text-sm text-blue-400 hover:text-blue-300 transition-colors" onclick="event.stopPropagation()">📧 ${escapeHtml(email)}</a>` : ''}
            </div>

            <div class="flex flex-wrap items-center gap-2">
              ${stats.active_jobs > 0 ? `<span class="badge badge-active">${stats.active_jobs} Active</span>` : ''}
              ${stats.queued_jobs > 0 ? `<span class="badge badge-queued">${stats.queued_jobs} Queued</span>` : ''}
              ${stats.completed_recent > 0 ? `<span class="badge badge-completed">${stats.completed_recent} Completed (90d)</span>` : ''}
            </div>

            ${address_short ? `<p class="text-sm text-dark-muted mt-2 truncate">📍 ${escapeHtml(address_short)}</p>` : ''}
          </div>

          <div class="flex flex-col items-end gap-2">
            <button 
              id="chevron-${id}"
              class="p-2 hover:bg-dark-hover rounded-lg transition-colors"
              aria-label="Expand"
            >
              <svg 
                class="w-5 h-5 text-dark-muted transition-transform ${isExpanded ? 'rotate-180' : ''}" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            <a 
              id="viewmore-${id}"
              href="/customers/${id}" 
              class="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
              onclick="event.stopPropagation()"
            >
              View More
            </a>
          </div>
        </div>

        <!-- Expanded View (Dashboard) -->
        <div id="dashboard-${id}" class="mt-4 pt-4 border-t border-dark-border ${isExpanded ? '' : 'hidden'}">
          ${isExpanded ? '<div class="text-center py-8"><div class="skeleton rounded-lg h-64 w-full"></div></div>' : ''}
        </div>
      </article>
    `;
  }

  async function toggleExpand(customerId) {
    const isExpanded = expandedCustomers.has(customerId);
    const card = document.getElementById(`customer-${customerId}`);
    const dashboard = document.getElementById(`dashboard-${customerId}`);
    const chevron = document.querySelector(`#chevron-${customerId} svg`);

    if (!card || !dashboard) return;

    if (isExpanded) {
      // Collapse
      expandedCustomers.delete(customerId);
      dashboard.classList.add('hidden');
      chevron.classList.remove('rotate-180');
      card.setAttribute('aria-expanded', 'false');
    } else {
      // Expand
      expandedCustomers.add(customerId);
      dashboard.classList.remove('hidden');
      chevron.classList.add('rotate-180');
      card.setAttribute('aria-expanded', 'true');

      // Load dashboard data if not already loaded
      if (!dashboard.dataset.loaded) {
        await loadDashboard(customerId);
      }
    }
  }

  async function loadDashboard(customerId) {
    const dashboard = document.getElementById(`dashboard-${customerId}`);
    if (!dashboard) return;

    try {
      const response = await fetch(`/api/customers/${customerId}/dashboard`);
      if (!response.ok) throw new Error('Failed to load dashboard');

      const data = await response.json();
      dashboard.innerHTML = renderDashboard(data, customerId);
      dashboard.dataset.loaded = 'true';
    } catch (error) {
      console.error('Error loading dashboard:', error);
      dashboard.innerHTML = `
        <div class="text-center py-8 text-red-400">
          <p class="text-sm">Failed to load dashboard data</p>
        </div>
      `;
    }
  }

  function renderDashboard(data, customerId) {
    const { kpis, mix, activity } = data;

    return `
      <!-- KPIs Row -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
        <div class="bg-dark-card rounded-lg p-3 border border-dark-border">
          <p class="text-xs text-dark-muted mb-1">Active Jobs</p>
          <p class="text-2xl font-bold text-dark-text">${kpis.active_jobs}</p>
        </div>
        ${kpis.avg_turnaround_days_10 !== null ? `
        <div class="bg-dark-card rounded-lg p-3 border border-dark-border">
          <p class="text-xs text-dark-muted mb-1">Avg Turnaround</p>
          <p class="text-2xl font-bold text-dark-text">${kpis.avg_turnaround_days_10}<span class="text-sm text-dark-muted ml-1">days</span></p>
        </div>
        ` : ''}
        ${kpis.on_time_pct_90d !== null ? `
        <div class="bg-dark-card rounded-lg p-3 border border-dark-border">
          <p class="text-xs text-dark-muted mb-1">On-Time (90d)</p>
          <p class="text-2xl font-bold ${kpis.on_time_pct_90d >= 80 ? 'text-green-400' : 'text-yellow-400'}">${kpis.on_time_pct_90d}%</p>
        </div>
        ` : ''}
        <div class="bg-dark-card rounded-lg p-3 border border-dark-border">
          <p class="text-xs text-dark-muted mb-1">Jobs This Month</p>
          <p class="text-2xl font-bold text-dark-text">${kpis.jobs_this_month}</p>
        </div>
        ${kpis.lifetime_revenue !== null ? `
        <div class="bg-dark-card rounded-lg p-3 border border-dark-border">
          <p class="text-xs text-dark-muted mb-1">Lifetime Revenue</p>
          <p class="text-2xl font-bold text-dark-text">$${kpis.lifetime_revenue.toLocaleString()}</p>
        </div>
        ` : ''}
        <div class="bg-dark-card rounded-lg p-3 border border-dark-border">
          <p class="text-xs text-dark-muted mb-1">Redos (12m)</p>
          <p class="text-2xl font-bold ${kpis.redo_count_12m === 0 ? 'text-green-400' : 'text-yellow-400'}">${kpis.redo_count_12m}</p>
        </div>
      </div>

      <!-- Work Mix & Activity -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Work Mix -->
        <div class="bg-dark-card rounded-lg p-4 border border-dark-border">
          <h4 class="text-sm font-semibold text-dark-text mb-3">Work Mix (6mo)</h4>
          ${mix.job_types.length > 0 ? `
            <div class="space-y-2">
              ${mix.job_types.map(jt => `
                <div class="flex items-center justify-between">
                  <span class="text-sm text-dark-muted">${escapeHtml(jt.type)}</span>
                  <span class="text-sm font-medium text-dark-text">${jt.count}</span>
                </div>
              `).join('')}
            </div>
          ` : '<p class="text-sm text-dark-muted">No job types recorded</p>'}
          
          ${mix.top_powders.length > 0 ? `
            <h5 class="text-xs font-semibold text-dark-muted mt-4 mb-2">Top Powders</h5>
            <div class="space-y-1">
              ${mix.top_powders.map(p => `
                <div class="flex items-center justify-between text-xs">
                  <span class="text-dark-muted">${escapeHtml(p.ral)}</span>
                  <span class="text-dark-text font-medium">${p.count}x</span>
                </div>
              `).join('')}
            </div>
          ` : ''}
        </div>

        <!-- Recent Activity -->
        <div class="bg-dark-card rounded-lg p-4 border border-dark-border">
          <h4 class="text-sm font-semibold text-dark-text mb-3">Recent Jobs</h4>
          ${activity.recent_jobs.length > 0 ? `
            <div class="space-y-2">
              ${activity.recent_jobs.map(job => `
                <div class="flex items-center justify-between py-2 border-b border-dark-border last:border-0">
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-dark-text">Job #${job.id}</p>
                    <p class="text-xs text-dark-muted truncate">${escapeHtml(job.type)} • ${getStatusBadge(job.status)}</p>
                  </div>
                  <div class="text-right">
                    <p class="text-xs text-dark-muted">${job.due_date || 'No due date'}</p>
                    <p class="text-xs text-dark-muted truncate">${escapeHtml(job.color)}</p>
                  </div>
                </div>
              `).join('')}
            </div>
          ` : '<p class="text-sm text-dark-muted">No recent jobs</p>'}
        </div>
      </div>

      <!-- Actions -->
      <div class="flex flex-wrap items-center gap-2 mt-4">
        <a href="/jobs?company=${encodeURIComponent(getCustomerCompany(customerId))}" class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors">
          Create Job
        </a>
        <a href="/customers/${customerId}" class="px-4 py-2 rounded-lg bg-dark-card hover:bg-dark-hover border border-dark-border text-sm font-medium transition-colors">
          View Full Profile
        </a>
      </div>
    `;
  }

  function getStatusBadge(status) {
    const badges = {
      'queued': '<span class="badge badge-queued">Queued</span>',
      'in_work': '<span class="badge badge-active">In Work</span>',
      'waiting_material': '<span class="badge badge-active">Waiting</span>',
      'ready_pickup': '<span class="badge badge-completed">Ready</span>',
      'completed': '<span class="badge badge-completed">Done</span>',
    };
    return badges[status] || `<span class="text-dark-muted">${status}</span>`;
  }

  function getCustomerCompany(customerId) {
    const customer = allCustomers.find(c => c.id === customerId);
    return customer ? customer.company : '';
  }

  function handleSearch() {
    const query = searchInput.value.toLowerCase().trim();
    
    if (!query) {
      renderCustomers(allCustomers);
      updateCount(allCustomers.length);
      return;
    }

    const filtered = allCustomers.filter(c => {
      return (
        c.company.toLowerCase().includes(query) ||
        (c.contact_name && c.contact_name.toLowerCase().includes(query)) ||
        (c.email && c.email.toLowerCase().includes(query))
      );
    });

    renderCustomers(filtered);
    updateCount(filtered.length);
  }

  function updateCount(count) {
    if (customerCount) {
      const word = count === 1 ? 'customer' : 'customers';
      customerCount.textContent = `${count} ${word}`;
    }
  }

  function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
})();

