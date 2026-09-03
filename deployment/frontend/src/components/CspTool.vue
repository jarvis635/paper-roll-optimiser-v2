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

        <!-- 2. OPTIMISE VIEW (Primary Solver UI) -->
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

          <!-- Workspace Grid -->
          <div class="workspace-grid">
            <!-- Input Panel (Left) -->
            <div class="input-panel flex-column gap-4">
              <!-- Demand Items Card -->
              <div class="clay-card">
                <div class="card-header-flex mb-3">
                  <div>
                    <h3 class="m-0">{{ mode_data.childTitle }}</h3>
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
                  {{ mode_data.childErrors }}
                </div>

                <table class="clay-table">
                  <thead>
                    <tr>
                      <th width="8%">#</th>
                      <th width="32%">Width</th>
                      <th v-if="mode === '2d'" width="32%">Height</th>
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
                          placeholder="e.g. 30"
                        />
                      </td>
                      <td v-if="mode === '2d'">
                        <input
                          type="text"
                          class="clay-input"
                          v-model="child.height"
                          placeholder="e.g. 20"
                        />
                      </td>
                      <td>
                        <input
                          type="text"
                          class="clay-input"
                          v-model="child.quantity"
                          placeholder="e.g. 5"
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

              <!-- Stock Settings Card -->
              <div class="clay-card mt-4">
                <div class="card-header-flex mb-3">
                  <div>
                    <h3 class="m-0">{{ mode_data.parentTitle }}</h3>
                    <p class="text-secondary text-sm m-0">{{ mode_data.parentMessage }}</p>
                  </div>
                </div>

                <div v-if="mode_data.parentErrors" class="alert-error mb-3">
                  {{ mode_data.parentErrors }}
                </div>

                <table class="clay-table">
                  <thead>
                    <tr>
                      <th width="8%">#</th>
                      <th width="32%">Width</th>
                      <th v-if="mode === '2d'" width="32%">Height</th>
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
                          placeholder="e.g. 100"
                        />
                      </td>
                      <td v-if="mode === '2d'">
                        <input
                          type="text"
                          class="clay-input"
                          v-model="parent.height"
                          placeholder="e.g. 100"
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
              </div>
            </div>

            <!-- Control & Visualization Panel (Right) -->
            <div class="output-panel flex-column gap-4">
              <!-- Controls & Optimise Actions -->
              <div class="clay-card">
                <div class="controls-row mb-3">
                  <div class="radio-group">
                    <label class="radio-label">
                      <input
                        type="radio"
                        name="cutStyle"
                        value="exactCuts"
                        v-model="cutStyle"
                      />
                      <span class="radio-custom"></span>
                      <span>Exact Cuts</span>
                    </label>

                    <label class="radio-label">
                      <input
                        type="radio"
                        name="cutStyle"
                        value="minWaste"
                        v-model="cutStyle"
                      />
                      <span class="radio-custom"></span>
                      <span>Minimize Waste</span>
                    </label>
                  </div>

                  <div class="action-btns">
                    <button
                      class="clay-btn clay-btn-primary"
                      :disabled="cutButtonDisabled"
                      @click="cutSheets()"
                    >
                      <b>⚡ Run Optimiser</b>
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

              <!-- Result Status & Visualization Container -->
              <div class="clay-card">
                <div class="card-header-flex mb-3" v-if="mode_data.result">
                  <div>
                    <h3 class="m-0">Optimization Plan</h3>
                    <span class="clay-badge clay-badge-success mt-1">
                      {{ mode_data.result.statusName }}
                    </span>
                  </div>
                  <button
                    v-if="mode === '1d'"
                    class="clay-btn text-sm"
                    @click="downloadCsv()"
                  >
                    📥 Export CSV
                  </button>
                </div>

                <div id="d3_area" class="d3-container my-3">
                  <svg class="w-100"></svg>
                </div>

                <!-- Cut Details Table for 1D -->
                <div v-if="mode_data.result && mode === '1d'" class="mt-4">
                  <div class="summary-metrics mb-3">
                    <div class="metric-pill">
                      <span class="metric-label">Required Stock</span>
                      <span class="metric-value">{{ mode_data.result.solutions.length }} rolls</span>
                    </div>
                  </div>

                  <table class="clay-table">
                    <thead>
                      <tr>
                        <th width="15%">Stock Roll</th>
                        <th width="25%">Utilization</th>
                        <th width="60%">Cut Pattern (Widths)</th>
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
                          <span class="cut-pattern-text">
                            {{ bigRoll[1].join(", ") }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
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
          <h2>📊 Google Sheets Integration</h2>
          <p class="text-secondary">Import demand schedules directly from Google Drive spreadsheet URLs.</p>

          <div class="sheets-form flex-column gap-3 max-w-md my-3">
            <label class="font-bold">Spreadsheet URL</label>
            <input type="text" class="clay-input" placeholder="https://docs.google.com/spreadsheets/d/..." />
            <div class="action-btns">
              <button class="clay-btn clay-btn-primary">Connect & Import Data</button>
            </div>
          </div>
        </div>

        <!-- 6. ASK PLAXAI VIEW -->
        <div v-else-if="currentNav === 'ai'" class="clay-card">
          <h2>🤖 Ask PLAXAI Assistant</h2>
          <p class="text-secondary">AI Optimization Assistant for paper roll cutting strategy recommendations.</p>

          <div class="chat-box my-3 p-3">
            <div class="chat-message ai-message mb-2">
              <b>PLAXAI:</b> Hello! I can help you analyze scrap reduction and suggest optimal stock widths. What is your question?
            </div>
          </div>

          <div class="chat-input-row flex gap-2">
            <input type="text" class="clay-input" placeholder="e.g. How can I minimize trim loss on 100cm parent rolls?" />
            <button class="clay-btn clay-btn-primary">Send</button>
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
        childTitle: "Small Rolls & Cut Demands",
        childMessage: "Specify target width and required quantity for 1D cutting",
        parentTitle: "Parent Stock Roll",
        parentMessage: "Parent stock roll length",
      },

      mode2d: {
        childs: [{ width: "27", height: "17", quantity: "2" }],
        parents: [{ width: "84", height: "72", quantity: "Auto" }],
        childErrors: null,
        parentErrors: null,
        result: null,
        childTitle: "Small Rectangular Sheets",
        childMessage: "Specify dimensions (W × H) and quantity",
        parentTitle: "Parent Sheet Stock",
        parentMessage: "Specify stock sheet width and height",
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
            this.mode_data.childErrors = `Row #${i + 1}: ${labels[j]} must be at least 1 unit.`;
            return false;
          }
        }
      }

      for (let i = 0; i < this.mode_data.parents.length; i++) {
        const parent = this.mode_data.parents[i];
        for (let j = 0; j < labels.length - 1; j++) {
          const val = parseInt(parent[labels[j]]);
          if (!Number.isInteger(val) || val < 1) {
            this.mode_data.parentErrors = `Stock Row #${i + 1}: ${labels[j]} must be at least 1 unit.`;
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

    sendReq() {
      const endpoint = this.mode === "1d" ? "/stocks_1d" : "/stocks_2d";
      const url = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
        ? `http://localhost:5000${endpoint}`
        : endpoint;

      this.cutButtonDisabled = true;
      const payload = this.mode === "1d" ? this.prepareDataToSend1D() : this.prepareDataToSend2D();

      axios.post(url, payload)
        .then((response) => {
          this.cutButtonDisabled = false;
          this.displayResult(response.data);
        })
        .catch((error) => {
          this.cutButtonDisabled = false;
          console.error("Optimization Server Request Error:", error);
        });
    },

    displayResult(data) {
      if (typeof data === "string") {
        data = JSON.parse(data);
      }
      this.mode_data.result = data;
      if (this.mode === "1d") {
        this.draw1d();
      } else {
        this.draw2d();
      }
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
  width: 24px;
  height: 24px;
  border: 3px solid var(--bg-stone-subtle);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
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

.controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
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

.action-btns {
  display: flex;
  gap: 10px;
}

.summary-metrics {
  display: flex;
  gap: 12px;
}

.metric-pill {
  background: var(--bg-stone-subtle);
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  display: flex;
  gap: 8px;
  align-items: center;
}

.metric-label {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.metric-value {
  font-weight: 700;
  color: var(--text-primary);
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
</style>
