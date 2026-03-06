# 🛠️ GitHub CLI (gh) — Hướng dẫn sử dụng cho Project Management

> **Mục đích**: Tham khảo nhanh các lệnh `gh` thường dùng khi quản lý dự án trên GitHub.
> **Yêu cầu**: `gh` đã cài đặt và đăng nhập (`gh auth login`)

---

## 📋 Mục lục

1. [Setup ban đầu](#1-setup-ban-đầu)
2. [Repository](#2-repository)
3. [Issues](#3-issues)
4. [Milestones](#4-milestones)
5. [Labels](#5-labels)
6. [Pull Requests](#6-pull-requests)
7. [GitHub Projects Board](#7-github-projects-board)
8. [Workflows thường dùng](#8-workflows-thường-dùng)
9. [Tips & Tricks](#9-tips--tricks)

---

## 1. Setup ban đầu

```bash
# Kiểm tra version
gh --version

# Đăng nhập GitHub
gh auth login

# Kiểm tra trạng thái đăng nhập
gh auth status

# Clone repository
gh repo clone EurusDevSec/Zero-Door

# Set default repo (nếu chưa cd vào repo)
gh repo set-default EurusDevSec/Zero-Door
```

---

## 2. Repository

```bash
# Tạo repository mới
gh repo create EurusDevSec/Zero-Door --public --description "Self-Healing Microservices"

# Xem thông tin repo hiện tại
gh repo view

# Xem trên browser
gh repo view --web
```

---

## 3. Issues

### 3.1. Tạo Issue

```bash
# Tạo issue đơn giản
gh issue create --title "S1: Infra Setup" --body "Setup GitHub repo, board, labels"

# Tạo issue với labels + milestone + assignee
gh issue create \
  --title "S1: Infra Setup" \
  --body "Setup GitHub repo, project board, labels, milestones" \
  --label "phase:setup,priority:P0,type:infra" \
  --milestone "M1: Infra Ready" \
  --assignee "EurusDevSec"

# Tạo issue từ file markdown
gh issue create --title "S8: Agent Gaia" --body-file tasks/TASK_S8_AGENT_GAIA.md

# Tạo nhiều issues bằng script
for i in 1 2 3; do
  gh issue create --title "Task $i" --body "Description $i"
done
```

### 3.2. Xem / Liệt kê Issues

```bash
# Liệt kê tất cả issues (open)
gh issue list

# Liệt kê tất cả (cả closed)
gh issue list --state all --limit 50

# Liệt kê theo milestone
gh issue list --milestone "M1: Infra Ready"

# Liệt kê theo label
gh issue list --label "phase:setup"

# Liệt kê theo assignee
gh issue list --assignee "EurusDevSec"

# Xem chi tiết 1 issue
gh issue view 1

# Xem trên browser
gh issue view 1 --web

# Output dạng JSON (cho scripting)
gh issue list --json number,title,milestone,labels \
  --jq '.[] | "\(.number) | \(.title) | \(.milestone.title // "none")"'
```

### 3.3. Chỉnh sửa Issue

```bash
# Đổi title
gh issue edit 1 --title "S1: Infra Setup"

# Gán milestone
gh issue edit 1 --milestone "M1: Infra Ready"

# Thêm label
gh issue edit 1 --add-label "priority:P0,type:infra"

# Xóa label
gh issue edit 1 --remove-label "priority:P2"

# Gán assignee
gh issue edit 1 --add-assignee "EurusDevSec,hpt8001"

# Đổi title + milestone + labels cùng lúc
gh issue edit 1 \
  --title "S1: Infra Setup" \
  --milestone "M1: Infra Ready" \
  --add-label "phase:setup"
```

### 3.4. Đóng / Mở lại Issue

```bash
# Đóng issue (hoàn thành)
gh issue close 1

# Đóng với comment
gh issue close 1 --comment "Completed in PR #15"

# Mở lại
gh issue reopen 1
```

### 3.5. Bulk Operations (Batch)

```bash
# Đổi title + gán milestone cho nhiều issues cùng lúc
for i in 1 2 3 4 5 6; do
  gh issue edit $i --milestone "M1: Infra Ready"
done

# Đóng nhiều issues
for i in 1 2 3; do
  gh issue close $i --comment "Done in Sprint 1"
done

# Gán label cho nhiều issues
for i in 7 8; do
  gh issue edit $i --add-label "phase:gaia"
done
```

---

## 4. Milestones

> ⚠️ **`gh` KHÔNG có lệnh milestone trực tiếp**. Phải dùng `gh api` (GitHub REST API).

### 4.1. Liệt kê Milestones

```bash
# Liệt kê tất cả milestones
gh api repos/:owner/:repo/milestones \
  --jq '.[] | "\(.number) | \(.title) | \(.state) | \(.open_issues)/\(.open_issues + .closed_issues) issues"'

# Xem chi tiết milestone
gh api repos/:owner/:repo/milestones/1 --jq '{title, description, state, open_issues, closed_issues}'
```

### 4.2. Tạo Milestone

```bash
# Tạo milestone đơn giản
gh api repos/:owner/:repo/milestones -X POST \
  -f title="M1: Infra Ready" \
  -f description="Phase 1 — Sprint 1-2. Tasks: S1-S6"

# Tạo milestone với due date (ISO 8601)
gh api repos/:owner/:repo/milestones -X POST \
  -f title="M1: Infra Ready" \
  -f description="Phase 1 tasks" \
  -f due_on="2026-02-14T23:59:59Z"

# Tạo nhiều milestones bằng script
declare -A milestones=(
  ["M1: Infra Ready"]="Phase 1 — Sprint 1-2. Tasks: S1-S6"
  ["M2: Architecture Documented"]="Phase 1 — Sprint 2. Architecture.md hoàn chỉnh"
  ["M3: Gaia Detects"]="Phase 2 — Sprint 3-4. Tasks: S7-S8"
)
for title in "${!milestones[@]}"; do
  gh api repos/:owner/:repo/milestones -X POST \
    -f title="$title" \
    -f description="${milestones[$title]}"
done
```

### 4.3. Sửa Milestone

```bash
# Sửa title + description (milestone number = 1)
gh api repos/:owner/:repo/milestones/1 -X PATCH \
  -f title="M1: Infra Ready (Updated)" \
  -f description="New description"

# Đóng milestone (khi hoàn thành)
gh api repos/:owner/:repo/milestones/1 -X PATCH -f state="closed"

# Mở lại milestone
gh api repos/:owner/:repo/milestones/1 -X PATCH -f state="open"
```

### 4.4. Xóa Milestone

```bash
# Xóa milestone (milestone number = 1)
gh api repos/:owner/:repo/milestones/1 -X DELETE
```

### 4.5. Gán Issue vào Milestone

```bash
# Cách 1: Dùng gh issue edit
gh issue edit 1 --milestone "M1: Infra Ready"

# Cách 2: Dùng API (milestone number)
gh api repos/:owner/:repo/issues/1 -X PATCH -F milestone=1

# Gán nhiều issues vào 1 milestone
for i in 1 2 3 4 5 6; do
  gh issue edit $i --milestone "M1: Infra Ready"
done

# Bỏ milestone khỏi issue
gh issue edit 1 --milestone ""
```

---

## 5. Labels

### 5.1. Tạo Labels

```bash
# Tạo label với màu
gh label create "phase:setup" --description "Phase 1: Setup" --color "0E8A16"
gh label create "priority:P0" --description "Critical" --color "B60205"
gh label create "type:infra" --description "Infrastructure" --color "1D76DB"

# Tạo nhiều labels bằng script
declare -A labels=(
  ["phase:setup"]="0E8A16"
  ["phase:gaia"]="FBCA04"
  ["phase:nemesis"]="B60205"
  ["phase:hephaestus"]="1D76DB"
  ["phase:wargame"]="D93F0B"
  ["phase:closing"]="6F42C1"
  ["priority:P0"]="B60205"
  ["priority:P1"]="D93F0B"
  ["priority:P2"]="FBCA04"
  ["type:feature"]="0E8A16"
  ["type:infra"]="1D76DB"
  ["type:docs"]="6F42C1"
  ["type:bug"]="B60205"
)
for label in "${!labels[@]}"; do
  gh label create "$label" --color "${labels[$label]}" --force
done
```

### 5.2. Liệt kê / Xóa Labels

```bash
# Liệt kê tất cả labels
gh label list

# Xóa label
gh label delete "old-label" --yes

# Sửa label
gh label edit "phase:setup" --new-name "phase:1-setup" --color "0E8A16"
```

---

## 6. Pull Requests

### 6.1. Tạo PR

```bash
# Tạo PR từ branch hiện tại
gh pr create --title "feat(s1): setup infrastructure" --body "Closes #1"

# PR với reviewer + assignee
gh pr create \
  --title "feat(s8): implement agent gaia" \
  --body "Closes #8" \
  --reviewer "hpt8001" \
  --assignee "EurusDevSec" \
  --label "phase:gaia" \
  --milestone "M3: Gaia Detects Anomalies"

# PR từ file template
gh pr create --title "feat(s1): setup" --body-file .github/PULL_REQUEST_TEMPLATE.md
```

### 6.2. Xem / Merge PR

```bash
# Liệt kê PRs
gh pr list

# Xem chi tiết
gh pr view 1

# Review PR
gh pr review 1 --approve
gh pr review 1 --request-changes --body "Cần sửa X"

# Merge PR
gh pr merge 1 --squash --delete-branch

# Merge với rebase
gh pr merge 1 --rebase --delete-branch
```

### 6.3. Auto-close Issue khi merge PR

```
Trong body của PR, viết:
  - Closes #1
  - Fixes #8
  - Resolves #12

→ Khi PR merged, issue tương ứng sẽ tự động đóng.
```

---

## 7. GitHub Projects Board

```bash
# Liệt kê projects
gh project list

# Xem project chi tiết
gh project view 1

# Tạo project mới  
gh project create --title "ZERO DOOR Sprint Board"

# Thêm issue vào project
gh project item-add 1 --url https://github.com/EurusDevSec/Zero-Door/issues/1

# Xem items trong project
gh project item-list 1
```

---

## 8. Workflows thường dùng

### 8.1. 🚀 Khởi tạo Project mới (Checklist)

```bash
# 1. Tạo repo
gh repo create OrgName/ProjectName --public

# 2. Clone
gh repo clone OrgName/ProjectName && cd ProjectName

# 3. Tạo labels
gh label create "priority:P0" --color "B60205"
gh label create "priority:P1" --color "D93F0B"
gh label create "priority:P2" --color "FBCA04"
gh label create "type:feature" --color "0E8A16"
gh label create "type:bug" --color "B60205"
gh label create "type:docs" --color "6F42C1"
gh label create "type:infra" --color "1D76DB"

# 4. Tạo milestones
gh api repos/:owner/:repo/milestones -X POST -f title="Sprint 1" -f due_on="2026-01-14T00:00:00Z"
gh api repos/:owner/:repo/milestones -X POST -f title="Sprint 2" -f due_on="2026-01-28T00:00:00Z"

# 5. Tạo issues
gh issue create --title "Task 1" --milestone "Sprint 1" --label "priority:P0"

# 6. Tạo project board
gh project create --title "Sprint Board"
```

### 8.2. 🔄 Sprint hàng ngày

```bash
# Xem issues đang làm
gh issue list --assignee @me --label "status:in-progress"

# Tạo branch cho task
git checkout -b feat/s1/infra-setup

# ... code ...

# Tạo PR khi xong
gh pr create --title "feat(s1): infra setup" --body "Closes #1"

# Review + merge
gh pr merge --squash --delete-branch
```

### 8.3. 📊 Kiểm tra tiến độ Milestone

```bash
# Xem tổng quan milestones
gh api repos/:owner/:repo/milestones \
  --jq '.[] | "\(.title): \(.closed_issues)/\(.open_issues + .closed_issues) done (\(.state))"'

# Xem issues còn lại trong milestone
gh issue list --milestone "M1: Infra Ready" --state open

# Xem issues đã xong trong milestone
gh issue list --milestone "M1: Infra Ready" --state closed
```

### 8.4. 🏷️ Kết thúc Sprint

```bash
# Đóng tất cả issues đã xong
gh issue close 1 --comment "Completed in Sprint 1"

# Đóng milestone
gh api repos/:owner/:repo/milestones/1 -X PATCH -f state="closed"

# Tạo release tag
gh release create v0.1.0 --title "Sprint 1 Complete" --notes "..."
```

---

## 9. Tips & Tricks

### 9.1. Sử dụng `--jq` để filter JSON output

```bash
# Chỉ lấy title issues
gh issue list --json title --jq '.[].title'

# Filter issues theo điều kiện
gh issue list --json number,title,labels \
  --jq '[.[] | select(.labels | any(.name == "priority:P0"))]'

# Đếm issues theo milestone
gh issue list --state all --json milestone \
  --jq 'group_by(.milestone.title) | .[] | {milestone: .[0].milestone.title, count: length}'
```

### 9.2. `:owner/:repo` shortcut

```bash
# Khi đã cd vào repo folder, dùng :owner/:repo thay vì viết đầy đủ
gh api repos/:owner/:repo/milestones    # ✅ tự detect repo
gh api repos/EurusDevSec/Zero-Door/milestones  # ✅ viết đầy đủ cũng được
```

### 9.3. Alias cho lệnh hay dùng

```bash
# Tạo alias
gh alias set issues-board 'issue list --json number,title,milestone,labels,assignees --jq "..."'
gh alias set sprint-status 'api repos/:owner/:repo/milestones --jq ".[] | ..."'

# Sử dụng
gh issues-board
gh sprint-status
```

### 9.4. Lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `unknown command "milestone"` | `gh` không có lệnh milestone trực tiếp | Dùng `gh api repos/:owner/:repo/milestones` |
| `milestone not found` | Tên milestone không khớp chính xác | Kiểm tra bằng `gh api repos/:owner/:repo/milestones --jq '.[].title'` |
| `gh issue edit --milestone ""` lỗi | Cú pháp khác | Dùng `gh api repos/:owner/:repo/issues/1 -X PATCH -F milestone=null` |
| `rate limit exceeded` | Quá nhiều API calls | Chờ 1 phút hoặc dùng `--limit` nhỏ hơn |

---

## 📌 Quick Reference: ZERO DOOR Project

### Current Milestones

| # | Milestone | Tasks | Phase | Sprint |
|---|-----------|-------|-------|--------|
| M1 | Infra Ready | S1, S2, S3 | Phase 1 | Sprint 1 |
| M2 | Architecture Documented | S4, S5, S6 | Phase 1 | Sprint 2 |
| M3 | Gaia Detects Anomalies | S7, S8 | Phase 2 | Sprint 3-4 |
| M4 | Nemesis Attacks Successfully | S9, S10 | Phase 3 | Sprint 5-6 |
| M5 | Full Loop Works | S11 | Phase 4 | Sprint 7-8 |
| M6 | Experiments Complete | S12 | Phase 5 | Sprint 9-10 |
| M7 | Project Complete | S13 | Phase 6 | Sprint 11-12 |

### Issues → Milestones

| Issue # | Title | Milestone |
|---------|-------|-----------|
| 1 | S1: Infra Setup | M1 |
| 2 | S2: K8s Cluster | M1 |
| 3 | S3: Dev Environment | M1 |
| 4 | S4: Architecture Design | M2 |
| 5 | S5: Kafka Setup | M2 |
| 6 | S6: Observability | M2 |
| 7 | S7: Deploy Target App | M3 |
| 8 | S8: Agent Gaia | M3 |
| 9 | S9: Go Chaos Worker | M4 |
| 10 | S10: Agent Nemesis | M4 |
| 11 | S11: Agent Hephaestus | M5 |
| 12 | S12: War Game & Experiments | M6 |
| 13 | S13: Report & Defense | M7 |

---

> **Tạo**: 05/03/2026
> **Cập nhật**: 05/03/2026
