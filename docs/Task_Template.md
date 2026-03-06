---
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
project: <% tp.system.suggester(["🛡️ Zero-Door", "🧠 Insight", "👁️ Holmz", "📚 Study"], ["Zero-Door", "Insight", "Holmz", "Study"]) %>
priority: <% tp.system.suggester(["🔴 Must Have — Critical for Sprint Goal", "🟠 Should Have — Important, not critical", "🟡 Could Have — Nice to have", "⚪ Won't Have — Out of scope"], ["must-have", "should-have", "could-have", "wont-have"]) %>
status: Backlog
due_date: 
tags: [task]
---

# <% tp.file.title %>

```dataviewjs
const file = dv.current();
const tasks = file.file.tasks;
const done = tasks.filter(t => t.completed).length;
const total = tasks.length;
const pct = total === 0 ? 0 : Math.round((done / total) * 100);

let color = "#ef4444";
if (pct >= 30) color = "#f97316";
if (pct >= 60) color = "#eab308";
if (pct === 100) color = "#22c55e";

const due = file.due_date;
const daysLeft = due ? Math.ceil((new Date(due) - new Date()) / 86400000) : null;
let dueText = "";
if (daysLeft !== null) {
  if (daysLeft < 0) dueText = `🚨 ${Math.abs(daysLeft)}d overdue`;
  else if (daysLeft === 0) dueText = "⚡ Due today";
  else if (daysLeft <= 3) dueText = `� ${daysLeft}d left`;
  else dueText = `📅 ${daysLeft}d left`;
}

dv.paragraph(`**${done}/${total}** tasks · <span style="color:${color};font-weight:bold;">${pct}%</span>${dueText ? " · " + dueText : ""}`);
dv.paragraph(`<div style="height:6px;background:#334155;border-radius:4px;margin-top:4px;"><div style="width:${pct}%;height:100%;background:${color};border-radius:4px;"></div></div>`);
```

---

## 💡 Context
> [!note]+ Mô tả vấn đề cho AI
> *Viết 2-3 câu, gửi cho AI để refine thành User Story*
> 
> 
---
## 🤖 AI Refined

> **User Story:**  
> As a `[role]`, I want `[goal]` so that `[value]`.

**Acceptance Criteria:**
- [ ] Happy path — Core functionality works
- [ ] Edge case — Handle errors gracefully
- [ ] Security — Input validated
---
## 🛠️ Implementation
- [ ] Branch: `feat/<% tp.file.title.toLowerCase().replace(/\s+/g, '-') %>`
- [ ] PR Created
- [ ] Tests Passed
- [ ] Deployed
---

## 📝 Notes
> *Quick notes, links, snippets*