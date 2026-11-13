"""Manual UI smoke test (not collected by pytest). Needs API on :8000, frontend on :3000, playwright + Edge.
Run: python tests/e2e/ui_smoke.py"""
import sys

from playwright.sync_api import sync_playwright

R = []


def log(ok, name, extra=""):
    R.append(f"{'PASS' if ok else 'FAIL'}  {name}  {extra}")


with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    ctx = b.new_context(accept_downloads=True)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.on("response", lambda r: errs.append(f"{r.status} {r.url}") if r.status >= 400 else None)
    B = "http://localhost:3000"

    def t(name, fn):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            log(False, name, str(e).splitlines()[0][:160])

    # ---- Score form
    def score():
        pg.goto(B + "/score", wait_until="networkidle")
        pg.click("button:has-text('Score application')")
        pg.wait_for_timeout(300)
        log(pg.locator("text=Required").count() > 0, "score: validation errors on empty form")
        pg.click("text=Fill suspicious sample")
        pg.click("button:has-text('Score application')")
        pg.wait_for_selector("text=Risk assessment", timeout=30000)
        log(pg.locator("text=Top contributing factors").count() == 1, "score: result + factors shown")
        banners = pg.locator("[role=status]").all_inner_texts()
        log(not banners, "score: not using mock fallback", " | ".join(banners)[:200])
        txt = pg.inner_text("main")
        log("/ 100" in txt, "score: display score rendered")
    t("score", score)

    # ---- Applications
    def apps():
        pg.goto(B + "/applications", wait_until="networkidle")
        pg.wait_for_selector("tbody tr")
        pg.select_option("select[aria-label=Tier]", "High")
        pg.wait_for_timeout(1200)
        tiers = pg.locator("tbody tr td:last-child").all_inner_texts()
        log(len(tiers) > 0 and all(x.strip() == "High" for x in tiers), "apps: tier filter", f"{len(tiers)} rows")
        pg.fill("input[aria-label=Search]", "Singh")
        pg.wait_for_timeout(1500)
        names = pg.locator("tbody tr td:nth-child(2)").all_inner_texts()
        log(len(names) > 0 and all("Singh" in n for n in names), "apps: search", f"{len(names)} rows")
        pg.fill("input[aria-label=Search]", "")
        pg.select_option("select[aria-label=Tier]", "")
        pg.wait_for_timeout(1200)
        pg.click("text=Next")
        pg.wait_for_timeout(1000)
        log("Page 2" in pg.inner_text("main"), "apps: pagination")
        pg.click("tbody tr:first-child")
        pg.wait_for_selector("text=Investigation notes", timeout=15000)
        log(pg.locator("text=Profile").count() >= 1, "apps: drawer opens")
        pg.fill("input[placeholder='Add a note…']", "pw test note")
        pg.click("button:has-text('Add')")
        pg.wait_for_selector("text=pw test note", timeout=10000)
        log(True, "apps: note saved")
        pg.click("button[aria-label=Close]")
        log(pg.locator("text=Investigation notes").count() == 0, "apps: drawer closes")
    t("apps", apps)

    # ---- Detail page
    def detail():
        pg.goto(B + "/applications/APP0019998", wait_until="networkidle")
        pg.wait_for_selector("text=Linked entities", timeout=15000)
        log(True, "detail page renders")
        pg.click("a[href^='/network?focus=']:first-of-type >> nth=0")
        pg.wait_for_url("**/network?focus=*", timeout=10000)
        pg.wait_for_selector(".react-flow__node", timeout=15000)
        log(pg.locator(".react-flow__node").count() > 1, "detail -> network link focuses graph",
            f"{pg.locator('.react-flow__node').count()} nodes")
    t("detail", detail)

    # ---- Network
    def net():
        pg.goto(B + "/network", wait_until="networkidle")
        pg.wait_for_selector(".react-flow__node", timeout=20000)
        n = pg.locator(".react-flow__node").count()
        log(n > 1, "network: default hub graph renders", f"{n} nodes, {pg.locator('.react-flow__edge').count()} edges")
        pg.locator(".react-flow__node").nth(1).click()
        pg.wait_for_timeout(500)
        log(pg.locator("text=Click a node in the graph").count() == 0, "network: node select shows details")
        pg.fill("input[aria-label='Entity search']", "device:dev-")
        pg.wait_for_timeout(1200)
        hits = pg.locator("ul button").count()
        log(hits > 0, "network: entity search returns hits", str(hits))
    t("net", net)

    # ---- Models: row select
    def models():
        pg.goto(B + "/models", wait_until="networkidle")
        pg.wait_for_selector("text=Confusion matrix")
        pg.click("tbody tr:has-text('logistic_regression')")
        pg.wait_for_timeout(500)
        log("logistic_regression" in pg.inner_text("main").split("Confusion matrix:")[1][:60], "models: row select switches detail")
        log(pg.locator(".recharts-surface").count() >= 3, "models: charts render", str(pg.locator(".recharts-surface").count()))
    t("models", models)

    # ---- Reports: CSV export
    def reports():
        pg.goto(B + "/reports", wait_until="networkidle")
        with pg.expect_download(timeout=20000) as d:
            pg.click("text=Export CSV")
        path = d.value.path()
        rows = open(path, encoding="utf-8").read().strip().splitlines()
        log(len(rows) > 5 and rows[0].startswith("application_id"), "reports: CSV export", f"{len(rows)} lines")
        pg.click("button:has-text('Low')")
        pg.wait_for_timeout(1000)
        log("Low-tier" in pg.inner_text("main"), "reports: tier switch")
    t("reports", reports)

    # ---- Overview/monitoring/features sanity
    def misc():
        for path, sel in [("/overview", ".recharts-surface"), ("/monitoring", ".recharts-surface"), ("/features", "text=Graph")]:
            pg.goto(B + path, wait_until="networkidle")
            pg.wait_for_selector(sel, timeout=15000)
        log(True, "overview/monitoring/features render")
    t("misc", misc)

    def landing():
        pg.goto(B + "/", wait_until="networkidle")
        log(pg.locator("h1:has-text('Catch fraud rings')").count() == 1, "landing: hero renders")
        log(pg.locator("text=Honest about what it is").count() == 1, "landing: limitations section present")
        pg.click("a:has-text('Explore the dashboard')")
        pg.wait_for_url("**/overview")
        log(pg.locator("h1:has-text('Overview')").count() == 1, "landing: CTA opens dashboard")
    t("landing", landing)

    def hops():
        pg.goto(B + "/network", wait_until="networkidle")
        pg.wait_for_selector(".react-flow__node")
        one = pg.locator(".react-flow__node").count()
        pg.click("button:has-text('2 hops')")
        pg.wait_for_timeout(1500)
        two = pg.locator(".react-flow__node").count()
        log(two > one, "network: 2 hops shows more nodes", f"{one} -> {two}")
    t("hops", hops)

    pg.goto(B + "/does-not-exist")
    log(pg.locator("text=Page not found").count() == 1, "404 page")

    sys.stdout.buffer.write(("\n".join(R) + "\n--- console errors:\n" + "\n".join(sorted(set(errs))) + "\n").encode("utf-8"))
    b.close()
