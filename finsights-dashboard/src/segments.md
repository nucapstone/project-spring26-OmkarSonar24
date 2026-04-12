---
toc: false
---

# Segment Profiles
K-Means clustering on 55 behavioral features identified four distinct customer groups.
```js
const profiles = FileAttachment("data/segment_profiles.csv").csv({typed: true});
const customers = FileAttachment("data/customer_clusters.csv").csv({typed: true});
const geo = FileAttachment("data/segment_geo.csv").csv({typed: true});
const maineMerchants = FileAttachment("data/segment_maine_merchants.csv").csv({typed: true});
const maineCities = FileAttachment("data/segment_maine_cities.csv").csv({typed: true});
const recurring = FileAttachment("data/segment_recurring.csv").csv({typed: true});
const categories = FileAttachment("data/segment_categories.csv").csv({typed: true});
const oosMerchants = FileAttachment("data/segment_oos_merchants.csv").csv({typed: true});
const oosCities = FileAttachment("data/segment_oos_cities.csv").csv({typed: true});
```

```js
const COLORS = {
  "Active Everyday Spenders": "#1e3a5f",
  "Lending-Engaged Loyal Customers": "#2563eb",
  "Low-Frequency Big Spenders": "#0ea5e9",
  "Low-Activity Digital Users": "#93c5fd"
};
```

```js
const segmentPicker = Inputs.select(
  Object.keys(COLORS),
  {label: "Select Segment"}
);
const selectedSegment = Generators.input(segmentPicker);
```

${segmentPicker}

```js
const seg = customers.filter(d => d.cluster_name === selectedSegment);
const segCount = seg.length;
const segPct = (segCount / customers.length * 100).toFixed(1);
const segGeo = geo.filter(d => d.cluster_name === selectedSegment);
const inState = segGeo.find(d => d.location === "In-State (Maine)");
const inStatePct = inState ? (inState.txn_count / d3.sum(segGeo, d => d.txn_count) * 100).toFixed(0) : "—";
const segColor = COLORS[selectedSegment];
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Customers</h2>
    <span class="big">${segCount.toLocaleString("en-US")}</span>
    <span style="color: #6b7280; font-size: 0.85rem;">${segPct}% of total</span>
  </div>
  <div class="card">
    <h2>Avg Spend</h2>
    <span class="big">$${d3.mean(seg, d => d.total_spend).toLocaleString("en-US", {maximumFractionDigits: 0})}</span>
  </div>
  <div class="card">
    <h2>Avg Transactions</h2>
    <span class="big">${d3.mean(seg, d => d.transaction_count).toFixed(0)}</span>
    <span style="color: #6b7280; font-size: 0.85rem;">$${(d3.mean(seg, d => d.total_spend) / d3.mean(seg, d => d.transaction_count)).toFixed(0)} per txn</span>
  </div>
  <div class="card">
    <h2>Maine Transactions</h2>
    <span class="big">${inStatePct}%</span>
  </div>
</div>

## Spending Profile

```js
function profileChart(data, segment, {width} = {}) {
  const filtered = data
    .filter(d => d.cluster_name === segment)
    .sort((a, b) => Math.abs(b.z_score) - Math.abs(a.z_score))
    .slice(0, 15);

  return Plot.plot({
    width,
    height: 400,
    marginLeft: 220,
    x: {label: "Std. Deviations from Average", grid: true, tickSize: 0},
    y: {label: null, tickSize: 0},
    color: {domain: [-2, 0, 2], range: ["#dc2626", "#e5e7eb", "#1e3a5f"], type: "linear"},
    marks: [
      Plot.axisY({fontSize: 12, tickSize: 0}),
      Plot.barX(filtered, {
        x: "z_score", y: "feature", fill: "z_score",
        sort: {y: "x"},
        tip: {format: {fill: false}}
      }),
      Plot.ruleX([0])
    ]
  });
}
```

```js
function categoryChart(data, segment, {width} = {}) {
  const row = data.find(d => d.cluster_name === segment);
  if (!row) return html`<p>No data</p>`;

  const cats = ["grocery", "dining", "gas", "digital", "retail", "healthcare",
                "entertainment", "financial", "telecom", "utilities", "other"];
  const catData = cats.map(c => ({category: c, share: row[c]}))
    .sort((a, b) => b.share - a.share);

  return Plot.plot({
    width,
    height: 400,
    marginLeft: 120,
    x: {label: "% of Spend", grid: false, axis: null},
    y: {label: null, tickSize: 0},
    marks: [
      Plot.axisY({fontSize: 12, tickSize: 0}),
      Plot.barX(catData, {
        x: "share", y: "category", fill: segColor,
        sort: {y: "-x"},
        tip: {format: {fill: false}}
      }),
      Plot.ruleX([0])
    ]
  });
}
```

<div class="grid grid-cols-2">
  <div class="card">
    <h2>Top Distinctive Features (Z-Score)</h2>
    ${resize((width) => profileChart(profiles, selectedSegment, {width}))}
  </div>
  <div class="card">
    <h2>Category Breakdown</h2>
    ${resize((width) => categoryChart(categories, selectedSegment, {width}))}
  </div>
</div>

## Transaction Patterns

```js
function geoSplitChart(data, segment, {width} = {}) {
  const filtered = data.filter(d => d.cluster_name === segment);
  const total = d3.sum(filtered, d => d.txn_count);
  const plotData = filtered.map(d => ({...d, pct: d.txn_count / total * 100}));

  return Plot.plot({
    width,
    height: 200,
    marginLeft: 160,
    marginRight: 20,
    x: {label: "% of Transactions", grid: false, tickSize: 0},
    y: {label: null, tickSize: 0},
    color: {domain: ["In-State (Maine)", "Out-of-State"], range: ["#1e3a5f", "#93c5fd"]},
    marks: [
      Plot.barX(plotData, {
        x: "pct", y: "location", fill: "location",
        tip: {format: {fill: false}}
      }),
      Plot.text(plotData, {
        x: "pct", y: "location", text: d => `${d.pct.toFixed(1)}%`,
        dx: -5, textAnchor: "end", fill: "white", fontSize: 12, fontWeight: 600
      }),
      Plot.ruleX([0])
    ]
  });
}
```

```js
function recurringChart(data, segment, {width} = {}) {
  const filtered = data.filter(d => d.cluster_name === segment);
  const total = d3.sum(filtered, d => d.txn_count);
  const plotData = filtered.map(d => ({...d, pct: d.txn_count / total * 100}));

  return Plot.plot({
    width,
    height: 200,
    marginLeft: 160,
    marginRight: 20,
    x: {label: "% of Transactions", grid: false, tickSize: 0},
    y: {label: null, tickSize: 0},
    color: {domain: ["Non-Recurring", "Recurring"], range: ["#1e3a5f", "#0ea5e9"]},
    marks: [
      Plot.barX(plotData, {
        x: "pct", y: "txn_type", fill: "txn_type",
        tip: {format: {fill: false}}
      }),
      Plot.text(plotData, {
        x: "pct", y: "txn_type", text: d => `${d.pct.toFixed(1)}%`,
        dx: -5, textAnchor: "end", fill: "white", fontSize: 12, fontWeight: 600
      }),
      Plot.ruleX([0])
    ]
  });
}
```

<div class="grid grid-cols-2">
  <div class="card">
    <h2>In-State vs Out-of-State</h2>
    ${resize((width) => geoSplitChart(geo, selectedSegment, {width}))}
  </div>
  <div class="card">
    <h2>Recurring vs One-Time</h2>
    ${resize((width) => recurringChart(recurring, selectedSegment, {width}))}
  </div>
</div>

## Where They Spend in Maine

```js
function merchantChart(data, segment, {width} = {}) {
  const filtered = data.filter(d => d.cluster_name === segment);

  return Plot.plot({
    width,
    height: 350,
    marginLeft: 200,
    x: {label: null, grid: false, axis: null},
    y: {label: null, tickSize: 0},
    marks: [
      Plot.axisY({fontSize: 12, tickSize: 0}),
      Plot.barX(filtered, {
        x: "total_spend", y: "Merchant_Name", fill: segColor,
        sort: {y: "-x"},
        tip: {format: {fill: false}}
      })
    ]
  });
}
```

```js
function cityChart(data, segment, {width} = {}) {
  const filtered = data.filter(d => d.cluster_name === segment);

  return Plot.plot({
    width,
    height: 350,
    marginLeft: 160,
    x: {label: null, grid: false, axis: null},
    y: {label: null, tickSize: 0},
    marks: [
      Plot.axisY({fontSize: 12, tickSize: 0}),
      Plot.barX(filtered, {
        x: "total_spend", y: "city", fill: segColor,
        sort: {y: "-x"},
        tip: {format: {fill: false}}
      })
    ]
  });
}
```

<div class="grid grid-cols-2">
  <div class="card">
    <h2>Top Maine Merchants</h2>
    ${resize((width) => merchantChart(maineMerchants, selectedSegment, {width}))}
  </div>
  <div class="card">
    <h2>Top Maine Cities</h2>
    ${resize((width) => cityChart(maineCities, selectedSegment, {width}))}
  </div>
</div>

## Where They Spend Outside Maine

```js
function oosMerchantChart(data, segment, {width} = {}) {
  const filtered = data.filter(d => d.cluster_name === segment);

  return Plot.plot({
    width,
    height: 350,
    marginLeft: 200,
    x: {label: null, grid: false, axis: null},
    y: {label: null, tickSize: 0},
    marks: [
      Plot.axisY({fontSize: 12, tickSize: 0}),
      Plot.barX(filtered, {
        x: "total_spend", y: "Merchant_Name", fill: segColor, fillOpacity: 0.6,
        sort: {y: "-x"},
        tip: {format: {fill: false}}
      })
    ]
  });
}
```

```js
function oosCityChart(data, segment, {width} = {}) {
  const filtered = data.filter(d => d.cluster_name === segment);

  return Plot.plot({
    width,
    height: 350,
    marginLeft: 160,
    x: {label: null, grid: false, axis: null},
    y: {label: null, tickSize: 0},
    marks: [
      Plot.axisY({fontSize: 12, tickSize: 0}),
      Plot.barX(filtered, {
        x: "total_spend", y: "city", fill: segColor, fillOpacity: 0.6,
        sort: {y: "-x"},
        tip: {format: {fill: false}}
      })
    ]
  });
}
```

<div class="grid grid-cols-2">
  <div class="card">
    <h2>Top Out-of-State Merchants</h2>
    ${resize((width) => oosMerchantChart(oosMerchants, selectedSegment, {width}))}
  </div>
  <div class="card">
    <h2>Top Out-of-State Cities</h2>
    ${resize((width) => oosCityChart(oosCities, selectedSegment, {width}))}
  </div>
</div>

<div class="note" style="font-size: 0.8rem; color: #6b7280; margin-top: 4px;">
  Some out-of-state entries display phone numbers instead of city names - these represent online merchants which report a toll-free number rather than a physical location (eg : 8,558,124,430 = Venmo, 855-707-7328 = Spectrum, 402-935-7733 = PayPal).
</div>