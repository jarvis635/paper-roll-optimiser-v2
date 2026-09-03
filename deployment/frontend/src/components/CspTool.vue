<template>
  <div class="main-wrapper">
    <!-- Header / Navigation Bar -->
    <header class="header-card clay-card mb-4">
      <div class="header-content">
        <div class="brand">
          <div class="brand-icon">P</div>
          <div class="brand-text">
            <h1 class="m-0">PLAX Optimiser</h1>
            <p class="brand-subtitle m-0">Cutting Stock & Paper Roll Optimization</p>
          </div>
        </div>

        <!-- Mobile Menu Toggle Button -->
        <button
          class="clay-btn mobile-menu-toggle"
          @click="mobileMenuOpen = !mobileMenuOpen"
          aria-label="Toggle Navigation Menu"
        >
          <span class="hamburger-icon">☰</span>
        </button>

        <!-- Desktop Navigation Bar -->
        <nav class="desktop-nav" role="navigation" aria-label="Main Navigation">
          <div class="clay-nav-pills">
            <button
              v-for="item in navItems"
              :key="item.id"
              class="clay-nav-pill"
              :class="{ active: currentNav === item.id }"
              @click="navigate(item.id)"
              @keydown.enter="navigate(item.id)"
              @keydown.space.prevent="navigate(item.id)"
              tabindex="0"
              :aria-selected="currentNav === item.id"
              role="tab"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span class="nav-label">{{ item.label }}</span>
            </button>
          </div>
        </nav>
      </div>

      <!-- Mobile Navigation Drawer -->
      <transition name="slide-fade">
        <div v-if="mobileMenuOpen" class="mobile-nav-drawer mt-3">
          <div class="mobile-nav-list">
            <button
              v-for="item in navItems"
              :key="item.id"
              class="clay-btn mobile-nav-btn"
              :class="{ active: currentNav === item.id }"
              @click="navigate(item.id); mobileMenuOpen = false;"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </button>
          </div>
        </div>
      </transition>

      <!-- Core Mode System Status Banner -->
      <div v-if="capabilities.coreMode" class="core-mode-badge-bar mt-3 p-2 rounded">
        <span class="clay-badge clay-badge-info">CORE MODE ACTIVE</span>
        <span class="text-xs text-secondary ml-2 font-bold">
          PLAX Optimiser is running in Core Mode. External cloud APIs isolated.
        </span>
      </div>
    </header>

    <!-- Main Content Views Container -->
    <main class="content-container" role="main">
      <!-- Loading State Banner -->
      <div v-if="navLoading" class="clay-card loading-card my-3">
        <div class="loading-spinner"></div>
        <p class="m-0 font-bold">Loading {{ currentNavMeta.label }} view...</p>
      </div>

      <!-- View Route Transitions -->
      <div v-else-if="!navLoading">
        <!-- 1. DASHBOARD VIEW -->
        <div v-if="currentNav === 'dashboard'" class="clay-card">
          <h2>📊 PLAX Operations Dashboard</h2>
          <p class="text-secondary">Real-time overview of cutting stock metrics and optimization efficiency.</p>

          <div class="stats-grid my-4">
            <div class="stat-card">
              <span class="stat-value">128</span>
              <span class="stat-label">Total Jobs Optimized</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">94.8%</span>
              <span class="stat-label">Average Yield / Material Utilization</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">14.2%</span>
              <span class="stat-label">Scrap Waste Reduction</span>
            </div>
          </div>

          <div class="recent-activity mt-4">
            <h3>Recent Activity</h3>
            <table class="clay-table">
              <thead>
                <tr>
                  <th>Job ID</th>
                  <th>Type</th>
                  <th>Rolls Used</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr class="clay-row">
                  <td class="font-bold">#JOB-2041</td>
                  <td>1D Paper Rolls</td>
                  <td>5 Rolls</td>
                  <td><span class="clay-badge clay-badge-success">OPTIMAL</span></td>
                </tr>
                <tr class="clay-row">
                  <td class="font-bold">#JOB-2040</td>
                  <td>2D Sheets</td>
                  <td>1 Sheet</td>
                  <td><span class="clay-badge clay-badge-success">OPTIMAL</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 2. OPTIMISE VIEW (Primary Workflow UI) -->
        <div v-else-if="currentNav === 'optimise'">
          <!-- Mode Tabs (1D vs 2D) -->
          <div class="subnav-row mb-3">
            <div class="clay-nav-pills">
              <button
                class="clay-nav-pill"
                :class="{ active: mode === '1d' }"
                @click="setMode('1d')"
              >
                1D Rolls & Rods
              </button>
              <button
                class="clay-nav-pill"
                :class="{ active: mode === '2d' }"
                @click="setMode('2d')"
              >
                2D Rectangular Sheets
              </button>
            </div>
          </div>

          <!-- Workflow Workspace Grid -->
          <div class="workspace-grid">
            <!-- Manual Input Panel (Left) -->
            <div class="input-panel flex-column gap-4">
              <!-- Step 1: Demand Specifications -->
              <div class="clay-card">
                <div class="card-header-flex mb-3">
                  <div>
                    <div class="flex items-center gap-2 mb-1">
                      <h3 class="m-0">1. Cut Requirements</h3>
                      <span v-if="dataSource === 'sheets'" class="clay-badge clay-badge-info">
                        📊 GOOGLE SHEETS IMPORTED
                      </span>
                      <span v-else class="clay-badge clay-badge-neutral">
                        ✏️ MANUAL ENTRY
                      </span>
                    </div>
                    <p class="text-secondary text-sm m-0">{{ mode_data.childMessage }}</p>
                  </div>
                  <div class="header-actions">
                    <button class="clay-btn text-sm" @click="addRowToChilds">
                      + Add Item
                    </button>
                    <button class="clay-btn clay-btn-danger text-sm" @click="clearChildData(true)">
                      Clear
                    </button>
                  </div>
                </div>

                <div v-if="mode_data.childErrors" class="alert-error mb-3">
                  ⚠️ {{ mode_data.childErrors }}
                </div>
                <div v-if="serverErrorMsg" class="alert-error mb-3 p-2 bg-red-100 rounded">
                  ⚠️ {{ serverErrorMsg }}
                </div>

                <table class="clay-table">
                  <thead>
                    <tr>
                      <th width="8%">#</th>
                      <th width="32%">Width (cm)</th>
                      <th v-if="mode === '2d'" width="32%">Height (cm)</th>
                      <th width="28%">Quantity</th>
                      <th width="10%"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(child, index) in mode_data.childs"
                      :key="index"
                      class="clay-row"
                    >
                      <td class="text-secondary text-center font-bold">{{ index + 1 }}</td>
                      <td>
                        <input
                          type="text"
                          class="clay-input"
                          v-model="child.width"
                          placeholder="Width"
                        />
                      </td>
                      <td v-if="mode === '2d'">
                        <input
                          type="text"
                          class="clay-input"
                          v-model="child.height"
                          placeholder="Height"
                        />
                      </td>
                      <td>
                        <input
                          type="text"
                          class="clay-input"
                          v-model="child.quantity"
                          placeholder="Qty"
                        />
                      </td>
                      <td class="text-center">
                        <button
                          class="clay-btn clay-btn-danger icon-only-btn"
                          @click="removeRow(index, false)"
                        >
                          ×
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Step 2: Parent Stock Dimensions & Strategy -->
              <div class="clay-card mt-4">
                <div class="card-header-flex mb-3">
                  <div>
                    <h3 class="m-0">2. Parent Stock & Constraints</h3>
                    <p class="text-secondary text-sm m-0">{{ mode_data.parentMessage }}</p>
                  </div>
                </div>

                <div v-if="mode_data.parentErrors" class="alert-error mb-3">
                  ⚠️ {{ mode_data.parentErrors }}
                </div>

                <table class="clay-table mb-3">
                  <thead>
                    <tr>
                      <th width="8%">#</th>
                      <th width="32%">Width (cm)</th>
                      <th v-if="mode === '2d'" width="32%">Height (cm)</th>
                      <th width="28%">Quantity</th>
                      <th width="10%"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(parent, index) in mode_data.parents"
                      :key="index"
                      class="clay-row"
                    >
                      <td class="text-secondary text-center font-bold">{{ index + 1 }}</td>
                      <td>
                        <input
                          type="text"
                          class="clay-input"
                          v-model="parent.width"
                          placeholder="Stock Width"
                        />
                      </td>
                      <td v-if="mode === '2d'">
                        <input
                          type="text"
                          class="clay-input"
                          v-model="parent.height"
                          placeholder="Stock Height"
                        />
                      </td>
                      <td>
                        <input
                          disabled
                          type="text"
                          class="clay-input disabled-input"
                          v-model="parent.quantity"
                        />
                      </td>
                      <td class="text-center">
                        <button
                          class="clay-btn clay-btn-danger icon-only-btn"
                          @click="removeRow(index, true)"
                        >
                          ×
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>

                <div v-if="mode === '1d'" class="strategy-selector p-3 rounded">
                  <span class="font-bold text-sm block mb-2">Optimization Objective Strategy:</span>
                  <div class="radio-group">
                    <label class="radio-label">
                      <input
                        type="radio"
                        name="cutStyle"
                        value="exactCuts"
                        v-model="cutStyle"
                      />
                      <span class="radio-custom"></span>
                      <span>Exact Cuts (Strict Demand)</span>
                    </label>

                    <label class="radio-label">
                      <input
                        type="radio"
                        name="cutStyle"
                        value="minWaste"
                        v-model="cutStyle"
                      />
                      <span class="radio-custom"></span>
                      <span>Minimize Waste (Over-cut Allowed)</span>
                    </label>
                  </div>
                </div>
              </div>

              <!-- Action Control Trigger Card -->
              <div class="clay-card mt-4">
                <div class="action-trigger-row">
                  <button
                    class="clay-btn clay-btn-primary optimise-hero-btn"
                    :disabled="cutButtonDisabled"
                    @click="cutSheets()"
                  >
                    <span v-if="!cutButtonDisabled">⚡ OPTIMISE</span>
                    <span v-else class="flex items-center gap-2">
                      <span class="loading-spinner-sm"></span>
                      <span>Running Solver...</span>
                    </span>
                  </button>

                  <button
                    class="clay-btn"
                    :disabled="cutButtonDisabled"
                    @click="reset()"
                  >
                    Reset
                  </button>
                </div>
              </div>
            </div>

            <!-- Output & Detailed Cutting Results (Right) -->
            <div class="output-panel flex-column gap-4">
              <!-- Solver Progress & Execution Status Banner -->
              <div v-if="cutButtonDisabled" class="clay-card progress-banner">
                <div class="progress-status-flex">
                  <div class="loading-spinner"></div>
                  <div>
                    <h4 class="m-0 font-bold">Executing OR-Tools Optimization Engine</h4>
                    <p class="m-0 text-secondary text-sm">Evaluating mathematical capacity constraints and pattern generation...</p>
                  </div>
                </div>
              </div>

              <!-- Results Card -->
              <div v-if="mode_data.result" class="clay-card">
                <div class="card-header-flex mb-3">
                  <div>
                    <h3 class="m-0">Optimised Cutting Plan</h3>
                    <div class="flex items-center gap-2 mt-1">
                      <span class="clay-badge clay-badge-success">
                        STATUS: {{ mode_data.result.statusName }}
                      </span>
                      <span class="text-secondary text-sm font-bold">
                        (Solutions Evaluated: {{ mode_data.result.numSolutions }})
                      </span>
                    </div>
                  </div>

                  <button
                    v-if="mode === '1d'"
                    class="clay-btn text-sm"
                    @click="downloadCsv()"
                  >
                    📥 Export CSV
                  </button>
                </div>

                <!-- Summary Efficiency Metrics Bar -->
                <div class="summary-metrics-grid mb-4">
                  <div class="metric-card">
                    <span class="metric-value">{{ totalStockItemsUsed }}</span>
                    <span class="metric-label">{{ mode === '1d' ? 'Stock Rolls Used' : 'Stock Sheets Used' }}</span>
                  </div>

                  <div class="metric-card">
                    <span class="metric-value text-success">{{ averageYieldPercentage }}%</span>
                    <span class="metric-label">Average Material Utilization</span>
                  </div>

                  <div class="metric-card">
                    <span class="metric-value text-warning">{{ totalWasteAmount }}</span>
                    <span class="metric-label">Total Scrap Waste Length</span>
                  </div>
                </div>

                <!-- Actual Result Visual Diagram -->
                <div class="diagram-section mb-4">
                  <h4 class="m-0 mb-2 text-sm font-bold text-secondary">ACTUAL SOLVER DIAGRAM</h4>
                  <div id="d3_area" class="d3-container">
                    <svg class="w-100"></svg>
                  </div>
                </div>

                <!-- Detailed Cutting Result Breakdown -->
                <div v-if="mode === '1d'" class="breakdown-section mt-4">
                  <h4 class="m-0 mb-2 font-bold">Detailed Cut Breakdown</h4>
                  <table class="clay-table">
                    <thead>
                      <tr>
                        <th width="12%">Roll</th>
                        <th width="28%">Efficiency Yield</th>
                        <th width="40%">Cut Widths</th>
                        <th width="20%">Leftover Waste</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(bigRoll, index) in mode_data.result.solutions"
                        :key="index"
                        class="clay-row"
                      >
                        <td class="text-center font-bold text-secondary">#{{ index + 1 }}</td>
                        <td>
                          <div class="utilization-bar-container">
                            <div
                              class="utilization-bar"
                              :style="{ width: getPercentageUtilization(bigRoll[0]) + '%' }"
                            ></div>
                            <span class="utilization-text">
                              {{ getPercentageUtilization(bigRoll[0]) }}%
                            </span>
                          </div>
                        </td>
                        <td>
                          <span class="cut-pattern-text font-bold">
                            {{ bigRoll[1].join(", ") }}
                          </span>
                        </td>
                        <td class="text-center font-bold text-secondary">
                          {{ Math.round(bigRoll[0] * 100) / 100 }} cm
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- 2D Sheet Breakdown -->
                <div v-if="mode === '2d' && mode_data.result.solutions" class="breakdown-section mt-4">
                  <h4 class="m-0 mb-2 font-bold">2D Rectangle Coordinates Layout</h4>
                  <table class="clay-table">
                    <thead>
                      <tr>
                        <th>Rectangle #</th>
                        <th>Top-Left (x1, y1)</th>
                        <th>Bottom-Right (x2, y2)</th>
                        <th>Dimensions (W × H)</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(rect, index) in mode_data.result.solutions[0]"
                        :key="index"
                        class="clay-row"
                      >
                        <td class="font-bold text-secondary">Item #{{ index + 1 }}</td>
                        <td>({{ rect[0] }}, {{ rect[1] }})</td>
                        <td>({{ rect[2] }}, {{ rect[3] }})</td>
                        <td class="font-bold">{{ rect[2] - rect[0] }} × {{ rect[3] - rect[1] }} cm</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Initial State Prompt prior to running solver -->
              <div v-else-if="!cutButtonDisabled && !mode_data.result" class="clay-card empty-result-prompt p-4 text-center">
                <span class="prompt-icon">⚡</span>
                <h3 class="m-0 my-2">Ready to Optimise</h3>
                <p class="text-secondary text-sm max-w-sm m-0 auto-margin">
                  Enter customer cut requirements and stock roll dimensions on the left, then click <b>⚡ OPTIMISE</b> to calculate minimum stock roll waste.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. ORDERS VIEW -->
        <div v-else-if="currentNav === 'orders'" class="clay-card">
          <div class="card-header-flex mb-3">
            <h2>📦 Customer Orders</h2>
            <button class="clay-btn clay-btn-primary text-sm" @click="navigate('optimise')">
              + Import Order to Optimiser
            </button>
          </div>
          <p class="text-secondary">Manage incoming cutting orders and batch requirements.</p>

          <table class="clay-table mt-3">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Client Name</th>
                <th>Dimensions</th>
                <th>Quantity</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr class="clay-row">
                <td class="font-bold">ORD-9012</td>
                <td>Apex Packaging Ltd</td>
                <td>30cm Roll</td>
                <td>3 Rolls</td>
                <td><span class="clay-badge clay-badge-success">Ready</span></td>
              </tr>
              <tr class="clay-row">
                <td class="font-bold">ORD-9013</td>
                <td>Papercraft Global</td>
                <td>72cm Roll</td>
                <td>2 Rolls</td>
                <td><span class="clay-badge clay-badge-warning">In Queue</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 4. RESULTS VIEW -->
        <div v-else-if="currentNav === 'results'" class="clay-card">
          <h2>📈 Solution & Waste Results</h2>
          <p class="text-secondary">Historical optimization reports and downloadable cutting patterns.</p>

          <div v-if="mode_data && mode_data.result" class="results-summary p-3 my-3">
            <h3>Latest Result Summary</h3>
            <p>Status: <b class="text-success">{{ mode_data.result.statusName }}</b></p>
            <p>Rolls Required: <b>{{ mode_data.result.solutions ? mode_data.result.solutions.length : 0 }}</b></p>
            <button class="clay-btn text-sm" @click="downloadCsv()">Download CSV</button>
          </div>
          <div v-else class="empty-state p-4 text-center">
            <p class="text-secondary">No recent active result in memory. Run the optimizer to view live reports.</p>
            <button class="clay-btn clay-btn-primary" @click="navigate('optimise')">Go to Optimiser</button>
          </div>
        </div>

        <!-- 5. GOOGLE SHEETS VIEW -->
        <div v-else-if="currentNav === 'sheets'" class="clay-card">
          <div class="card-header-flex mb-3">
            <div>
              <h2 class="m-0">📑 Google Sheets Integration</h2>
              <p class="text-secondary text-sm m-0">Connect external spreadsheets as an optional data connector.</p>
            </div>
            <div>
              <span v-if="sheetsConfig.connected" class="clay-badge clay-badge-success">CONNECTED</span>
              <span v-else class="clay-badge clay-badge-warning">DISCONNECTED</span>
            </div>
          </div>

          <!-- Connection Status Card -->
          <div class="sheets-status-card p-4 mb-4 rounded-lg">
            <div class="flex justify-between items-center flex-wrap gap-3">
              <div>
                <span class="text-xs uppercase font-bold text-secondary block mb-1">DATA SOURCE STATUS</span>
                <h3 class="m-0 text-lg flex items-center gap-2">
                  <span v-if="sheetsConfig.connected" class="pulse-dot green-dot"></span>
                  <span v-else class="pulse-dot gray-dot"></span>
                  <span>{{ sheetsConfig.connected ? 'Google Sheets Active' : 'Manual Entry Active (Spreadsheet Disconnected)' }}</span>
                </h3>
              </div>
              <div v-if="sheetsConfig.connected" class="text-right">
                <span class="text-xs text-secondary block font-bold">LAST SYNCED</span>
                <span class="font-bold text-sm">{{ sheetsConfig.lastSyncTime || 'Just now' }}</span>
              </div>
            </div>

            <!-- Connected Metadata Overview -->
            <div v-if="sheetsConfig.connected" class="sheets-meta-grid mt-3 pt-3 border-top">
              <div><b>Sheet ID:</b> <code class="text-xs">{{ sheetsConfig.sheetId }}</code></div>
              <div><b>Tab Name:</b> <span>{{ sheetsConfig.sheetName }}</span></div>
              <div><b>Records Loaded:</b> <span class="font-bold">{{ sheetsConfig.rowsCount }} rows</span></div>
            </div>
          </div>

          <!-- Connecting Animation Overlay / Banner -->
          <div v-if="sheetsState.isConnecting" class="clay-card animation-card my-4 p-4 text-center">
            <div class="pulse-ring-container auto-margin mb-3">
              <div class="pulse-ring"></div>
              <span class="pulse-icon">⚡</span>
            </div>
            <h3 class="m-0 mb-1 font-bold">Connecting to Google Sheets</h3>
            <p class="text-secondary text-sm m-0 mb-3">{{ sheetsState.stepMessage }}</p>
            <div class="connection-progress-bar auto-margin">
              <div class="connection-progress-fill" :style="{ width: (sheetsState.stepNumber * 25) + '%' }"></div>
            </div>
          </div>

          <!-- Success Banner with Check Animation -->
          <div v-if="sheetsState.showSuccessAnim" class="clay-card success-banner my-4 p-4 text-center">
            <div class="success-check-badge auto-margin mb-2">✓</div>
            <h3 class="m-0 text-success font-bold">Google Sheets Connected</h3>
            <p class="text-secondary text-sm m-0 mt-1">Spreadsheet orders mapped and ready to import into Optimiser.</p>
          </div>

          <!-- Error Alert Notice -->
          <div v-if="sheetsState.errorMsg" class="alert-error-card p-3 my-3">
            <div class="flex items-center gap-2">
              <span class="clay-badge clay-badge-danger">CONNECTION ERROR</span>
              <span class="font-bold text-sm">{{ sheetsState.errorMsg }}</span>
            </div>
            <p class="text-secondary text-xs mt-2 m-0">
              Core optimisation remains 100% operational using Manual Entry.
            </p>
          </div>

          <!-- Configuration Form -->
          <div class="clay-card my-3">
            <h3 class="m-0 mb-3">Spreadsheet Configuration</h3>
            <div class="sheets-form flex-column gap-3 max-w-lg">
              <div>
                <label class="font-bold text-sm block mb-1">Google Sheet ID or Shareable Link</label>
                <input
                  type="text"
                  class="clay-input"
                  v-model="sheetsForm.sheetIdInput"
                  placeholder="e.g. 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms or full URL"
                />
                <span class="text-xs text-secondary mt-1 block">Ensure link sharing is set to "Anyone with the link can view".</span>
              </div>

              <div class="form-row-2">
                <div>
                  <label class="font-bold text-sm block mb-1">Sheet / Tab Name</label>
                  <input
                    type="text"
                    class="clay-input"
                    v-model="sheetsForm.sheetNameInput"
                    placeholder="Sheet1"
                  />
                </div>
                <div>
                  <label class="font-bold text-sm block mb-1">Optional Range</label>
                  <input
                    type="text"
                    class="clay-input"
                    v-model="sheetsForm.rangeInput"
                    placeholder="e.g. A1:D50 (Optional)"
                  />
                </div>
              </div>

              <div class="action-trigger-row mt-3">
                <button
                  v-if="!sheetsConfig.connected"
                  class="clay-btn clay-btn-primary"
                  :disabled="sheetsState.isConnecting"
                  @click="connectGoogleSheets"
                >
                  <span v-if="!sheetsState.isConnecting">⚡ Connect Sheet</span>
                  <span v-else>Connecting...</span>
                </button>

                <button
                  v-if="sheetsConfig.connected"
                  class="clay-btn clay-btn-primary"
                  :disabled="sheetsState.isConnecting"
                  @click="syncGoogleSheets"
                >
                  🔄 Sync / Refresh Data
                </button>

                <button
                  v-if="sheetsConfig.connected"
                  class="clay-btn clay-btn-danger"
                  @click="disconnectGoogleSheets"
                >
                  Disconnect Sheet
                </button>

                <button
                  v-if="sheetsConfig.connected"
                  class="clay-btn"
                  @click="importSheetToOptimiser"
                >
                  📥 Load into Optimiser
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 6. ASK PLAXAI VIEW -->
        <div v-else-if="currentNav === 'ai'" class="clay-card">
          <h2>🤖 Ask PLAXAI Assistant</h2>

          <div class="degraded-notice-card p-3 my-3">
            <div class="flex items-center gap-2">
              <span class="clay-badge clay-badge-warning">PLAXAI OFFLINE</span>
              <span class="font-bold text-sm">PLAXAI is unavailable. Core optimisation remains available.</span>
            </div>
            <p class="text-secondary text-sm mt-2 m-0">
              Cloud AI recommendation service is unconfigured or offline. Mathematical cutting stock calculations are processed locally by OR-Tools.
            </p>
            <button class="clay-btn clay-btn-primary text-sm mt-3" @click="navigate('optimise')">
              ⚡ Open Optimiser Workspace
            </button>
          </div>

          <div class="chat-box my-3 p-3">
            <div
              v-for="(msg, idx) in aiMessages"
              :key="idx"
              class="chat-message mb-2"
              :class="msg.sender === 'user' ? 'user-message text-right' : 'ai-message'"
            >
              <b>{{ msg.sender === 'user' ? 'You' : 'PLAXAI' }}:</b> {{ msg.text }}
            </div>
          </div>

          <div class="chat-input-row flex gap-2">
            <input
              type="text"
              class="clay-input"
              v-model="aiQueryInput"
              @keydown.enter="sendAiQuery"
              placeholder="e.g. How can I minimize trim loss on 100cm parent rolls?"
            />
            <button class="clay-btn clay-btn-primary" @click="sendAiQuery">Send</button>
          </div>
        </div>

        <!-- 7. HISTORY VIEW -->
        <div v-else-if="currentNav === 'history'" class="clay-card">
          <h2>📜 Optimization History</h2>
          <p class="text-secondary">Audit log of previously executed cutting stock models.</p>

          <table class="clay-table mt-3">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Model</th>
                <th>Items</th>
                <th>Stock Width</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr class="clay-row">
                <td>Today, 14:32</td>
                <td>1D Small Model</td>
                <td>2 items (3x30, 2x72)</td>
                <td>100</td>
                <td><span class="clay-badge clay-badge-success">OPTIMAL</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 8. SETTINGS VIEW -->
        <div v-else-if="currentNav === 'settings'" class="clay-card">
          <h2>⚙️ System Settings</h2>
          <p class="text-secondary">Configure default optimization constraints and application preferences.</p>

          <div class="settings-list flex-column gap-3 max-w-md my-3">
            <div>
              <label class="font-bold">Default Solver Strategy</label>
              <select class="clay-input mt-1">
                <option>CBC Mixed Integer Programming (MIP)</option>
                <option>GLOP Linear Programming</option>
                <option>CP-SAT Constraint Programming</option>
              </select>
            </div>
            <div>
              <label class="font-bold">Units of Measurement</label>
              <input type="text" class="clay-input mt-1" value="Centimeters (cm)" disabled />
            </div>
          </div>
        </div>

        <!-- 9. HELP / ABOUT VIEW -->
        <div v-else-if="currentNav === 'help'" class="clay-card">
          <h2>ℹ️ Help & About PLAX Optimiser</h2>
          <p class="text-secondary">Paper Roll & Cutting Stock Optimisation Platform v2.0</p>

          <div class="help-info mt-3 flex-column gap-2">
            <p><b>Engine Backend:</b> Google OR-Tools Mathematical Optimiser</p>
            <p><b>Supported Solvers:</b> 1D Column Generation MIP & 2D CP-SAT NoOverlap2D</p>
            <p><b>Documentation:</b> Designed for industrial cutting efficiency and trim loss minimization.</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import * as d3 from "d3";
import axios from "axios";

export default {
  name: "CspTool",
  data() {
    return {
      currentNav: "optimise",
      navLoading: false,
      mobileMenuOpen: false,

      capabilities: {
        sheetsConnected: false,
        aiConnected: false,
        serverConnected: true,
        coreMode: true,
      },

      serverErrorMsg: null,

      dataSource: "manual", // "manual" or "sheets"

      sheetsForm: {
        sheetIdInput: "",
        sheetNameInput: "Sheet1",
        rangeInput: "",
      },

      sheetsConfig: {
        connected: false,
        sheetId: "",
        sheetName: "Sheet1",
        range: "",
        lastSyncTime: null,
        rowsCount: 0,
        dataPayload: null,
      },

      sheetsState: {
        isConnecting: false,
        stepNumber: 0,
        stepMessage: "",
        showSuccessAnim: false,
        errorMsg: null,
      },

      aiQueryInput: "",
      aiMessages: [
        {
          sender: "ai",
          text: "PLAXAI is unavailable. Core optimisation remains available.",
        },
      ],

      navItems: [
        { id: "dashboard", label: "Dashboard", icon: "📊" },
        { id: "optimise", label: "Optimise", icon: "⚡" },
        { id: "orders", label: "Orders", icon: "📦" },
        { id: "results", label: "Results", icon: "📈" },
        { id: "sheets", label: "Google Sheets", icon: "📑" },
        { id: "ai", label: "Ask PLAXAI", icon: "🤖" },
        { id: "history", label: "History", icon: "📜" },
        { id: "settings", label: "Settings", icon: "⚙️" },
        { id: "help", label: "Help / About", icon: "ℹ️" },
      ],

      mode: "1d",
      cutStyle: "exactCuts",
      cutButtonDisabled: false,

      mode1d: {
        childs: [{ width: "30", quantity: "3" }, { width: "72", quantity: "2" }],
        parents: [{ width: "100", quantity: "Auto" }],
        childErrors: null,
        parentErrors: null,
        result: null,
        childMessage: "Specify cut length (cm) and required quantity",
        parentTitle: "Stock Roll Specification",
        parentMessage: "Parent stock roll width (cm)",
      },

      mode2d: {
        childs: [{ width: "27", height: "17", quantity: "2" }],
        parents: [{ width: "84", height: "72", quantity: "Auto" }],
        childErrors: null,
        parentErrors: null,
        result: null,
        childMessage: "Specify dimensions (W × H cm) and quantity",
        parentTitle: "Parent Sheet Stock",
        parentMessage: "Specify stock sheet width and height (cm)",
      },

      mode_data: null,

      colors: [
        "#4a6fa5", "#3b8256", "#d97706", "#8b5cf6",
        "#ec4899", "#06b6d4", "#10b981", "#f59e0b"
      ],
      wasteColor: "#a3a8a4",
    };
  },

  computed: {
    currentNavMeta() {
      return this.navItems.find(i => i.id === this.currentNav) || { label: "View" };
    },

    totalStockItemsUsed() {
      if (!this.mode_data?.result?.solutions) return 0;
      return this.mode_data.result.solutions.length;
    },

    averageYieldPercentage() {
      if (!this.mode_data?.result?.solutions || !this.mode_data.result.solutions.length) return 0;
      const pWidth = parseInt(this.mode_data.parents[0].width) || 1;
      let totalYield = 0;
      this.mode_data.result.solutions.forEach(roll => {
        const unused = roll[0];
        const yieldPct = ((pWidth - unused) * 100) / pWidth;
        totalYield += yieldPct;
      });
      return Math.round((totalYield / this.mode_data.result.solutions.length) * 10) / 10;
    },

    totalWasteAmount() {
      if (!this.mode_data?.result?.solutions) return "0 cm";
      let totalWaste = 0;
      this.mode_data.result.solutions.forEach(roll => {
        totalWaste += roll[0];
      });
      return `${Math.round(totalWaste * 10) / 10} cm`;
    }
  },

  beforeMount() {
    this.setMode("1d");
  },

  methods: {
    navigate(navId) {
      if (this.currentNav === navId) return;
      this.navLoading = true;
      this.currentNav = navId;

      setTimeout(() => {
        this.navLoading = false;
        if (navId === "optimise") {
          this.$nextTick(() => {
            if (this.mode === "1d") this.draw1d();
            else this.draw2d();
          });
        }
      }, 150);
    },

    setMode(newMode) {
      this.mode = newMode;
      if (newMode === "1d") {
        if (this.mode_data != null) this.mode2d = this.mode_data;
        this.mode_data = this.mode1d;
        this.draw1d();
      } else if (newMode === "2d") {
        if (this.mode_data != null) this.mode1d = this.mode_data;
        this.mode_data = this.mode2d;
        this.draw2d();
      }
    },

    addRowToChilds() {
      if (this.mode === "1d") {
        this.mode_data.childs.push({ width: "", quantity: "" });
      } else {
        this.mode_data.childs.push({ width: "", height: "", quantity: "" });
      }
    },

    clearChildData(askConfirm = true) {
      if (askConfirm) {
        if (!confirm("Clear all items in demand table?")) return;
      }
      this.mode_data.childs = this.mode === "1d"
        ? [{ width: "", quantity: "" }]
        : [{ width: "", height: "", quantity: "" }];
      this.mode_data.childErrors = null;
      this.mode_data.result = null;
      this.clearTheDrawing();
    },

    clearParentData(askConfirm = true) {
      if (askConfirm) {
        if (!confirm("Reset stock parameters?")) return;
      }
      this.mode_data.parents = this.mode === "1d"
        ? [{ width: "", quantity: "Auto" }]
        : [{ width: "", height: "", quantity: "Auto" }];
      this.mode_data.parentErrors = null;
      this.mode_data.result = null;
      this.clearTheDrawing();
    },

    removeRow(idx, is_parent) {
      if (is_parent) {
        this.clearParentData(false);
        return;
      }
      if (this.mode_data.childs.length > 1) {
        this.mode_data.childs.splice(idx, 1);
      } else {
        this.clearChildData(false);
      }
    },

    cutSheets() {
      this.hideErrorMsgs();
      this.clearTheDrawing();

      if (!this.validate()) return;

      this.sendReq();
    },

    validate() {
      this.hideErrorMsgs();
      const labels = this.mode === "2d" ? ["width", "height", "quantity"] : ["width", "quantity"];

      for (let i = 0; i < this.mode_data.childs.length; i++) {
        const child = this.mode_data.childs[i];
        for (let j = 0; j < labels.length; j++) {
          const val = parseInt(child[labels[j]]);
          if (!Number.isInteger(val) || val < 1) {
            this.mode_data.childErrors = `Item Row #${i + 1}: ${labels[j]} must be a positive integer.`;
            return false;
          }
        }
      }

      for (let i = 0; i < this.mode_data.parents.length; i++) {
        const parent = this.mode_data.parents[i];
        for (let j = 0; j < labels.length - 1; j++) {
          const val = parseInt(parent[labels[j]]);
          if (!Number.isInteger(val) || val < 1) {
            this.mode_data.parentErrors = `Stock Row #${i + 1}: ${labels[j]} must be a positive integer.`;
            return false;
          }
        }
      }

      return true;
    },

    hideErrorMsgs() {
      this.mode_data.childErrors = null;
      this.mode_data.parentErrors = null;
    },

    prepareDataToSend1D() {
      const newChilds = this.mode_data.childs.map((c) => [parseInt(c.quantity), parseInt(c.width)]);
      const newParents = this.mode_data.parents.map((p) => [10, parseInt(p.width)]);
      return { child_rolls: newChilds, parent_rolls: newParents, cutStyle: this.cutStyle };
    },

    prepareDataToSend2D() {
      const newChilds = [];
      this.mode_data.childs.forEach((child) => {
        const q = parseInt(child.quantity);
        const item = [parseInt(child.width), parseInt(child.height)];
        for (let i = 0; i < q; i++) newChilds.push(item);
      });
      const newParents = [[parseInt(this.mode_data.parents[0].width), parseInt(this.mode_data.parents[0].height)]];
      return { child_rects: newChilds, parent_rects: newParents };
    },

    connectGoogleSheets() {
      this.sheetsState.errorMsg = null;
      this.sheetsState.showSuccessAnim = false;

      if (!this.sheetsForm.sheetIdInput.trim()) {
        this.sheetsState.errorMsg = "Invalid Sheet ID. Please enter a valid Google Sheet ID or URL.";
        return;
      }

      const url = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
        ? "http://localhost:5000/sheets/fetch"
        : "/sheets/fetch";

      this.sheetsState.isConnecting = true;
      this.sheetsState.stepNumber = 1;
      this.sheetsState.stepMessage = "Validating Sheet ID and configuration...";

      setTimeout(() => {
        this.sheetsState.stepNumber = 2;
        this.sheetsState.stepMessage = "Testing server connection...";

        axios.post(url, {
          sheet_id: this.sheetsForm.sheetIdInput,
          sheet_name: this.sheetsForm.sheetNameInput || "Sheet1",
          range: this.sheetsForm.rangeInput,
        })
          .then((response) => {
            this.sheetsState.stepNumber = 3;
            this.sheetsState.stepMessage = "Retrieving metadata & parsing structure...";

            setTimeout(() => {
              this.sheetsState.stepNumber = 4;
              this.sheetsState.stepMessage = "Mapping rows to application input model...";

              setTimeout(() => {
                this.sheetsState.isConnecting = false;
                if (response.data.status === "success") {
                  const now = new Date();
                  this.sheetsConfig.connected = true;
                  this.sheetsConfig.sheetId = response.data.sheet_id;
                  this.sheetsConfig.sheetName = response.data.sheet_name;
                  this.sheetsConfig.range = this.sheetsForm.rangeInput;
                  this.sheetsConfig.lastSyncTime = now.toLocaleTimeString();
                  this.sheetsConfig.rowsCount = response.data.rows_count;
                  this.sheetsConfig.dataPayload = response.data;

                  this.capabilities.sheetsConnected = true;
                  this.sheetsState.showSuccessAnim = true;

                  setTimeout(() => {
                    this.sheetsState.showSuccessAnim = false;
                  }, 4000);
                } else {
                  this.sheetsState.errorMsg = response.data.message || "Failed to connect to Google Sheets.";
                }
              }, 300);
            }, 300);
          })
          .catch((error) => {
            this.sheetsState.isConnecting = false;
            if (error.response && error.response.data && error.response.data.message) {
              this.sheetsState.errorMsg = error.response.data.message;
            } else {
              this.sheetsState.errorMsg = "Network unavailable. Please verify connection and backend service.";
            }
          });
      }, 300);
    },

    syncGoogleSheets() {
      if (!this.sheetsConfig.connected) return;
      this.connectGoogleSheets();
    },

    disconnectGoogleSheets() {
      this.sheetsConfig.connected = false;
      this.sheetsConfig.dataPayload = null;
      this.capabilities.sheetsConnected = false;
      this.sheetsState.showSuccessAnim = false;
      this.sheetsState.errorMsg = null;
      this.dataSource = "manual";
    },

    importSheetToOptimiser() {
      if (!this.sheetsConfig.dataPayload) {
        this.sheetsState.errorMsg = "No sheet data loaded. Please connect a spreadsheet first.";
        return;
      }

      if (this.mode_data.childs && this.mode_data.childs.length > 0) {
        const hasCustomData = this.mode_data.childs.some(c => c.width && c.width !== "30" && c.width !== "27");
        if (hasCustomData) {
          if (!confirm("Import data from Google Sheets? (This will update the Optimiser input fields)")) {
            return;
          }
        }
      }

      const payload = this.sheetsConfig.dataPayload;

      if (this.mode === "1d") {
        if (payload.child_rolls && payload.child_rolls.length) {
          this.mode1d.childs = payload.child_rolls.map(r => ({ quantity: String(r[0]), width: String(r[1]) }));
        }
        if (payload.parent_rolls && payload.parent_rolls.length) {
          this.mode1d.parents = payload.parent_rolls.map(r => ({ quantity: "Auto", width: String(r[1]) }));
        }
      } else {
        if (payload.child_rects && payload.child_rects.length) {
          // Group 2d child rects by dimension
          const counts = {};
          payload.child_rects.forEach(r => {
            const key = `${r[0]}x${r[1]}`;
            if (!counts[key]) counts[key] = { width: String(r[0]), height: String(r[1]), quantity: 0 };
            counts[key].quantity += 1;
          });
          this.mode2d.childs = Object.values(counts).map(item => ({
            width: item.width,
            height: item.height,
            quantity: String(item.quantity)
          }));
        }
        if (payload.parent_rects && payload.parent_rects.length) {
          this.mode2d.parents = [{ width: String(payload.parent_rects[0][0]), height: String(payload.parent_rects[0][1]), quantity: "Auto" }];
        }
      }

      this.dataSource = "sheets";
      this.navigate("optimise");
    },

    sendAiQuery() {
      if (!this.aiQueryInput.trim()) return;
      const query = this.aiQueryInput;
      this.aiMessages.push({ sender: "user", text: query });
      this.aiQueryInput = "";
      setTimeout(() => {
        this.aiMessages.push({
          sender: "ai",
          text: "PLAXAI is unavailable. Core optimisation remains available.",
        });
      }, 300);
    },

    sendReq() {
      this.serverErrorMsg = null;
      const endpoint = this.mode === "1d" ? "/stocks_1d" : "/stocks_2d";
      const url = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
        ? `http://localhost:5000${endpoint}`
        : endpoint;

      this.cutButtonDisabled = true;
      const payload = this.mode === "1d" ? this.prepareDataToSend1D() : this.prepareDataToSend2D();

      axios.post(url, payload)
        .then((response) => {
          this.cutButtonDisabled = false;
          this.capabilities.serverConnected = true;
          this.displayResult(response.data);
        })
        .catch((error) => {
          this.cutButtonDisabled = false;
          this.capabilities.serverConnected = false;
          this.serverErrorMsg = "Optimisation server is currently unavailable. Please ensure the Python OR-Tools backend service is running.";
          console.error("Optimization Server Request Error:", error);
        });
    },

    displayResult(data) {
      if (typeof data === "string") {
        data = JSON.parse(data);
      }
      this.mode_data.result = data;
      this.$nextTick(() => {
        if (this.mode === "1d") {
          this.draw1d();
        } else {
          this.draw2d();
        }
      });
    },

    sortBigRolls(bigRolls) {
      return bigRolls.sort((a, b) => a[0] - b[0]).map((roll) => [roll[0], roll[1].sort((x, y) => x - y)]);
    },

    clearTheDrawing() {
      d3.selectAll("#d3_area svg > *").remove();
    },

    draw1d() {
      this.clearTheDrawing();
      if (!this.mode_data.result) return;

      const bigRolls = this.sortBigRolls(this.mode_data.result.solutions);
      this.mode_data.result.solutions = bigRolls;

      const parentWidth = parseInt(this.mode_data.parents[0].width);
      const containerWidth = document.getElementById("d3_area")?.clientWidth || 400;

      const xScale = d3.scaleLinear().domain([0, parentWidth]).range([0, containerWidth - 20]);
      const yScale = d3.scaleBand().domain(d3.range(bigRolls.length)).range([0, 45 * bigRolls.length]).padding(0.2);

      const svg = d3.select("#d3_area svg")
        .attr("width", containerWidth)
        .attr("height", Math.max(120, 45 * bigRolls.length + 20));

      const colorDict = this.getColorDict();

      bigRolls.forEach((bigRoll, i) => {
        const unusedWidth = bigRoll[0];
        const smallRolls = bigRoll[1];
        let xPos = 10;
        const yPos = yScale(i);

        smallRolls.forEach((smallRoll) => {
          const width = xScale(smallRoll);
          const g = svg.append("g").attr("transform", `translate(${xPos},${yPos})`);

          g.append("rect")
            .attr("fill", colorDict[smallRoll] || "#4a6fa5")
            .attr("width", Math.max(1, width - 2))
            .attr("height", yScale.bandwidth())
            .attr("rx", 6);

          if (width > 24) {
            g.append("text")
              .attr("fill", "white")
              .attr("x", width / 2)
              .attr("y", yScale.bandwidth() / 2)
              .attr("text-anchor", "middle")
              .attr("dy", "0.35em")
              .style("font-size", "12px")
              .style("font-weight", "600")
              .text(smallRoll);
          }

          xPos += width;
        });

        if (unusedWidth > 0) {
          const width = xScale(unusedWidth);
          const g = svg.append("g").attr("transform", `translate(${xPos},${yPos})`);

          g.append("rect")
            .attr("fill", this.wasteColor)
            .attr("width", Math.max(1, width - 2))
            .attr("height", yScale.bandwidth())
            .attr("rx", 6);

          if (width > 24) {
            g.append("text")
              .attr("fill", "white")
              .attr("x", width / 2)
              .attr("y", yScale.bandwidth() / 2)
              .attr("text-anchor", "middle")
              .attr("dy", "0.35em")
              .style("font-size", "11px")
              .text(Math.round(unusedWidth));
          }
        }
      });
    },

    draw2d() {
      this.clearTheDrawing();
      if (!this.mode_data.result || !this.mode_data.result.solutions.length) return;

      const sol = this.mode_data.result.solutions[0];
      const parentWidth = parseInt(this.mode_data.parents[0].width);
      const parentHeight = parseInt(this.mode_data.parents[0].height);
      const containerWidth = document.getElementById("d3_area")?.clientWidth || 400;

      const scale = (containerWidth - 40) / parentWidth;
      const svgHeight = parentHeight * scale + 40;

      const svg = d3.select("#d3_area svg")
        .attr("width", containerWidth)
        .attr("height", svgHeight);

      sol.forEach((rect, idx) => {
        const x1 = rect[0] * scale + 20;
        const y1 = rect[1] * scale + 20;
        const w = (rect[2] - rect[0]) * scale;
        const h = (rect[3] - rect[1]) * scale;

        const g = svg.append("g").attr("transform", `translate(${x1},${y1})`);

        g.append("rect")
          .attr("width", w - 2)
          .attr("height", h - 2)
          .attr("fill", this.colors[idx % this.colors.length])
          .attr("rx", 6);

        if (w > 30 && h > 20) {
          g.append("text")
            .attr("fill", "white")
            .attr("x", w / 2)
            .attr("y", h / 2)
            .attr("text-anchor", "middle")
            .attr("dy", "0.35em")
            .style("font-size", "11px")
            .style("font-weight", "600")
            .text(`${rect[2] - rect[0]}×${rect[3] - rect[1]}`);
        }
      });
    },

    getColorDict() {
      if (!this.mode_data.result) return {};
      const bigRolls = this.mode_data.result.solutions;
      const uniqueRolls = Array.from(new Set(bigRolls.flatMap((r) => r[1])));
      const dict = {};
      uniqueRolls.forEach((r, i) => {
        dict[r] = this.colors[i % this.colors.length];
      });
      return dict;
    },

    getPercentageUtilization(unusedWidth) {
      const pWidth = parseInt(this.mode_data.parents[0].width);
      const used = pWidth - unusedWidth;
      return Math.round(((used * 100) / pWidth) * 100) / 100;
    },

    reset() {
      if (!confirm("Reset inputs to default?")) return;
      this.clearChildData(false);
      this.clearParentData(false);
    },

    downloadCsv() {
      if (!this.mode_data.result || !this.mode_data.result.solutions) return;

      const rows = [["Stock Roll", "Utilization %", "Cut Pattern Widths"]];
      this.mode_data.result.solutions.forEach((roll, idx) => {
        rows.push([idx + 1, `${this.getPercentageUtilization(roll[0])}%`, `"${roll[1].join(",")}"`]);
      });

      const csvContent = "data:text/csv;charset=utf-8," + rows.map((e) => e.join(",")).join("\n");
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `PLAX_Optimiser_Cuts_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
  },
};
</script>

<style scoped>
.main-wrapper {
  max-width: 1280px;
  margin: 0 auto;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-icon {
  width: 44px;
  height: 44px;
  background: var(--accent-primary);
  color: white;
  font-size: 1.5rem;
  font-weight: 800;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--clay-shadow-sm);
}

.brand-subtitle {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.desktop-nav {
  display: flex;
}

.mobile-menu-toggle {
  display: none;
}

@media (max-width: 1024px) {
  .desktop-nav {
    display: none;
  }
  .mobile-menu-toggle {
    display: inline-flex;
  }
}

.mobile-nav-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mobile-nav-btn {
  justify-content: flex-start;
  width: 100%;
}

.mobile-nav-btn.active {
  background: var(--accent-primary);
  color: white;
}

.nav-icon {
  margin-right: 6px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: var(--bg-stone-subtle);
  padding: 18px;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  box-shadow: var(--clay-shadow-inset);
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--accent-primary);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.loading-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 30px;
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--bg-stone-subtle);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.subnav-row {
  display: flex;
  justify-content: flex-start;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 900px) {
  .workspace-grid {
    grid-template-columns: 1fr;
  }
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.icon-only-btn {
  padding: 4px 10px;
  border-radius: 8px;
}

.strategy-selector {
  background: rgba(255, 255, 255, 0.4);
  border-radius: var(--radius-sm);
  box-shadow: var(--clay-shadow-inset);
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

.action-trigger-row {
  display: flex;
  gap: 12px;
}

.optimise-hero-btn {
  flex: 1;
  padding: 14px 24px;
  font-size: 1.1rem;
  font-weight: 800;
  letter-spacing: 0.05em;
}

.progress-banner {
  background: #edf3fc;
  border: 1px solid rgba(74, 111, 165, 0.3);
}

.progress-status-flex {
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.metric-card {
  background: var(--bg-stone-subtle);
  padding: 14px;
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  box-shadow: var(--clay-shadow-inset);
  text-align: center;
}

.metric-value {
  font-size: 1.4rem;
  font-weight: 800;
}

.metric-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.utilization-bar-container {
  position: relative;
  height: 20px;
  background: var(--bg-stone-subtle);
  border-radius: 10px;
  overflow: hidden;
}

.utilization-bar {
  height: 100%;
  background: var(--accent-success);
  border-radius: 10px;
}

.utilization-text {
  position: absolute;
  right: 8px;
  top: 1px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-primary);
}

.d3-container {
  background: rgba(255, 255, 255, 0.4);
  border-radius: var(--radius-md);
  padding: 12px;
  box-shadow: var(--clay-shadow-inset);
  min-height: 140px;
}

.alert-error {
  color: var(--accent-danger);
  font-size: 0.85rem;
  font-weight: 600;
}

.disabled-input {
  opacity: 0.6;
}

.empty-result-prompt {
  background: var(--clay-bg);
}

.prompt-icon {
  font-size: 2rem;
  display: block;
}

.auto-margin {
  margin-left: auto;
  margin-right: auto;
}

.core-mode-badge-bar {
  background: rgba(74, 111, 165, 0.08);
  border: 1px dashed rgba(74, 111, 165, 0.4);
  display: flex;
  align-items: center;
}

.degraded-notice-card {
  background: var(--bg-stone-subtle);
  border-left: 4px solid #d97706;
  border-radius: var(--radius-sm);
  box-shadow: var(--clay-shadow-inset);
}

.sheets-status-card {
  background: var(--bg-stone-subtle);
  box-shadow: var(--clay-shadow-inset);
}

.sheets-meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  font-size: 0.85rem;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.green-dot {
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.gray-dot {
  background: #9ca3af;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 600px) {
  .form-row-2 {
    grid-template-columns: 1fr;
  }
}

.animation-card {
  background: rgba(74, 111, 165, 0.05);
  border: 1px solid rgba(74, 111, 165, 0.2);
}

.pulse-ring-container {
  position: relative;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pulse-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(74, 111, 165, 0.3);
  animation: pulse-ring-anim 1.4s infinite ease-out;
}

@keyframes pulse-ring-anim {
  0% { transform: scale(0.8); opacity: 0.9; }
  100% { transform: scale(1.6); opacity: 0; }
}

.pulse-icon {
  font-size: 1.5rem;
  z-index: 1;
}

.connection-progress-bar {
  width: 200px;
  height: 6px;
  background: rgba(0, 0, 0, 0.08);
  border-radius: 3px;
  overflow: hidden;
}

.connection-progress-fill {
  height: 100%;
  background: var(--accent-primary);
  transition: width 0.3s ease;
}

.success-banner {
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.success-check-badge {
  width: 42px;
  height: 42px;
  background: #10b981;
  color: white;
  border-radius: 50%;
  font-size: 1.4rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.alert-error-card {
  background: rgba(220, 38, 38, 0.08);
  border-left: 4px solid var(--accent-danger);
  border-radius: var(--radius-sm);
}

.clay-badge-neutral {
  background: var(--bg-stone-subtle);
  color: var(--text-secondary);
}
</style>
