---
toc: false
---

# FinSights - Customer Intelligence

<div class="tip" label="About">
  The original data includes 276,836 customers of <b>Bangor Savings Bank</b> and 8,137,375 transactions. This project focuses on customers who made at least one debit card transaction over a <b>65 day window between November 20, 2025 - January 24, 2026</b>. This resulted in a dataset of <b>58,677 customers</b> after removing non-individual customers and certain outliers having a combined <b>3,695,806 transactions</b>. 
</div>

```js
const customers = FileAttachment("data/customer_clusters.csv").csv({typed: true});
```

```js
const COLORS = {
  "Active Everyday Spenders": "#1e3a5f",
  "Lending-Engaged Loyal Customers": "#2563eb",
  "Low-Frequency Big Spenders": "#0ea5e9",
  "Low-Activity Digital Users": "#93c5fd"
};
```

<div class="grid grid-cols-3">
  <div class="card">
    <h2>Total Customers</h2>
    <span class="big">${customers.length.toLocaleString("en-US")}</span>
  </div>
  <div class="card">
    <h2>Behavioral Features</h2>
    <span class="big">55</span>
  </div>
  <div class="card">
    <h2>Customer Segments</h2>
    <span class="big">4</span>
  </div>
</div>

## Customer Segments

```js
const segmentData = d3.rollups(
  customers,
  v => v.length,
  d => d.cluster_name
).map(([name, count]) => ({name, count, pct: (count / customers.length * 100).toFixed(1)}));
```

```js
function segmentBar(data, {width} = {}) {
  return Plot.plot({
    width,
    height: 300,
    marginLeft: 260,
    marginRight: 20,
    x: {label: null, grid: false, axis: null},
    y: {label: null},
    color: {
      domain: Object.keys(COLORS),
      range: Object.values(COLORS)
    },
    marks: [
      Plot.axisY({fontSize: 13, tickSize: 0}),
      Plot.barX(data, {
        x: "count", y: "name", fill: "name",
        sort: {y: "-x"},
        tip: {format: {fill: false}}
      }),
      Plot.text(data, {
        x: "count", y: "name",
        text: d => `${d.pct}%`,
        dx: -5, textAnchor: "end", fill: "white", fontSize: 12, fontWeight: 600
      }),
      Plot.ruleX([0])
    ]
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => segmentBar(segmentData, {width}))}
  </div>
</div>