/**
 * G$L Government Funding Opportunities Marketplace (KSL Classifieds Theme)
 * File: gsl.js
 */

(function () {
  // Initial Mock Dataset of Government Funding Opportunities
  const INITIAL_OPPORTUNITIES = [
    {
      id: "GSL-2026-0891",
      title: "RFQ-2026-88: Advanced Grid Energy Storage Infrastructure Grant",
      type: "Grant",
      agency: "U.S. Department of Energy (DOE)",
      agencyCode: "DOE",
      category: "Clean Energy & Climate",
      awardMin: 500000,
      awardMax: 3500000,
      postedDate: "2026-08-10",
      deadline: "2026-09-15",
      closingDays: 8,
      status: "Open",
      eligibility: ["Small Business", "Higher Ed / Universities", "State & Local Gov"],
      location: "Salt Lake City, UT & Regional Grid",
      tags: ["Matching 20% Required", "Clean Energy", "Grid Reliability"],
      description: "Funding for commercialization of utility-scale battery energy storage systems, virtual power plants (VPPs), and microgrid integrations across rural and urban energy grids in Utah and the Intermountain West.",
      contactEmail: "grants-cleanenergy@hq.doe.gov",
      cfdaNumber: "81.086",
      portalUrl: "https://www.grants.gov/search-grants?opportunityNum=DOE-FOA-0003180"
    },
    {
      id: "GSL-2026-0442",
      title: "RFP-UT-2026: State of Utah Innovation & Commercialization SBIR Match Grant",
      type: "SBIR",
      agency: "State of Utah GOED (Governor's Office of Economic Opportunity)",
      agencyCode: "Utah GOED",
      category: "Small Business Development",
      awardMin: 100000,
      awardMax: 250000,
      postedDate: "2026-08-14",
      deadline: "2026-10-01",
      closingDays: 24,
      status: "Open",
      eligibility: ["Small Business", "SBA Certified"],
      location: "Statewide Utah",
      tags: ["State Matching Grant", "Technology", "Startup Support"],
      description: "Direct state matching grants for Utah-based small technology businesses that have received federal Phase I SBIR/STTR awards to accelerate prototype deployment.",
      contactEmail: "innovation@utah.gov",
      cfdaNumber: "UT-GOED-2026",
      portalUrl: "https://business.utah.gov/innovation-grants"
    },
    {
      id: "GSL-2026-1033",
      title: "RFQ-DOD-2026: Autonomous Drone Swarm Communications & Edge AI",
      type: "RFQ",
      agency: "Department of Defense (DoD / DARPA)",
      agencyCode: "DoD",
      category: "AI & Technology",
      awardMin: 1500000,
      awardMax: 8000000,
      postedDate: "2026-08-01",
      deadline: "2026-08-28",
      closingDays: 3,
      status: "Open",
      eligibility: ["Small Business", "Defense Contractors"],
      location: "Nationwide / Remote",
      tags: ["Security Clearance Required", "Edge Computing", "AI/ML"],
      description: "Request for Quotes for low-latency tactical mesh networking algorithms and embedded artificial intelligence hardware prototypes operating in GPS-denied environments.",
      contactEmail: "sbir-darpa@darpa.mil",
      cfdaNumber: "12.000",
      portalUrl: "https://www.sam.gov/opp/darpa-rfq-2026"
    },
    {
      id: "GSL-2026-0714",
      title: "NSF 26-501: Regional AI Research Institute & Supercomputing Infrastructure",
      type: "Grant",
      agency: "National Science Foundation (NSF)",
      agencyCode: "NSF",
      category: "Education & Research",
      awardMin: 2000000,
      awardMax: 20000000,
      postedDate: "2026-07-25",
      deadline: "2026-11-15",
      closingDays: 69,
      status: "Open",
      eligibility: ["Higher Ed / Universities", "Non-Profit / 501(c)(3)"],
      location: "Intermountain West Hub (UT, ID, WY)",
      tags: ["Compute Grant", "AI Education", "STEM Pipeline"],
      description: "Multi-year institution grants aimed at expanding regional artificial intelligence compute clusters, ethics frameworks, and interdisciplinary graduate training programs.",
      contactEmail: "ai-institutes@nsf.gov",
      cfdaNumber: "47.070",
      portalUrl: "https://www.nsf.gov/funding/pgm_summ.jsp?pims_id=505640"
    },
    {
      id: "GSL-2026-0295",
      title: "RFP-USDA-2026: Climate-Smart Agriculture & Water Conservation Technology",
      type: "RFP",
      agency: "U.S. Department of Agriculture (USDA)",
      agencyCode: "USDA",
      category: "Agriculture",
      awardMin: 250000,
      awardMax: 1200000,
      postedDate: "2026-08-08",
      deadline: "2026-09-30",
      closingDays: 23,
      status: "Open",
      eligibility: ["Small Business", "Non-Profit / 501(c)(3)", "Individual Researchers"],
      location: "Utah Rural Basins & Idaho Snake River Plain",
      tags: ["Water Conservation", "Drought Resilience", "AgTech"],
      description: "Funding for automated drip irrigation telemetry, soil moisture remote sensing, and drought-resistant crop strain field trials across agricultural basins.",
      contactEmail: "nrcs-grants@usda.gov",
      cfdaNumber: "10.912",
      portalUrl: "https://www.nrcs.usda.gov/funding-opportunities"
    },
    {
      id: "GSL-2026-0566",
      title: "CONTRACT-DOT-2026: Intelligent Transportation System & Traffic Sensor Mesh",
      type: "Contract",
      agency: "U.S. Department of Transportation (DOT)",
      agencyCode: "DOT",
      category: "Infrastructure & Construction",
      awardMin: 800000,
      awardMax: 4500000,
      postedDate: "2026-08-12",
      deadline: "2026-10-15",
      closingDays: 38,
      status: "Open",
      eligibility: ["Small Business", "State & Local Gov"],
      location: "I-15 Corridor & Wasatch Front",
      tags: ["ITS", "Smart Infrastructure", "V2X Telematics"],
      description: "Procurement contract for roadside LiDAR sensors, connected vehicle warning beacons, and automated real-time transit bottleneck analysis platforms.",
      contactEmail: "contracts-its@dot.gov",
      cfdaNumber: "20.205",
      portalUrl: "https://www.sam.gov/opp/dot-its-wasatch"
    },
    {
      id: "GSL-2026-0977",
      title: "HHS-NIH-2026: Digital Health Disparities & Rural Telemedicine Expansion",
      type: "Grant",
      agency: "Department of Health & Human Services (HHS / NIH)",
      agencyCode: "HHS",
      category: "Healthcare & Biotech",
      awardMin: 400000,
      awardMax: 2000000,
      postedDate: "2026-08-05",
      deadline: "2026-10-30",
      closingDays: 53,
      status: "Open",
      eligibility: ["Non-Profit / 501(c)(3)", "Higher Ed / Universities", "Small Business"],
      location: "Utah Rural Health Clinics & Tribal Nations",
      tags: ["Telehealth", "Biotech", "Rural Medicine"],
      description: "Grants supporting implementation of HIPAA-compliant AI diagnostics and broadband diagnostic video links to remote clinics and underserved communities.",
      contactEmail: "grants-info@nih.gov",
      cfdaNumber: "93.865",
      portalUrl: "https://grants.nih.gov/funding/search-nih-guide.htm"
    }
  ];

  // Application State
  const state = {
    opportunities: [...INITIAL_OPPORTUNITIES],
    bookmarks: JSON.parse(localStorage.getItem('gsl_bookmarks') || '[]'),
    filters: {
      searchQuery: '',
      type: 'ALL', // ALL, Grant, RFQ, RFP, SBIR, Contract
      category: 'ALL',
      agency: 'ALL',
      minAward: '',
      maxAward: '',
      status: 'ALL',
      eligibility: 'ALL',
      showOnlyBookmarks: false
    },
    sortBy: 'newest', // newest, closing_soon, amount_high
    activeModal: null, // null, 'detail', 'post'
    selectedOpportunity: null
  };

  // Main Initialization
  document.addEventListener('DOMContentLoaded', () => {
    initApp();
  });

  function initApp() {
    renderApp();
    bindEvents();
  }

  // Render Full Web Application Structure
  function renderApp() {
    const root = document.getElementById('app') || document.body;
    
    root.innerHTML = `
      <!-- Top Navigation Bar (KSL Navy Style) -->
      <header class="gsl-header">
        <div class="gsl-header-top">
          <div class="brand-section">
            <a href="#" class="gsl-logo-circle" title="G$L Funding Opportunities">
              G<span class="dollar-sign">$</span>L
            </a>
            <ul class="gsl-nav-links">
              <li><a href="#" class="active">Grants</a></li>
              <li><a href="#">RFQs & RFPs</a></li>
              <li><a href="#">SBIR / STTR</a></li>
              <li><a href="#">State Incentives</a></li>
            </ul>
          </div>
          <div class="gsl-header-right">
            <div class="location-weather">
              <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              <span>Utah & Regional • <strong>64°</strong></span>
            </div>
            <div class="user-actions">
              <a href="#" class="btn-login">
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                Sign In
              </a>
            </div>
          </div>
        </div>
      </header>

      <!-- Sub Navigation Bar -->
      <div class="gsl-subnav">
        <div class="gsl-subnav-inner">
          <ul class="subnav-links">
            <li><a href="#" id="nav-all-listings">Browse Opportunities</a></li>
            <li>
              <a href="#" id="nav-saved-listings">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24" style="color:var(--accent-gold);"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                Saved (<span id="saved-count">0</span>)
              </a>
            </li>
            <li><a href="#">Funding Guidelines</a></li>
            <li><a href="#">Help & Support</a></li>
          </ul>
          <button class="btn-post-rfq" id="btn-open-post-modal">
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            Post Opportunity / RFQ
          </button>
        </div>
      </div>

      <!-- Main Application Container -->
      <main class="gsl-container">
        <!-- Breadcrumbs -->
        <div class="gsl-breadcrumbs">
          <a href="#">G$L Home</a> &rsaquo; 
          <span>Grants & Funding Opportunities</span>
        </div>

        <!-- Page Header & Count -->
        <div class="gsl-page-title-row">
          <h1>Government Funding Opportunities in Utah & Federal</h1>
          <div class="gsl-results-count">
            Showing <span id="results-count-num">0</span> Active Funding Listings
          </div>
        </div>

        <!-- Layout Grid (Sidebar + Feed) -->
        <div class="gsl-main-layout">
          <!-- Sidebar Filters -->
          <aside class="gsl-sidebar" id="gsl-sidebar">
            <div class="filter-header-mobile">
              <h3>Filter Opportunities</h3>
              <button class="btn-reset-filters" id="btn-reset-filters">Reset All</button>
            </div>

            <!-- Funding Type Filter -->
            <div class="filter-group">
              <div class="filter-group-title">Funding Type</div>
              <div class="funding-type-buttons">
                <button class="btn-type-toggle active" data-type="ALL">All Types</button>
                <button class="btn-type-toggle" data-type="Grant">Grants</button>
                <button class="btn-type-toggle" data-type="RFQ">RFQs</button>
                <button class="btn-type-toggle" data-type="RFP">RFPs</button>
                <button class="btn-type-toggle" data-type="SBIR">SBIR/STTR</button>
                <button class="btn-type-toggle" data-type="Contract">Contracts</button>
              </div>
            </div>

            <!-- Category Filter -->
            <div class="filter-group">
              <div class="filter-group-title">Category / Sector</div>
              <select class="filter-select" id="filter-category">
                <option value="ALL">All Categories</option>
                <option value="Clean Energy & Climate">Clean Energy & Climate</option>
                <option value="AI & Technology">AI & Technology</option>
                <option value="Infrastructure & Construction">Infrastructure & Construction</option>
                <option value="Healthcare & Biotech">Healthcare & Biotech</option>
                <option value="Small Business Development">Small Business Development</option>
                <option value="Agriculture">Agriculture</option>
                <option value="Education & Research">Education & Research</option>
              </select>
            </div>

            <!-- Issuing Agency Filter -->
            <div class="filter-group">
              <div class="filter-group-title">Issuing Agency</div>
              <select class="filter-select" id="filter-agency">
                <option value="ALL">All Agencies</option>
                <option value="DOE">U.S. Department of Energy (DOE)</option>
                <option value="Utah GOED">State of Utah (GOED)</option>
                <option value="DoD">Department of Defense (DoD)</option>
                <option value="NSF">National Science Foundation (NSF)</option>
                <option value="USDA">Department of Agriculture (USDA)</option>
                <option value="DOT">Department of Transportation (DOT)</option>
                <option value="HHS">Health & Human Services (HHS/NIH)</option>
              </select>
            </div>

            <!-- Award Amount Filter -->
            <div class="filter-group">
              <div class="filter-group-title">Award Amount ($)</div>
              <div class="range-inputs">
                <input type="number" class="filter-input" id="filter-min-award" placeholder="Min ($)" step="50000">
                <span style="color:var(--text-muted);">&ndash;</span>
                <input type="number" class="filter-input" id="filter-max-award" placeholder="Max ($)" step="100000">
              </div>
            </div>

            <!-- Eligibility Filter -->
            <div class="filter-group">
              <div class="filter-group-title">Eligible Entities</div>
              <div class="checkbox-list">
                <label class="checkbox-label">
                  <input type="checkbox" class="filter-eligibility-cb" value="Small Business"> Small Business (SBA)
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" class="filter-eligibility-cb" value="Higher Ed / Universities"> Universities / Colleges
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" class="filter-eligibility-cb" value="Non-Profit / 501(c)(3)"> Non-Profit / 501(c)(3)
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" class="filter-eligibility-cb" value="State & Local Gov"> State & Local Gov
                </label>
              </div>
            </div>
          </aside>

          <!-- Main Feed & Search Area -->
          <section class="gsl-feed-container">
            <!-- Search Bar Wrapper (KSL Style) -->
            <div class="gsl-search-bar-wrapper">
              <svg class="search-icon-svg" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              <input type="text" class="gsl-search-input" id="search-input" placeholder="Search by title, keywords, agency, or grant number (e.g. 'energy', 'drone', 'Utah')...">
              <button class="btn-clear-search" id="btn-clear-search">&times;</button>
              <button class="btn-search-submit" id="btn-search-submit">Search</button>
            </div>

            <!-- Feed Toolbar Controls -->
            <div class="gsl-toolbar">
              <div class="toolbar-left">
                <button class="toggle-sidebar-btn" id="btn-toggle-sidebar">
                  <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2a1 1 0 01-.293.707L13 13.414V19a1 1 0 01-.447.894l-4 2A1 1 0 017 21v-7.586L3.293 6.707A1 1 0 013 6V4z"/></svg>
                  Toggle Filters
                </button>
                <span id="active-filter-pill" style="font-size:0.82rem; color:var(--accent-blue); font-weight:600;"></span>
              </div>
              <div class="toolbar-right">
                <div class="sort-group">
                  <label for="sort-select">Sort by:</label>
                  <select class="sort-select" id="sort-select">
                    <option value="newest">Newest to Oldest</option>
                    <option value="closing_soon">Closing Soonest</option>
                    <option value="amount_high">Highest Award Amount</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Opportunity Card Feed -->
            <div class="opportunity-list" id="opportunity-list">
              <!-- Rendered via JS -->
            </div>
          </section>
        </div>
      </main>

      <!-- Modal: Detail View -->
      <div class="modal-overlay" id="modal-detail">
        <div class="modal-card">
          <div class="modal-header">
            <div class="modal-header-title-box">
              <span id="md-badge-type" class="badge-type badge-grant">Grant</span>
              <h3 id="md-title">Opportunity Title</h3>
            </div>
            <button class="btn-close-modal" class="btn-close-modal" id="btn-close-detail">&times;</button>
          </div>
          <div class="modal-body">
            <div class="modal-grid-metrics">
              <div class="modal-metric-box">
                <span class="modal-metric-label">Award Amount Range</span>
                <span class="modal-metric-val" id="md-amount" style="color:var(--grant-green);">$500,000 &ndash; $2,500,000</span>
              </div>
              <div class="modal-metric-box">
                <span class="modal-metric-label">Application Deadline</span>
                <span class="modal-metric-val" id="md-deadline">Sept 15, 2026</span>
              </div>
              <div class="modal-metric-box">
                <span class="modal-metric-label">Issuing Agency</span>
                <span class="modal-metric-val" id="md-agency">DOE</span>
              </div>
              <div class="modal-metric-box">
                <span class="modal-metric-label">CFDA / Opportunity #</span>
                <span class="modal-metric-val" id="md-cfda">81.086</span>
              </div>
            </div>

            <div class="modal-section">
              <h4>Opportunity Summary & Scope</h4>
              <p id="md-description" style="color:var(--text-main); font-size:0.92rem; line-height:1.6;"></p>
            </div>

            <div class="modal-section">
              <h4>Eligibility & Target Applicants</h4>
              <div id="md-eligibility" style="display:flex; gap:0.5rem; flex-wrap:wrap;"></div>
            </div>

            <div class="modal-section">
              <h4>Location & Scope Region</h4>
              <p id="md-location" style="color:var(--text-muted); font-weight:600; font-size:0.9rem;"></p>
            </div>
          </div>
          <div class="modal-footer">
            <span style="font-size:0.82rem; color:var(--text-muted);">Contact: <strong id="md-contact">agency@gov.us</strong></span>
            <a href="#" id="md-portal-link" target="_blank" class="btn-post-rfq" style="text-decoration:none;">
              Official Agency Application Portal &rarr;
            </a>
          </div>
        </div>
      </div>

      <!-- Modal: Post New RFQ / Opportunity -->
      <div class="modal-overlay" id="modal-post">
        <div class="modal-card">
          <div class="modal-header">
            <div class="modal-header-title-box">
              <h3>Post Government Funding Opportunity / RFQ</h3>
            </div>
            <button class="btn-close-modal" id="btn-close-post">&times;</button>
          </div>
          <form id="form-post-opportunity">
            <div class="modal-body">
              <div class="form-grid">
                <div class="form-group-full">
                  <label class="form-label" for="post-title">Opportunity Title / RFQ Headline *</label>
                  <input type="text" class="filter-input" id="post-title" required placeholder="e.g. RFQ-2026-99: Rural Renewable Energy Microgrid Grant">
                </div>
                
                <div>
                  <label class="form-label" for="post-type">Funding Type *</label>
                  <select class="filter-select" id="post-type" required>
                    <option value="Grant">Grant</option>
                    <option value="RFQ">RFQ (Request for Quote)</option>
                    <option value="RFP">RFP (Request for Proposal)</option>
                    <option value="SBIR">SBIR / STTR</option>
                    <option value="Contract">Procurement Contract</option>
                  </select>
                </div>

                <div>
                  <label class="form-label" for="post-agency">Issuing Agency Name *</label>
                  <input type="text" class="filter-input" id="post-agency" required placeholder="e.g. State of Utah Dept of Transportation">
                </div>

                <div>
                  <label class="form-label" for="post-category">Category / Industry *</label>
                  <select class="filter-select" id="post-category" required>
                    <option value="Clean Energy & Climate">Clean Energy & Climate</option>
                    <option value="AI & Technology">AI & Technology</option>
                    <option value="Infrastructure & Construction">Infrastructure & Construction</option>
                    <option value="Healthcare & Biotech">Healthcare & Biotech</option>
                    <option value="Small Business Development">Small Business Development</option>
                    <option value="Agriculture">Agriculture</option>
                    <option value="Education & Research">Education & Research</option>
                  </select>
                </div>

                <div>
                  <label class="form-label" for="post-deadline">Application Deadline *</label>
                  <input type="date" class="filter-input" id="post-deadline" required>
                </div>

                <div>
                  <label class="form-label" for="post-min-award">Min Award ($)</label>
                  <input type="number" class="filter-input" id="post-min-award" placeholder="100000" step="10000">
                </div>

                <div>
                  <label class="form-label" for="post-max-award">Max Award ($)</label>
                  <input type="number" class="filter-input" id="post-max-award" placeholder="1500000" step="50000">
                </div>

                <div class="form-group-full">
                  <label class="form-label" for="post-desc">Full Scope & Summary Description *</label>
                  <textarea class="filter-input" id="post-desc" rows="4" required placeholder="Provide grant scope, eligibility requirements, evaluation criteria, and submission instructions..."></textarea>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn-reset-filters" id="btn-cancel-post">Cancel</button>
              <button type="submit" class="btn-post-rfq">Publish Opportunity</button>
            </div>
          </form>
        </div>
      </div>
    `;

    updateSavedCount();
    renderFeed();
  }

  // Bind DOM Event Listeners
  function bindEvents() {
    // Search input
    const searchInput = document.getElementById('search-input');
    const clearBtn = document.getElementById('btn-clear-search');
    
    searchInput.addEventListener('input', (e) => {
      state.filters.searchQuery = e.target.value.trim();
      clearBtn.classList.toggle('visible', state.filters.searchQuery.length > 0);
      renderFeed();
    });

    clearBtn.addEventListener('click', () => {
      searchInput.value = '';
      state.filters.searchQuery = '';
      clearBtn.classList.remove('visible');
      renderFeed();
    });

    // Funding Type Toggles
    const typeBtns = document.querySelectorAll('.btn-type-toggle');
    typeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        typeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.filters.type = btn.dataset.type;
        renderFeed();
      });
    });

    // Select filters
    document.getElementById('filter-category').addEventListener('change', (e) => {
      state.filters.category = e.target.value;
      renderFeed();
    });

    document.getElementById('filter-agency').addEventListener('change', (e) => {
      state.filters.agency = e.target.value;
      renderFeed();
    });

    document.getElementById('filter-min-award').addEventListener('input', (e) => {
      state.filters.minAward = e.target.value;
      renderFeed();
    });

    document.getElementById('filter-max-award').addEventListener('input', (e) => {
      state.filters.maxAward = e.target.value;
      renderFeed();
    });

    // Eligibility checkboxes
    const elCbs = document.querySelectorAll('.filter-eligibility-cb');
    elCbs.forEach(cb => {
      cb.addEventListener('change', () => {
        renderFeed();
      });
    });

    // Reset filters
    document.getElementById('btn-reset-filters').addEventListener('click', () => {
      state.filters.searchQuery = '';
      state.filters.type = 'ALL';
      state.filters.category = 'ALL';
      state.filters.agency = 'ALL';
      state.filters.minAward = '';
      state.filters.maxAward = '';
      state.filters.showOnlyBookmarks = false;
      
      document.getElementById('search-input').value = '';
      clearBtn.classList.remove('visible');
      document.getElementById('filter-category').value = 'ALL';
      document.getElementById('filter-agency').value = 'ALL';
      document.getElementById('filter-min-award').value = '';
      document.getElementById('filter-max-award').value = '';
      elCbs.forEach(cb => cb.checked = false);
      
      typeBtns.forEach(b => b.classList.remove('active'));
      document.querySelector('.btn-type-toggle[data-type="ALL"]').classList.add('active');

      renderFeed();
    });

    // Sort select
    document.getElementById('sort-select').addEventListener('change', (e) => {
      state.sortBy = e.target.value;
      renderFeed();
    });

    // Saved Listings Subnav button
    document.getElementById('nav-saved-listings').addEventListener('click', (e) => {
      e.preventDefault();
      state.filters.showOnlyBookmarks = !state.filters.showOnlyBookmarks;
      renderFeed();
    });

    document.getElementById('nav-all-listings').addEventListener('click', (e) => {
      e.preventDefault();
      state.filters.showOnlyBookmarks = false;
      renderFeed();
    });

    // Sidebar Mobile Toggle
    document.getElementById('btn-toggle-sidebar').addEventListener('click', () => {
      document.getElementById('gsl-sidebar').classList.toggle('mobile-open');
    });

    // Modals
    document.getElementById('btn-open-post-modal').addEventListener('click', () => {
      openModal('post');
    });

    document.getElementById('btn-close-detail').addEventListener('click', () => {
      closeModal('detail');
    });

    document.getElementById('btn-close-post').addEventListener('click', () => {
      closeModal('post');
    });

    document.getElementById('btn-cancel-post').addEventListener('click', () => {
      closeModal('post');
    });

    // Post Opportunity Form Submission
    document.getElementById('form-post-opportunity').addEventListener('submit', (e) => {
      e.preventDefault();
      const title = document.getElementById('post-title').value;
      const type = document.getElementById('post-type').value;
      const agency = document.getElementById('post-agency').value;
      const category = document.getElementById('post-category').value;
      const deadline = document.getElementById('post-deadline').value;
      const minAward = Number(document.getElementById('post-min-award').value) || 50000;
      const maxAward = Number(document.getElementById('post-max-award').value) || 250000;
      const description = document.getElementById('post-desc').value;

      const newOp = {
        id: `GSL-2026-${Math.floor(1000 + Math.random() * 9000)}`,
        title,
        type,
        agency,
        agencyCode: agency.slice(0, 10),
        category,
        awardMin: minAward,
        awardMax: maxAward,
        postedDate: new Date().toISOString().split('T')[0],
        deadline,
        closingDays: 30,
        status: "Open",
        eligibility: ["Small Business", "Higher Ed / Universities"],
        location: "Statewide Utah & Federal",
        tags: ["User Posted", "Active Opportunity"],
        description,
        contactEmail: "grants-submit@gsl-funding.gov",
        cfdaNumber: "99.999",
        portalUrl: "https://www.grants.gov"
      };

      state.opportunities.unshift(newOp);
      closeModal('post');
      e.target.reset();
      renderFeed();
    });
  }

  // Filter & Render Opportunity List
  function renderFeed() {
    const container = document.getElementById('opportunity-list');
    const resultsCountEl = document.getElementById('results-count-num');
    const activePill = document.getElementById('active-filter-pill');

    // Selected eligibility values
    const selectedEligibility = Array.from(document.querySelectorAll('.filter-eligibility-cb:checked')).map(cb => cb.value);

    // Apply Filter Logic
    let filtered = state.opportunities.filter(op => {
      // Bookmark filter
      if (state.filters.showOnlyBookmarks && !state.bookmarks.includes(op.id)) {
        return false;
      }

      // Keyword search
      if (state.filters.searchQuery) {
        const q = state.filters.searchQuery.toLowerCase();
        const matchTitle = op.title.toLowerCase().includes(q);
        const matchAgency = op.agency.toLowerCase().includes(q);
        const matchDesc = op.description.toLowerCase().includes(q);
        const matchCfda = op.cfdaNumber.toLowerCase().includes(q);
        if (!matchTitle && !matchAgency && !matchDesc && !matchCfda) return false;
      }

      // Type filter
      if (state.filters.type !== 'ALL' && op.type.toUpperCase() !== state.filters.type.toUpperCase()) {
        return false;
      }

      // Category filter
      if (state.filters.category !== 'ALL' && op.category !== state.filters.category) {
        return false;
      }

      // Agency filter
      if (state.filters.agency !== 'ALL' && op.agencyCode !== state.filters.agency) {
        return false;
      }

      // Award Min
      if (state.filters.minAward && op.awardMax < Number(state.filters.minAward)) {
        return false;
      }

      // Award Max
      if (state.filters.maxAward && op.awardMin > Number(state.filters.maxAward)) {
        return false;
      }

      // Eligibility
      if (selectedEligibility.length > 0) {
        const hasMatch = selectedEligibility.some(e => op.eligibility.includes(e));
        if (!hasMatch) return false;
      }

      return true;
    });

    // Apply Sorting
    if (state.sortBy === 'newest') {
      filtered.sort((a, b) => new Date(b.postedDate) - new Date(a.postedDate));
    } else if (state.sortBy === 'closing_soon') {
      filtered.sort((a, b) => a.closingDays - b.closingDays);
    } else if (state.sortBy === 'amount_high') {
      filtered.sort((a, b) => b.awardMax - a.awardMax);
    }

    // Update Counter
    resultsCountEl.textContent = filtered.length.toLocaleString();
    if (state.filters.showOnlyBookmarks) {
      activePill.textContent = 'Filtering: My Saved Opportunities';
    } else {
      activePill.textContent = '';
    }

    // Render Cards or Empty State
    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">&bull; 0 Results &bull;</div>
          <h3>No Funding Opportunities Found</h3>
          <p>Try broadening your search keywords or resetting filter criteria to view all opportunities.</p>
          <button class="btn-search-submit" onclick="document.getElementById('btn-reset-filters').click()">Clear All Filters</button>
        </div>
      `;
      return;
    }

    container.innerHTML = filtered.map(op => {
      const isBookmarked = state.bookmarks.includes(op.id);
      const badgeClass = getBadgeClass(op.type);
      const isClosingSoon = op.closingDays <= 10;
      
      return `
        <div class="opportunity-card" data-id="${op.id}">
          <div class="card-top-bar">
            <div class="type-and-agency">
              <span class="badge-type ${badgeClass}">${op.type}</span>
              <span class="agency-name">
                <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                ${op.agency}
              </span>
            </div>
            <div class="card-actions-top">
              <button class="btn-bookmark ${isBookmarked ? 'bookmarked' : ''}" data-id="${op.id}" title="Save opportunity">
                ${isBookmarked ? '&#9733;' : '&#9734;'}
              </button>
            </div>
          </div>

          <a class="opportunity-title" data-id="${op.id}">${op.title}</a>

          <div class="opportunity-metrics">
            <div class="metric-item">
              <span class="metric-label">Award Range:</span>
              <span class="metric-value amount">$${formatCurrency(op.awardMin)} &ndash; $${formatCurrency(op.awardMax)}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Deadline:</span>
              <span class="metric-value ${isClosingSoon ? 'deadline-closing' : 'deadline-normal'}">
                ${formatDate(op.deadline)} (${op.closingDays} days left)
              </span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Category:</span>
              <span class="metric-value">${op.category}</span>
            </div>
          </div>

          <div class="opportunity-desc">${op.description}</div>

          <div class="opportunity-tags">
            ${op.tags.map(t => `<span class="tag-pill">${t}</span>`).join('')}
            ${op.eligibility.map(e => `<span class="tag-pill" style="background:#e0f2fe; color:#0369a1;">${e}</span>`).join('')}
          </div>

          <div class="card-bottom-bar">
            <div class="location-tag">
              <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/></svg>
              ${op.location}
            </div>
            <div class="card-cta-group">
              <button class="btn-details" data-id="${op.id}">View Details & Scope &rarr;</button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Attach card event listeners (Title click, Bookmark, Details button)
    document.querySelectorAll('.opportunity-title, .btn-details').forEach(el => {
      el.addEventListener('click', (e) => {
        const id = el.dataset.id || el.closest('.opportunity-card').dataset.id;
        openDetailModal(id);
      });
    });

    document.querySelectorAll('.btn-bookmark').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleBookmark(btn.dataset.id);
      });
    });
  }

  // Modal Controllers
  function openModal(modalId) {
    const modal = document.getElementById(`modal-${modalId}`);
    if (modal) {
      modal.classList.add('active');
    }
  }

  function closeModal(modalId) {
    const modal = document.getElementById(`modal-${modalId}`);
    if (modal) {
      modal.classList.remove('active');
    }
  }

  function openDetailModal(id) {
    const op = state.opportunities.find(o => o.id === id);
    if (!op) return;

    state.selectedOpportunity = op;
    
    document.getElementById('md-badge-type').className = `badge-type ${getBadgeClass(op.type)}`;
    document.getElementById('md-badge-type').textContent = op.type;
    document.getElementById('md-title').textContent = op.title;
    document.getElementById('md-amount').textContent = `$${formatCurrency(op.awardMin)} – $${formatCurrency(op.awardMax)}`;
    document.getElementById('md-deadline').textContent = `${formatDate(op.deadline)} (${op.closingDays} days remaining)`;
    document.getElementById('md-agency').textContent = op.agency;
    document.getElementById('md-cfda').textContent = op.cfdaNumber;
    document.getElementById('md-description').textContent = op.description;
    document.getElementById('md-location').textContent = op.location;
    document.getElementById('md-contact').textContent = op.contactEmail;
    document.getElementById('md-portal-link').href = op.portalUrl;

    const elBox = document.getElementById('md-eligibility');
    elBox.innerHTML = op.eligibility.map(e => `<span class="tag-pill" style="background:#e0f2fe; color:#0369a1; font-weight:600;">${e}</span>`).join('');

    openModal('detail');
  }

  // Bookmark Toggle
  function toggleBookmark(id) {
    const idx = state.bookmarks.indexOf(id);
    if (idx >= 0) {
      state.bookmarks.splice(idx, 1);
    } else {
      state.bookmarks.push(id);
    }
    localStorage.setItem('gsl_bookmarks', JSON.stringify(state.bookmarks));
    updateSavedCount();
    renderFeed();
  }

  function updateSavedCount() {
    const countEl = document.getElementById('saved-count');
    if (countEl) {
      countEl.textContent = state.bookmarks.length;
    }
  }

  // Helper Utilities
  function getBadgeClass(type) {
    switch (type.toUpperCase()) {
      case 'GRANT': return 'badge-grant';
      case 'RFQ': return 'badge-rfq';
      case 'RFP': return 'badge-rfp';
      case 'SBIR': return 'badge-sbir';
      case 'CONTRACT': return 'badge-contract';
      default: return 'badge-grant';
    }
  }

  function formatCurrency(val) {
    if (!val) return '0';
    return val.toLocaleString();
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  // Expose global controller if needed
  window.GSLApp = {
    state,
    renderFeed,
    openDetailModal
  };

})();
