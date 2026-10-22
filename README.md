# Cloud AI GitHub delivery pipeline

A small demo that uses GitHub-hosted runners for CI, AI inference, and deployment. It does not require a Copilot subscription or a self-hosted runner. AI inference uses the Gemini Developer API free tier; a Gemini API key is stored as a GitHub Actions secret.

**Live demo:** [https://ehrlichsei.github.io/local-ai-delivery-pipeline/](https://ehrlichsei.github.io/local-ai-delivery-pipeline/)

```text
PR → GitHub-hosted tests → Gemini generates test cases → fixed test harness runs them
   → Gemini reviews the diff → findings are posted to the PR
main push → same tests and AI test generation → deploy site/ to GitHub Pages
```

## Agents

- **QA agent** (`agents/generate_tests.py`) asks Gemini for behavioral test cases as JSON. The model returns data, not executable code; `agents/run_generated_tests.py` validates and executes cases through a fixed harness.
- **Review agent** (`agents/review_diff.py`) reviews a PR diff and posts structured findings as a PR comment.
- **Issue coding agent** (`.github/workflows/issue-agent.yml`) turns a repository issue into a constrained code proposal, runs tests, and opens a PR for human review.
- **Deployment** publishes the static `site/` folder to GitHub Pages after baseline and AI-generated tests pass on `main`.

The deployed page includes a browser-only calculator playground with addition, subtraction, multiplication, division, exponentiation, input errors, and a five-item calculation history. Values stay in the browser and are not sent to an API. The Python `app.py` calculator also supports modulo; this backend function is covered by tests but is not wired into the browser playground.

AI suggestions can miss defects or report false positives. Keep human review and merge approval.

## One-time GitHub setup

1. Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/app/apikey).
2. In this repository, open **Settings → Secrets and variables → Actions → New repository secret**. Name it `GEMINI_API_KEY` and paste the key. Never commit the key into the repository.
3. In **Settings → Pages → Build and deployment**, set the source to **GitHub Actions**.
4. Keep the default branch as `main`. Require the `Baseline tests` check and human PR review before merging.

The default model is `gemini-3.5-flash-lite`. To choose another model, add an Actions variable named `GEMINI_MODEL` with a model ID available to your Gemini API project.

## Triggers

- Opening or updating a PR to `main` runs baseline tests, AI-generated tests, and AI review. Fork PRs still get baseline tests; AI jobs skip them because GitHub does not provide repository secrets to fork workflows.
- A push or merge to `main` reruns tests and AI test generation, then deploys the site if both jobs pass.
- To request an implementation, open an issue and ask the repository owner to add the `ai:implement` label. The issue agent generates changes only for `app.py`, `tests/test_app.py`, and `README.md`, validates the patch, runs the tests, and opens a PR if they pass. It never merges or deploys by itself; merging its PR follows the normal review and deployment flow. The label-triggered workflow runs only when the label is added by the repository owner.
- The Issue agent also scans open issues every Monday at 09:17 UTC. It triages at most five unscanned issues and processes at most one suitable task per run. It marks checked issues with `ai:scanned`; if one is suitable, it adds `ai:implement` and continues through the same tests and PR flow. Remove `ai:scanned` to let the next scan consider an issue again. Run the scan immediately from **Actions → Issue coding agent → Run workflow**; an optional issue number skips triage and selects that issue directly.
- Scheduled triage sends public issue titles and bodies to Gemini. Do not put secrets or sensitive information in repository issues.
- For Actions to open PRs automatically, enable **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests**. PRs created with the built-in workflow token may require a maintainer to approve their workflow checks.

## Cost and data

- GitHub-hosted Actions are free for public repositories under GitHub's current policy. Gemini offers a free tier with request limits; availability and quotas can change.
- Gemini's free-tier prompts may be used by Google to improve its products. Do not send secrets, private source, or sensitive data through the free tier. This demo repository is public.
- If the free quota is exceeded, AI jobs fail; ordinary baseline tests still run. No automatic paid upgrade or fallback is configured.

## Local checks

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s agents -p 'test_*.py' -v
```
