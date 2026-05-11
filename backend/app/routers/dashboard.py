from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])


@router.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Ad Quality Automation Platform</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f6f7f9;
        --panel: #ffffff;
        --panel-border: #d9dee7;
        --text: #182230;
        --muted: #667085;
        --accent: #0f766e;
        --accent-dark: #115e59;
        --danger: #b42318;
        --warning-bg: #fff7ed;
        --warning-border: #fed7aa;
        --code: #101828;
      }

      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: var(--bg);
        color: var(--text);
      }

      header {
        border-bottom: 1px solid var(--panel-border);
        background: var(--panel);
      }

      .wrap {
        width: min(1180px, calc(100vw - 32px));
        margin: 0 auto;
      }

      .topbar {
        min-height: 76px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
      }

      h1 {
        margin: 0;
        font-size: 22px;
        font-weight: 760;
        letter-spacing: 0;
      }

      .subtitle {
        margin: 4px 0 0;
        color: var(--muted);
        font-size: 14px;
      }

      .docs-link {
        color: var(--accent);
        text-decoration: none;
        font-weight: 650;
        white-space: nowrap;
      }

      main {
        padding: 24px 0 40px;
      }

      .layout {
        display: grid;
        grid-template-columns: minmax(360px, 460px) 1fr;
        gap: 20px;
        align-items: start;
      }

      .panel {
        background: var(--panel);
        border: 1px solid var(--panel-border);
        border-radius: 8px;
      }

      .panel-header {
        padding: 16px 18px;
        border-bottom: 1px solid var(--panel-border);
      }

      .panel-title {
        margin: 0;
        font-size: 16px;
        font-weight: 720;
      }

      .panel-body {
        padding: 18px;
      }

      .steps {
        display: grid;
        gap: 10px;
      }

      .step {
        display: grid;
        grid-template-columns: 34px 1fr auto;
        gap: 12px;
        align-items: center;
        padding: 12px;
        border: 1px solid var(--panel-border);
        border-radius: 8px;
        background: #fbfcfe;
      }

      .step-index {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        border-radius: 999px;
        background: #e6f4f1;
        color: var(--accent-dark);
        font-weight: 760;
      }

      .step-name {
        font-size: 14px;
        font-weight: 700;
      }

      .step-desc {
        margin-top: 2px;
        color: var(--muted);
        font-size: 12px;
      }

      button {
        border: 0;
        border-radius: 6px;
        background: var(--accent);
        color: white;
        min-height: 36px;
        padding: 0 12px;
        font-weight: 720;
        cursor: pointer;
      }

      button:hover { background: var(--accent-dark); }
      button:disabled {
        background: #98a2b3;
        cursor: not-allowed;
      }

      .secondary {
        background: #344054;
      }

      .secondary:hover {
        background: #1d2939;
      }

      .metrics {
        display: grid;
        grid-template-columns: repeat(4, minmax(110px, 1fr));
        gap: 12px;
      }

      .metric {
        border: 1px solid var(--panel-border);
        border-radius: 8px;
        padding: 14px;
        background: #fbfcfe;
        min-height: 92px;
      }

      .metric-label {
        color: var(--muted);
        font-size: 12px;
        font-weight: 650;
      }

      .metric-value {
        margin-top: 8px;
        font-size: 24px;
        font-weight: 780;
      }

      .split {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-top: 20px;
      }

      pre {
        margin: 0;
        padding: 14px;
        min-height: 220px;
        overflow: auto;
        border-radius: 8px;
        background: var(--code);
        color: #e4e7ec;
        font-size: 12px;
        line-height: 1.55;
      }

      .alerts {
        display: grid;
        gap: 10px;
      }

      .alert {
        border: 1px solid var(--warning-border);
        border-radius: 8px;
        background: var(--warning-bg);
        padding: 12px;
      }

      .alert-type {
        color: var(--danger);
        font-weight: 760;
        font-size: 13px;
      }

      .alert-desc {
        margin-top: 4px;
        color: #7a2e0e;
        font-size: 13px;
      }

      .empty {
        color: var(--muted);
        font-size: 14px;
      }

      @media (max-width: 900px) {
        .layout,
        .split {
          grid-template-columns: 1fr;
        }

        .metrics {
          grid-template-columns: repeat(2, minmax(120px, 1fr));
        }
      }
    </style>
  </head>
  <body>
    <header>
      <div class="wrap topbar">
        <div>
          <h1>Ad Quality Automation Platform</h1>
          <p class="subtitle">Run a full ad delivery, attribution, metrics, and quality-alert workflow.</p>
        </div>
        <a class="docs-link" href="/docs">Open API Docs</a>
      </div>
    </header>

    <main class="wrap">
      <div class="layout">
        <section class="panel">
          <div class="panel-header">
            <h2 class="panel-title">Demo Flow</h2>
          </div>
          <div class="panel-body">
            <div class="steps" id="steps"></div>
          </div>
        </section>

        <section>
          <div class="panel">
            <div class="panel-header">
              <h2 class="panel-title">Campaign Metrics</h2>
            </div>
            <div class="panel-body">
              <div class="metrics" id="metrics"></div>
            </div>
          </div>

          <div class="split">
            <div class="panel">
              <div class="panel-header">
                <h2 class="panel-title">Quality Alerts</h2>
              </div>
              <div class="panel-body">
                <div class="alerts" id="alerts">
                  <div class="empty">No alerts yet. Run the quality check after recording a click.</div>
                </div>
              </div>
            </div>

            <div class="panel">
              <div class="panel-header">
                <h2 class="panel-title">Last API Response</h2>
              </div>
              <div class="panel-body">
                <pre id="output">{}</pre>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>

    <script>
      const state = {
        user: null,
        campaign: null,
        ad: null,
        delivery: null,
        click: null,
        conversion: null,
        metrics: null,
        alerts: []
      };

      const flow = [
        {
          name: "Create user",
          desc: "Synthetic US user, age 24",
          enabled: () => !state.user,
          run: async () => {
            state.user = await api("/users", "POST", {
              country: "US",
              age: 24,
              device: "ios",
              interests: "fitness sports"
            });
            return state.user;
          }
        },
        {
          name: "Create campaign",
          desc: "Active campaign with budget and targeting",
          enabled: () => state.user && !state.campaign,
          run: async () => {
            state.campaign = await api("/campaigns", "POST", {
              advertiser_name: "Nike",
              daily_budget: 500,
              bid_cpc: 1.2,
              target_country: "US",
              target_age_min: 18,
              target_age_max: 35,
              status: "active"
            });
            return state.campaign;
          }
        },
        {
          name: "Create ad",
          desc: "Ad creative under the campaign",
          enabled: () => state.campaign && !state.ad,
          run: async () => {
            state.ad = await api(`/campaigns/${state.campaign.id}/ads`, "POST", {
              campaign_id: state.campaign.id,
              title: "Running Shoes",
              landing_url: "https://example.com/shoes",
              creative_url: "https://example.com/shoes.png"
            });
            return state.ad;
          }
        },
        {
          name: "Request ad",
          desc: "Select eligible highest-bid campaign",
          enabled: () => state.user && state.ad && !state.delivery,
          run: async () => {
            state.delivery = await api("/ads/request", "POST", { user_id: state.user.id });
            return state.delivery;
          }
        },
        {
          name: "Record click",
          desc: "Click references the impression and deducts CPC",
          enabled: () => state.delivery && !state.click,
          run: async () => {
            state.click = await api("/events/click", "POST", { impression_id: state.delivery.impression_id });
            return state.click;
          }
        },
        {
          name: "Record conversion",
          desc: "Conversion attributed to the click",
          enabled: () => state.click && !state.conversion,
          run: async () => {
            state.conversion = await api("/events/conversion", "POST", {
              click_id: state.click.id,
              conversion_value: 79.99
            });
            return state.conversion;
          }
        },
        {
          name: "Load metrics",
          desc: "CTR, CVR, spend, and remaining budget",
          enabled: () => state.campaign,
          run: async () => {
            state.metrics = await api(`/metrics/campaigns/${state.campaign.id}`, "GET");
            return state.metrics;
          }
        },
        {
          name: "Run quality check",
          desc: "Create alerts for abnormal traffic patterns",
          enabled: () => state.campaign && state.click,
          run: async () => {
            state.alerts = await api(`/quality/campaigns/${state.campaign.id}/run`, "POST");
            return state.alerts;
          }
        }
      ];

      async function api(path, method, body) {
        const response = await fetch(path, {
          method,
          headers: body ? { "Content-Type": "application/json" } : {},
          body: body ? JSON.stringify(body) : undefined
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(JSON.stringify(data, null, 2));
        }
        writeOutput(data);
        return data;
      }

      function writeOutput(data) {
        document.getElementById("output").textContent = JSON.stringify(data, null, 2);
      }

      function renderSteps() {
        const root = document.getElementById("steps");
        root.innerHTML = "";
        flow.forEach((item, index) => {
          const row = document.createElement("div");
          row.className = "step";
          row.innerHTML = `
            <div class="step-index">${index + 1}</div>
            <div>
              <div class="step-name">${item.name}</div>
              <div class="step-desc">${item.desc}</div>
            </div>
          `;
          const button = document.createElement("button");
          button.textContent = "Run";
          button.disabled = !item.enabled();
          button.addEventListener("click", async () => {
            button.disabled = true;
            try {
              await item.run();
              if (state.campaign) {
                try {
                  state.metrics = await api(`/metrics/campaigns/${state.campaign.id}`, "GET");
                } catch (_) {}
              }
              renderAll();
            } catch (error) {
              writeOutput({ error: error.message });
              renderAll();
            }
          });
          row.appendChild(button);
          root.appendChild(row);
        });

        const reset = document.createElement("button");
        reset.className = "secondary";
        reset.textContent = "Reset page state";
        reset.addEventListener("click", () => {
          Object.keys(state).forEach((key) => {
            state[key] = Array.isArray(state[key]) ? [] : null;
          });
          state.alerts = [];
          writeOutput({});
          renderAll();
        });
        root.appendChild(reset);
      }

      function renderMetrics() {
        const metrics = state.metrics || {
          impressions: 0,
          clicks: 0,
          conversions: 0,
          ctr: 0,
          cvr: 0,
          spend: 0,
          remaining_budget: 0
        };
        const values = [
          ["Impressions", metrics.impressions],
          ["Clicks", metrics.clicks],
          ["Conversions", metrics.conversions],
          ["CTR", `${Math.round(metrics.ctr * 100)}%`],
          ["CVR", `${Math.round(metrics.cvr * 100)}%`],
          ["Spend", `$${Number(metrics.spend).toFixed(2)}`],
          ["Remaining", `$${Number(metrics.remaining_budget).toFixed(2)}`],
          ["Campaign", state.campaign ? `#${state.campaign.id}` : "-"]
        ];
        document.getElementById("metrics").innerHTML = values.map(([label, value]) => `
          <div class="metric">
            <div class="metric-label">${label}</div>
            <div class="metric-value">${value}</div>
          </div>
        `).join("");
      }

      function renderAlerts() {
        const root = document.getElementById("alerts");
        if (!state.alerts || state.alerts.length === 0) {
          root.innerHTML = `<div class="empty">No alerts yet. Run the quality check after recording a click.</div>`;
          return;
        }
        root.innerHTML = state.alerts.map((alert) => `
          <div class="alert">
            <div class="alert-type">${alert.alert_type} · ${alert.severity}</div>
            <div class="alert-desc">${alert.description}</div>
          </div>
        `).join("");
      }

      function renderAll() {
        renderSteps();
        renderMetrics();
        renderAlerts();
      }

      renderAll();
    </script>
  </body>
</html>
    """

