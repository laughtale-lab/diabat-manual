# Diabat Manual 与 latex2md v0.1.2 固定版本联动

**已经指定转换器提交**：`d61fd12be59f40969a06af7f46aa236fcb88f55a`。

这个工具包只增加第三阶段文件；不会改动现有的 LaTeX 源码或正式 `publish.yml`。
应先在一个 Pull Request 中预览生成的网站，人工检查满意之后再切换生产工作流。

## A. 本地确认 tag 对应的 SHA

```bash
cd ~/github/latex2md
git fetch origin --tags
git rev-parse 'v0.1.2^{}'
```

确认输出恰好等于开头的 SHA。带注释 tag 必须加 `^{}` 才能获取其指向的 commit。

## B. 为 Manual 建立不会发布的预览分支

```bash
cd ~/github/diabat-manual
git switch main
git pull --ff-only
git status   # 需要先确认没有本地未提交内容
git switch -c feature/mdbook-preview
```

将这个压缩包放在仓库**外面**（例如 `~/github/diabat-manual-mdbook-pin-v0.1.2.zip`），
从仓库根目录执行：

```bash
unzip -n ~/github/diabat-manual-mdbook-pin-v0.1.2.zip
cat tools/latex2md.sha
python3 tools/check-latex2md-pin.py
cat .gitignore.APPEND >> .gitignore
rm .gitignore.APPEND
git status --short
python3 -m unittest discover -s tests -v
```

`unzip -n` 在有同名文件时不会覆盖，务必检查提示，确认新文件已经实际加入。
对第一次安装而言，应该新增 `verify-mdbook.yml`、若干 `tools/` 检查文件和 `docs/` 文档；
原来的 `.github/workflows/publish.yml` 必须仍然完全不变。
如果你之前已经解压过旧的联动套件，请**不要**盲目覆盖；先用
`git status`/`git diff` 检查旧文件与本套件，合并已变化的设置，尤其是 SHA。

确认安全后提交本次预览：

```bash
git diff --check
git add .github/workflows/verify-mdbook.yml .gitignore docs/ tools/latex2md.sha \
  tools/check-latex2md-pin.py tools/diabat-2.0-baseline.json \
  tools/audit-mdbook.py tools/write-web-provenance.py tests/test_audit_mdbook.py
git diff --cached --stat
git diff --cached -- .github/workflows/publish.yml
git commit -m 'Preview mdBook using pinned latex2md v0.1.2'
git push -u origin feature/mdbook-preview
```

**注意**：`git diff --cached -- .github/workflows/publish.yml` 没有输出才正常：
首次预览绝不更改生产发布工作流。

## C. GitHub Pull Request 与验收

在 `laughtale-lab/diabat-manual` 仓库的 Pull requests 页面创建 PR：
`feature/mdbook-preview` -> `main`。如果没有自动执行，请查看仓库 Actions
权限或 PR checks 状态；此工作流使用 `pull_request`，不需要事先覆盖 `main`。
PR 预览工作流自动：

1. 用 TeX Live 2025 编译并验证 PDF。
2. 读取 `tools/latex2md.sha`，检出固定转换器 SHA，并二次核验其真实提交。
3. 转换整个手册，验证 13 项初版基准、源文件和交叉引用。
4. 使用 mdBook **0.4.52** 生成 HTML，并逐页检查链接和锚点。
5. 将 HTML 与 PDF 放在**同一**候选目录，上传 `diabat-manual-html-preview` 和转换报告。

该工作流**不部署**，现有 GitHub Pages 保持原状。
从 PR 的成功 Actions 页面底部下载 `diabat-manual-html-preview`，解压后
进入 `index.html` 所在目录，推荐在个人电脑运行：

```bash
python3 -m http.server 8000
```

打开 `http://localhost:8000/`；若文件仍在远程 Linux 集群，可先下载到个人电脑，
或者使用 SSH 端口转发。浏览器不要直接打开 `file://` 页面测试全文搜索。

人工重点看章节导航、全文搜索、图片、数学公式、关键词链接、Script/Example 编号、
语法高亮，以及首页 PDF 链接。另从转换报告核对标签和统计。

## D. 验收后替换唯一的正式发布工作流

继续停留在 `feature/mdbook-preview` 分支：

```bash
cd ~/github/diabat-manual
git status
diff -u .github/workflows/publish.yml docs/publish-mdbook.yml.example || true
```

**仅当第一阶段正式工作流仍为原始版本，且新预览全部通过**，才考虑：

```bash
cp docs/publish-mdbook.yml.example .github/workflows/publish.yml
git diff --check
git diff -- .github/workflows/publish.yml
git add .github/workflows/publish.yml
git commit -m 'Publish verified PDF and mdBook together'
git push origin feature/mdbook-preview
```

如果你对第一阶段的正式发布逻辑做过修改，**不要照抄 `cp`**：
先用 `diff` 比较，再把新转换与验证步骤合并进去，保留已有防护。
最好对同一个 PR 再跑一次完整预览，然后在 GitHub 上合并 PR。
正式发布只保留一个 `.github/workflows/publish.yml`，不同时运行两套 Pages 工作流。

## E. 最终检查与版本追溯

在 GitHub 的 `main` 触发的新 Actions 中，确认构建、转换、mdBook、审计、部署全部成功。
检查：

```bash
curl -fIL https://laughtale-lab.github.io/diabat-manual/
curl -fIL https://laughtale-lab.github.io/diabat-manual/diabat.pdf
curl -fsSL https://laughtale-lab.github.io/diabat-manual/build-info.json
curl -fsSL https://laughtale-lab.github.io/diabat-manual/converter-info.json
curl -fsSL https://laughtale-lab.github.io/diabat-manual/diabat.pdf -o /tmp/diabat-published.pdf
sha256sum /tmp/diabat-published.pdf
```

`converter-info.json` 中的 `latex2md_commit` 必须等于固定 SHA，
PDF SHA-256 必须与两份 JSON 的 PDF 哈希一致。
每次升级转换器，只修改 `tools/latex2md.sha`、重新走 PR 预览和验收，
绝不让正式构建自动追踪转换器 `main`。
