---
toc: false
---

# Recommendations

Translating customer segments into actionable strategies for Bangor Savings Bank.

```js
const customers = FileAttachment("data/customer_clusters.csv").csv({typed: true});
const geo = FileAttachment("data/segment_geo.csv").csv({typed: true});
const recurring = FileAttachment("data/segment_recurring.csv").csv({typed: true});
const maineMerchants = FileAttachment("data/segment_maine_merchants.csv").csv({typed: true});
const categories = FileAttachment("data/segment_categories.csv").csv({typed: true});
```

```js
const COLORS = {
  "Active Everyday Spenders": "#1e3a5f",
  "Lending-Engaged Loyal Customers": "#2563eb",
  "Low-Frequency Big Spenders": "#0ea5e9",
  "Low-Activity Digital Users": "#93c5fd"
};

const segments = Object.keys(COLORS).map(name => {
  const seg = customers.filter(d => d.cluster_name === name);
  const segGeo = geo.filter(d => d.cluster_name === name);
  const inState = segGeo.find(d => d.location === "In-State (Maine)");
  const total = d3.sum(segGeo, d => d.txn_count);
  const segRec = recurring.filter(d => d.cluster_name === name);
  const recRow = segRec.find(d => d.txn_type === "Recurring");
  const recTotal = d3.sum(segRec, d => d.txn_count);
  return {
    name,
    color: COLORS[name],
    count: seg.length,
    pct: (seg.length / customers.length * 100).toFixed(1),
    avg_spend: d3.mean(seg, d => d.total_spend).toFixed(0),
    avg_txns: d3.mean(seg, d => d.transaction_count).toFixed(0),
    total_spend: d3.sum(seg, d => d.total_spend),
    maine_pct: inState ? (inState.txn_count / total * 100).toFixed(0) : "—",
    recurring_pct: recRow ? (recRow.txn_count / recTotal * 100).toFixed(0) : "—"
  };
});
```


<div class="grid grid-cols-4">
  ${segments.map(s => html`<div class="card">
    <h2 style="color: ${s.color}; font-size: 0.95rem;">${s.name}</h2>
    <b>$${Number(s.avg_spend).toLocaleString("en-US")}</b> avg spend · <b>${s.avg_txns}</b> txns<br>
    <b>$${(Number(s.avg_spend) / Number(s.avg_txns)).toFixed(0)}</b> per txn · <b>${s.maine_pct}%</b> in Maine
  </div>`)}
</div>

## 1. Buoy Local Rewards

<div class="tip" label="Opportunity">
  <b>Active Everyday Spenders</b> and <b>Lending-Engaged Loyal Customers</b> already have 60%+ Maine transactions across 1,000+ local merchants. Hence, Buoy Local enrollment and rewards can be targeted at these two segments first.
</div>

```js
function mainePctChart(data, {width} = {}) {
  return Plot.plot({
    width,
    height: 220,
    marginLeft: 280,
    marginRight: 20,
    x: {label: "% of Transactions In-State", grid: false, tickSize: 0, domain: [0, 100]},
    y: {label: null, tickSize: 0},
    color: {domain: Object.keys(COLORS), range: Object.values(COLORS)},
    marks: [
      Plot.axisY({fontSize: 12, tickSize: 0}),
      Plot.barX(data, {
        x: d => +d.maine_pct, y: "name", fill: "name",
        sort: {y: "-x"},
        tip: {format: {fill: false}}
      }),
      Plot.text(data, {
        x: d => +d.maine_pct, y: "name",
        text: d => `${d.maine_pct}%`,
        dx: -8, textAnchor: "end", fill: "white", fontSize: 12, fontWeight: 600
      }),
      Plot.ruleX([0])
    ]
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">
    <h2>In-State Transaction Share by Segment</h2>
    ${resize((width) => mainePctChart(segments, {width}))}
  </div>
</div>

## 2. Personalized Cashback

<div class="tip" label="Opportunity">
  Each segment spends differently - one-size-fits-all cashback misses the mark. <b>Active Everyday Spenders</b> want grocery & gas rewards. <b>Low-Activity Digital Users</b> will respond to subscription & digital incentives. <b>Low-Frequency Big Spenders</b> are bill payers - cashback on utilities and financial services will retain them.
</div>


## 3. Early Intervention

<div class="tip" label="Risk">
  <b>Low-Activity Digital Users</b> (${segments.find(s => s.name === "Low-Activity Digital Users")?.count.toLocaleString("en-US")} customers) average just ${segments.find(s => s.name === "Low-Activity Digital Users")?.avg_txns} transactions and $${segments.find(s => s.name === "Low-Activity Digital Users")?.avg_spend} over 3 months. Their card is mostly on autopay. <b>Low-Frequency Big Spenders</b> use their card almost exclusively for bill pay. Both groups need proactive engagement before they switch.
</div>

```js
function revenueRiskChart(data, {width} = {}) {
  const sorted = [...data].sort((a, b) => b.total_spend - a.total_spend);
  const maxSpend = d3.max(sorted, d => d.total_spend);

  return Plot.plot({
    width,
    height: 280,
    marginLeft: 280,
    marginRight: 60,
    x: {label: null, grid: false, axis: null},
    y: {label: null, tickSize: 0},
    color: {domain: Object.keys(COLORS), range: Object.values(COLORS)},
    marks: [
      Plot.axisY({fontSize: 13, tickSize: 0}),
      Plot.barX(sorted, {
        x: "total_spend", y: "name", fill: "name",
        sort: {y: "-x"},
        tip: {format: {fill: false}}
      }),
      Plot.text(sorted.filter(d => d.total_spend / maxSpend > 0.15), {
        x: "total_spend", y: "name",
        text: d => `$${(d.total_spend / 1e6).toFixed(1)}M`,
        dx: -8, textAnchor: "end", fill: "white", fontSize: 12, fontWeight: 600
      }),
      Plot.text(sorted.filter(d => d.total_spend / maxSpend <= 0.15), {
        x: "total_spend", y: "name",
        text: d => `$${(d.total_spend / 1e6).toFixed(1)}M`,
        dx: 5, textAnchor: "start", fill: "#1e3a5f", fontSize: 12, fontWeight: 600
      }),
      Plot.ruleX([0])
    ]
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">
    <h2>Revenue at Risk by Segment</h2>
    ${resize((width) => revenueRiskChart(segments, {width}))}
  </div>
</div>

## 4. Local Business Promotions

<div class="tip" label="Opportunity">
  Bangor dominates local spend across all segments, followed by Portland, Augusta, and Brewer. <b>Active Everyday Spenders</b> drive $${(segments.find(s => s.name === "Active Everyday Spenders")?.total_spend / 1e6).toFixed(1)}M in total spend - they are the local economy engine. Local businesses should target the Bangor–Brewer corridor and Portland metro first, with segment-specific merchant partnerships.
</div>


## Limitations & Next Steps

<div class="grid grid-cols-2">
  <div class="card">
    <h2 style="color: #dc2626;">Known Limitations</h2>
    <p><b>Short observation window</b> - 65 days (Nov 20, 2025 - Jan 24, 2026) includes holiday seasonality and post-holiday pullback. Patterns may shift with a full year of data.</p>
    <p><b>Customer coverage</b> - analysis covers 58,677 customers with both transaction and demographic records. ~59,000 additional transacting customers lacked demographic data and were excluded.</p>
  </div>
  <div class="card">
    <h2 style="color: #115e59;">Future Work</h2>
    <p><b>Predictive modeling</b> - classify customers as UPGRADE / STABLE / DOWNGRADE to identify at-risk customers before they churn.</p>
    <p><b>Extended time window</b> - a 12-month dataset removes seasonal bias and reveals true behavioral trends.</p>
    <p><b>Cross-sell scoring</b> - 30,000+ Active Everyday Spenders have zero loans. Predictive models could identify which customers are most likely to adopt lending products.</p>
  </div>
</div>