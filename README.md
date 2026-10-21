# Cloud AI GitHub delivery pipeline

A small demo that uses GitHub-hosted runners for CI, AI inference, and deployment. It does not require a Copilot subscription or a self-hosted runner. AI inference uses the Gemini Developer API free tier; a Gemini API key is stored as a GitHub Actions secret.

```text
PR → GitHub-hosted tests → Gemini generates test cases → fixed test harness runs them
   → Gemini reviews the diff → findings are posted to the PR
main push → same tests and AI test generation → deploy site/ to GitHub Pages
```

## Agents

- **QA agent** (`agents/generate_tests.py`) asks Gemini for behavioral test cases as JSON. The model returns data, not executable code; `agents/run_generated_tests.py` validates and executes cases through a fixed harness.
- **Review agent** (`agents/review_diff.py`) reviews a PR diff and posts structured findings as a PR comment.
- **Deployment** publishes the static `site/` folder to GitHub Pages after baseline and AI-generated tests pass on `main`.

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

## Cost and data

- GitHub-hosted Actions are free for public repositories under GitHub's current policy. Gemini offers a free tier with request limits; availability and quotas can change.
- Gemini's free-tier prompts may be used by Google to improve its products. Do not send secrets, private source, or sensitive data through the free tier. This demo repository is public.
- If the free quota is exceeded, AI jobs fail; ordinary baseline tests still run. No automatic paid upgrade or fallback is configured.

## Local checks

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s agents -p 'test_*.py' -v
```
