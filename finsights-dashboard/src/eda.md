---
toc: false
---

# Trends

```js
const hourly = FileAttachment("data/hourly_pattern.csv").csv({typed: true});
const daily = FileAttachment("data/daily_pattern.csv").csv({typed: true});
const monthly = FileAttachment("data/monthly_trend.csv").csv({typed: true});
const categories = FileAttachment("data/category_spend.csv").csv({typed: true});
const merchants = FileAttachment("data/top_merchants.csv").csv({typed: true});
const geo = FileAttachment("data/geo_spending.csv").csv({typed: true});
const customers = FileAttachment("data/customer_clusters.csv").csv({typed: true});
const demographics = FileAttachment("data/demographics.csv").csv({typed: true});
```

```js
const ACCENT = "#1e3a5f";
const ACCENT_LIGHT = "#7c9fc0";
```

<div class="grid grid-cols-3">
  <div class="card">
    <h2>Total Transactions</h2>
    <span class="big">${d3.sum(monthly, d => d.transaction_count).toLocaleString("en-US")}</span>
  </div>
  <div class="card">
    <h2>Total Spend</h2>
    <span class="big">$${(d3.sum(monthly, d => d.total_spend) / 1e6).toFixed(1)}M</span>
  </div>
  <div class="card">
    <h2>Avg Transaction</h2>
    <span class="big">$${(d3.sum(monthly, d => d.total_spend) / d3.sum(monthly, d => d.transaction_count)).toFixed(2)}</span>
  </div>
</div>

## Customer Demographics

```js
const genderCounts = d3.rollups(
  demographics,
  v => v.length,
  d => (d.gender == null || d.gender === "") ? "" : d.gender
).map(([gender, count]) => ({gender, count}));

const totalGendered = d3.sum(genderCounts, d => d.count);
```

```js
function genderPie(data, {width} = {}) {
  const total = d3.sum(data, d => d.count);
  const colors = {"F": "#1e3a5f", "M": "#7c9fc0", "O": "#a3c4dc", "U": "#d1e2ee", "": "#e5e7eb"};
  const labels = {"F": "Female", "M": "Male", "O": "Other", "U": "Undeclared", "": "Not Provided"};
  const size = Math.min(width, 280);
  const radius = size / 2 - 20;
  const pie = d3.pie().value(d => d.count).sort(null);
  const arc = d3.arc().innerRadius(0).outerRadius(radius);
  const labelArc = d3.arc().innerRadius(radius * 0.55).outerRadius(radius * 0.55);
  const arcs = pie(data);

  const svg = d3.create("svg")
    .attr("width", size)
    .attr("height", size)
    .attr("viewBox", [-size / 2, -size / 2, size, size]);

  svg.selectAll("path")
    .data(arcs)
    .join("path")
    .attr("d", arc)
    .attr("fill", d => colors[d.data.gender] || "#999");

  svg.selectAll("text")
    .data(arcs.filter(d => d.data.count / total > 0.02))
    .join("text")
    .attr("transform", d => `translate(${labelArc.centroid(d)})`)
    .attr("text-anchor", "middle")
    .attr("fill", d => ["Unknown", "U"].includes(d.data.gender) ? "#374151" : "white")
    .attr("font-size", "13px")
    .attr("font-weight", "600")
    .each(function(d) {
      const el = d3.select(this);
      el.append("tspan").attr("x", 0).attr("dy", "-0.3em").text(labels[d.data.gender] || d.data.gender);
      el.append("tspan").attr("x", 0).attr("dy", "1.3em").text(`${(d.data.count / total * 100).toFixed(1)}%`);
    });

  return svg.node();
}
```

```js
function ageChart(data, {width} = {}) {
  const filtered = data.filter(d => d.age > 0);
  return Plot.plot({
    width,
    height: 280,
    x: {label: "Age", tickSize: 0},
    y: {label: "Customers", grid: true, tickSize: 0},
    marks: [
      Plot.rectY(filtered, Plot.binX({y: "count"}, {
        x: "age", fill: ACCENT, thresholds: 30
      })),
      Plot.ruleY([0])
    ]
  });
}
```

<div class="grid grid-cols-2">
  <div class="card">
    <h2>Gender Distribution</h2>
    ${resize((width) => genderPie(genderCounts, {width}))}
  </div>
  <div class="card">
    <h2>Age Distribution</h2>
    ${resize((width) => ageChart(demographics, {width}))}
  </div>
</div>

<div class="note" style="font-size: 0.8rem; color: #6b7280; margin-top: 4px;">
  Other: ${genderCounts.find(d => d.gender === "O")?.count.toLocaleString("en-US") || 0} customers · 
  Undeclared: ${genderCounts.find(d => d.gender === "U")?.count.toLocaleString("en-US") || 0} customers · 
  Not Provided: ${genderCounts.find(d => d.gender === "")?.count.toLocaleString("en-US") || 0} customers.
  80 customers with age 0 are excluded from the age chart. Extreme values (age 1, 120) may reflect data quality issues.
</div>

## Monthly Overview

```js
function monthlySpendChart(data, {width} = {}) {
  return Plot.plot({
    width,
    height: 280,
    x: {label: null, domain: ["November", "December", "January"], tickSize: 0},
    y: {label: null, grid: false, axis: null},
    marks: [
      Plot.barY(data, {
        x: "month", y: "total_spend", fill: ACCENT,
        tip: {format: {fill: false}}
      }),
      Plot.text(data, {
        x: "month", y: "total_spend",
        text: d => `$${(d.total_spend / 1e6).toFixed(1)}M`,
        dy: -10, fontSize: 13, fontWeight: 600
      }),
      Plot.ruleY([0])
    ]
  });
}
```

```js
function monthlyTxnChart(data, {width} = {}) {
  return Plot.plot({
    width,
    height: 280,
    x: {label: null, domain: ["November", "December", "January"], tickSize: 0},
    y: {label: null, grid: false, axis: null},
    marks: [
      Plot.barY(data, {
        x: "month", y: "transaction_count", fill: ACCENT_LIGHT,
        tip: {format: {fill: false}}
      }),
      Plot.text(data, {
        x: "month", y: "transaction_count",
        text: d => d.transaction_count.toLocaleString("en-US"),
        dy: -10, fontSize: 13, fontWeight: 600
      }),
      Plot.ruleY([0])
    ]
  });
}
```

<div class="grid grid-cols-2">
  <div class="card">
    <h2>Spend Volume</h2>
    ${resize((width) => monthlySpendChart(monthly, {width}))}
  </div>
  <div class="card">
    <h2>Transaction Count</h2>
    ${resize((width) => monthlyTxnChart(monthly, {width}))}
  </div>
</div>

## Spending by Category

```js
function categoryChart(data, {width} = {}) {
  return Plot.plot({
    width,
    height: 400,
    marginLeft: 200,
    x: {label: null, grid: false, axis: null},
    y: {label: null, tickSize: 0},
    marks: [
      Plot.axisY({fontSize: 12, tickSize: 0}),
      Plot.barX(data, {
        x: "total_spend", y: "category", fill: ACCENT,
        sort: {y: "-x"},
        tip: {format: {fill: false}}
      }),
      Plot.ruleX([0])
    ]
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => categoryChart(categories, {width}))}
  </div>
</div>

## Transaction Timing

```js
function hourlyChart(data, {width} = {}) {
  return Plot.plot({
    width,
    height: 280,
    x: {label: "Hour of Day", ticks: d3.range(0, 24, 2), tickSize: 0},
    y: {label: "Transactions", grid: true, tickSize: 0},
    marks: [
      Plot.areaY(data, {x: "hour", y: "transaction_count", fill: ACCENT, fillOpacity: 0.15}),
      Plot.lineY(data, {x: "hour", y: "transaction_count", stroke: ACCENT, strokeWidth: 2}),
      Plot.dot(data, {x: "hour", y: "transaction_count", fill: ACCENT, r: 3, tip: true})
    ]
  });
}
```

```js
function dailyChart(data, {width} = {}) {
  return Plot.plot({
    width,
    height: 280,
    x: {label: null, domain: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], tickSize: 0},
    y: {label: "Transactions", grid: true, tickSize: 0},
    marks: [
      Plot.barY(data, {
        x: "day_name", y: "transaction_count",
        fill: d => (d.day_name === "Saturday" || d.day_name === "Sunday") ? ACCENT_LIGHT : ACCENT,
        tip: {format: {fill: false}}
      }),
      Plot.ruleY([0])
    ]
  });
}
```

<div class="grid grid-cols-2">
  <div class="card">
    <h2>Hourly Pattern</h2>
    ${resize((width) => hourlyChart(hourly, {width}))}
  </div>
  <div class="card">
    <h2>Day of Week</h2>
    ${resize((width) => dailyChart(daily, {width}))}
  </div>
</div>

## Top 10 Merchants

```js
function merchantChart(data, {width} = {}) {
  const top10 = data.slice(0, 10);
  return Plot.plot({
    width,
    height: 350,
    marginLeft: 200,
    x: {label: null, grid: false, axis: null},
    y: {label: null},
    marks: [
      Plot.axisY({fontSize: 12, tickSize: 0}),
      Plot.barX(top10, {
        x: "total_spend", y: "merchant", fill: ACCENT,
        sort: {y: "-x"},
        tip: {format: {fill: false}}
      })
    ]
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => merchantChart(merchants, {width}))}
  </div>
</div>

## Where Customers Spend

```js
const maineCities = geo.filter(d => d.state === "ME");
const outOfState = geo.filter(d => d.state !== "ME");
```

```js
function geoChart(data, {width} = {}) {
  return Plot.plot({
    width,
    height: 400,
    marginLeft: 160,
    x: {label: null, grid: false, axis: null},
    y: {label: null},
    marks: [
      Plot.axisY({fontSize: 12, tickSize: 0}),
      Plot.barX(data, {
        x: "total_spend", y: "city", fill: ACCENT,
        sort: {y: "-x"},
        tip: {format: {fill: false}}
      })
    ]
  });
}
```

<div class="grid grid-cols-2">
  <div class="card">
    <h2>Maine Cities</h2>
    ${resize((width) => geoChart(maineCities, {width}))}
  </div>
  <div class="card">
    <h2>Out-of-State / Online</h2>
    ${resize((width) => geoChart(outOfState, {width}))}
  </div>
</div>

<div class="note" style="font-size: 0.8rem; color: #6b7280; margin-top: 4px;">
  Some out-of-state entries display phone numbers instead of city names - these represent online merchants which report a toll-free number rather than a physical location (eg : 8,558,124,430 = Venmo, 855-707-7328 = Spectrum).
</div>