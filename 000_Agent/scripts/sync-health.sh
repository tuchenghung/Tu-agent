#!/usr/bin/env bash
# sync-health.sh
# 驗證 Claude Code 跨裝置同步架構是否健康
# 由 pro-kit 07 生成 · by 雷蒙
# 建議每週五複盤日執行一次

set -e

echo "🩺 sync-health.sh 開始體檢..."
echo "   執行時間：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

FAIL=0
MOTHER_CANDIDATES=(
  "$HOME/Library/CloudStorage/Dropbox/Tu-agent"
  "$HOME/Dropbox/Tu-agent"
)

MOTHER=""
for candidate in "${MOTHER_CANDIDATES[@]}"; do
  if [ -d "$candidate/.claude" ]; then
    MOTHER="$candidate"
    break
  fi
done

if [ -z "$MOTHER" ]; then
  echo "❌ 找不到母體資料夾，請確認 Dropbox 已同步"
  exit 1
fi

echo "   母體路徑：$MOTHER"
echo ""

# 檢查 1：~/.claude/ 底下的 symlink 指向是否都存在
echo "[1/4] 檢查 ~/.claude/ symlink..."
for item in settings.json commands keybindings.json skills; do
  link="$HOME/.claude/$item"
  if [ -L "$link" ]; then
    target=$(readlink "$link")
    if [ -e "$target" ]; then
      echo "  ✅ $item → $target"
    else
      echo "  ❌ $item → $target（target 不存在）"
      FAIL=$((FAIL+1))
    fi
  elif [ -e "$link" ]; then
    echo "  ⚠️  $item 是一般檔案（可能是 Dropbox 同步問題）"
    FAIL=$((FAIL+1))
  else
    echo "  ➖ $item 不存在（可跳過）"
  fi
done

# 檢查 2：母體的核心檔案是否存在
echo ""
echo "[2/4] 檢查母體核心檔案..."
for item in .claude/settings.json .claude/commands; do
  if [ -e "$MOTHER/$item" ]; then
    echo "  ✅ $item 存在"
  else
    echo "  ❌ $item 不存在"
    FAIL=$((FAIL+1))
  fi
done

# 檢查 3：關鍵 skill 讀得到
echo ""
echo "[3/4] 檢查關鍵 skill 可讀取..."
SKILLS_DIR="$HOME/.claude/skills"
if [ -d "$SKILLS_DIR" ]; then
  SKILL_COUNT=$(ls "$SKILLS_DIR" 2>/dev/null | wc -l | tr -d ' ')
  echo "  ✅ skills/ 可讀取（共 $SKILL_COUNT 個 skill）"
else
  echo "  ❌ skills/ 讀不到（可能是 symlink 斷了）"
  FAIL=$((FAIL+1))
fi

# 檢查 4：MEMORY.md 可讀取
echo ""
echo "[4/4] 檢查記憶系統..."
MEMORY="$MOTHER/000_Agent/memory/MEMORY.md"
if [ -f "$MEMORY" ]; then
  LINE_COUNT=$(wc -l < "$MEMORY" | tr -d ' ')
  echo "  ✅ MEMORY.md 可讀取（$LINE_COUNT 行）"
else
  echo "  ❌ MEMORY.md 讀不到：$MEMORY"
  FAIL=$((FAIL+1))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$FAIL" = "0" ]; then
  echo "🎉 全部正常！你的 AI 分身活著。"
  echo "   下次體檢：下週五"
else
  echo "⚠️  發現 $FAIL 個問題，建議檢查："
  echo "   1. 確認 Dropbox 已完整同步"
  echo "   2. 如問題持續，從 ~/claude-backup-* 還原後重跑 pro-kit 07"
  exit 1
fi
