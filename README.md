# Daily Sports Brief — free GitHub Actions pipeline

Publishes an auto-updating page to `https://malathirenati.github.io/sports/brief/`
every day at 9:30am IST, using only things GitHub gives you for free:
GitHub Actions (free, unlimited minutes on a public repo) and GitHub Pages
(free static hosting). No Claude subscription, no paid API, no other
account of any kind is required to keep this running.

**Read `LIMITATIONS.md` before you rely on this** — it explains exactly what
this automated version can and can't do compared to the brief you've seen
Claude produce in chat.

## One-time setup (about 5 minutes)

1. **Create the repo.** On GitHub, create a new **public** repository named
   exactly `sports` under your account (`malathirenati/sports`). Public is
   required for GitHub Actions and Pages to be free and unlimited — a
   private repo works too but Actions minutes are capped on the free plan
   (2,000 min/month, plenty for this, but public is simplest).

2. **Add these files** to the repo, preserving the folder structure:
   ```
   .github/workflows/daily-brief.yml
   scripts/generate_brief.py
   README.md
   LIMITATIONS.md
   ```
   Easiest way: unzip the delivered `sports-brief-action.zip` into the repo
   folder, then commit and push.

3. **Allow the workflow to push.** In the repo, go to
   **Settings → Actions → General → Workflow permissions**, choose
   **"Read and write permissions"**, and save. This is a one-time setting —
   it is not a per-run approval, and nobody has to click anything once it's
   set.

4. **Turn on GitHub Pages.** Go to **Settings → Pages**. Under
   **Build and deployment → Source**, choose **"Deploy from a branch"**,
   then branch **`gh-pages`**, folder **`/ (root)`**. Save.
   (The `gh-pages` branch doesn't exist yet — it's fine, it gets created
   automatically the first time the workflow runs. Come back and set this
   after step 5's first run if the branch isn't listed yet.)

5. **Trigger the first run.** Go to the **Actions** tab → **Daily Sports
   Brief** workflow → **Run workflow** (this is the `workflow_dispatch`
   trigger — a manual click *you* make once to kick things off; after this,
   the daily 9:30am IST schedule runs itself with no further clicks).

6. **Check the page.** After the run finishes (~30 seconds), visit
   `https://malathirenati.github.io/sports/brief/`. It can take a minute or
   two the very first time for Pages to go live.

From here on, the workflow fires itself every day at 9:30am IST
(`cron: '0 4 * * *'`, since IST is UTC+5:30) and pushes the new page — no
approvals, no manual steps, no cost.

## Changing the schedule or the topics

- **Time:** edit the `cron:` line in `.github/workflows/daily-brief.yml`.
  Cron is in UTC — subtract 5:30 from your desired IST time.
- **What gets pulled:** edit the `BUCKETS` list at the top of
  `scripts/generate_brief.py` — each entry is a plain Google News search
  query string, no code changes needed elsewhere.

## Testing locally

```bash
cd sports
python3 scripts/generate_brief.py
open public/brief/index.html   # or just open the file in a browser
```

## Cost, forever

- GitHub Actions on a public repo: free, no minute limit.
- GitHub Pages: free.
- Google News RSS: free, public, no API key, no rate-limit account needed.
- This repo, run daily: **$0/month, indefinitely**, with no subscription
  of any kind — Claude or otherwise — required to keep it running.

The only way this ever costs money is if you deliberately add a paid
service to it later (see `LIMITATIONS.md` for what that would buy you).
