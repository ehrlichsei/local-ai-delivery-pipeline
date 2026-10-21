# 本地 AI 驱动的 GitHub 交付流水线

一个不依赖 Copilot 订阅或模型 API key 的小型 demo。Ollama 在自己的电脑上提供模型，GitHub Actions 负责事件编排和部署：

```text
PR → 本地 Ollama 生成行为测试 → 跑固定测试执行器 → 本地 Ollama 审查 diff → PR 留言
主分支 push → 同一套 AI 测试通过 → GitHub Pages 部署
```

## Agent 做什么

- **QA agent** (`agents/generate_tests.py`) 阅读 `app.py`，让模型输出 JSON 测例。生成的是数据而不是 Python 代码，再由固定的 `run_generated_tests.py` 执行，避免直接运行模型生成的脚本。
- **Review agent** (`agents/review_diff.py`) 阅读 PR diff，输出结构化发现，并由 workflow 留言到 PR。
- **部署**由 GitHub Pages Actions 完成，仅在 `main` 的 push 且 AI 测试成功后运行。

模型输出可能漏测或误报。AI review 只是辅助信息，PR 仍需人类检查和合并。

## 准备

1. 把本目录内容放进一个独立 GitHub repository 的根目录。PR 的 AI jobs 仅对同仓库分支运行，来自 fork 的 PR 会跳过自托管 runner。
2. 在一台常开且安装了 Git、Python 3.11+、Ollama 的电脑上注册 GitHub self-hosted runner。给 runner 添加自定义 label：`ollama`；本工作流按 `self-hosted, Windows, X64, ollama` 选择它。
3. 在 runner 电脑启动 Ollama 并下载模型：

   ```powershell
   ollama pull qwen2.5-coder:7b
   ollama run qwen2.5-coder:7b
   ```

   Ollama 默认 API 地址为 `http://127.0.0.1:11434`。确保 runner 服务进程能访问该地址；若 Ollama 跑在另一台机器上，在仓库 Settings → Secrets and variables → Actions → Variables 中设置 `OLLAMA_BASE_URL` 和 `OLLAMA_MODEL`。

4. 在 GitHub 仓库 Settings → Pages → Build and deployment 选择 **GitHub Actions**。
5. 将 `main` 设为默认分支，并建议设置 branch protection：要求 `AI-generated tests + baseline tests` 成功；由人类完成 PR review 和合并。

## 触发

- 开 PR 到 `main`：执行 AI 生成测例、baseline tests 和 AI review；review 结果作为 PR 评论。
- push/merge 到 `main`：重新跑 AI 测试，通过后发布 `site/` 到 GitHub Pages。
- 也可以在 runner 电脑本地试：

  ```powershell
  $env:OLLAMA_MODEL = "qwen2.5-coder:7b"
  python agents/generate_tests.py
  python -m unittest discover -s tests -v
  python agents/run_generated_tests.py
  ```

## 安全边界

- PR 分支里的 workflow、依赖和代码可能在 runner 上执行。工作流会跳过 fork PR；仍只应让可信写入者创建的同仓库分支使用 runner。GitHub 建议公开仓库避免使用持久自托管 runner；公开仓库应改用隔离的临时虚拟机或 GitHub-hosted runner。
- 给 runner 单独创建操作系统用户和工作目录，不存放日常账号凭据。GitHub Pages deploy 使用 GitHub 提供的短期 Actions token，不需要个人访问令牌。
- Ollama 和模型运行在本机；GitHub 仍托管代码、workflow 日志和部署产物。自托管 runner 与 GitHub Pages 用量仍受 GitHub 计划和额度约束。
- AI 测试只接受有限 JSON schema，由固定 harness 执行；依然要把测试结果和模型评审当作建议，不能替代人工判断。
