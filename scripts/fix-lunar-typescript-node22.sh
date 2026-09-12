#!/usr/bin/env bash
# scripts/fix-lunar-typescript-node22.sh
#
# 修复 iztro 1.8.6 + Node 22 ESM 解析失败问题。

根因：
  iztro 1.8.6 安装时把 lunar-typescript nested 到
  node_modules/iztro/node_modules/lunar-typescript/ 但只装源码没装 dist/
  Node 22 ESM resolver 严格按 package.json 'exports' 查找 dist/index.cjs
  → Cannot find module '.../lunar-typescript/dist/index.cjs'

修法：
  把 root node_modules/lunar-typescript/dist/ 复制到 nested 目录。

用法：
  bash scripts/fix-lunar-typescript-node22.sh

可重入性：
  - 先检测是否存在 dist/index.cjs
  - 不存在才复制（避免覆盖）
  - 跨平台 bash (git-bash / MSYS)

适用场景：
  - CI / 全新 clone 后跑测试前
  - lunar-typescript 升版本后再次发生
"""
#!/usr/bin/env bash
set -e

# Locate repo root (this script's parent)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ROOT_DIST="$REPO_ROOT/node_modules/lunar-typescript/dist"
NESTED_DEST="$REPO_ROOT/node_modules/iztro/node_modules/lunar-typescript"

echo "[P0-6 fix] Repo root: $REPO_ROOT"

# Check root dist exists
if [ ! -d "$ROOT_DIST" ]; then
    echo "[P0-6 fix] FAIL: $ROOT_DIST 不存在"
    echo "  请先运行: npm install 或 npm install lunar-typescript"
    exit 1
fi

# Check nested dest exists
if [ ! -d "$NESTED_DEST" ]; then
    echo "[P0-6 fix] FAIL: $NESTED_DEST 不存在"
    echo "  请先运行: npm install (让 iztro 自动 nested lunar-typescript)"
    exit 1
fi

# Check if already fixed
if [ -f "$NESTED_DEST/dist/index.cjs" ]; then
    echo "[P0-6 fix] OK: $NESTED_DEST/dist/index.cjs 已存在，无需修复"
    exit 0
fi

# Apply fix
echo "[P0-6 fix] 复制 dist/ 到 nested lunar-typescript ..."
cp -r "$ROOT_DIST" "$NESTED_DEST/"

# Verify
if [ -f "$NESTED_DEST/dist/index.cjs" ]; then
    echo "[P0-6 fix] ✅ 修复完成: $NESTED_DEST/dist/index.cjs"
    echo "  验证: node -e \"console.log(require('iztro').astro)\""
else
    echo "[P0-6 fix] ❌ 修复失败"
    exit 1
fi
