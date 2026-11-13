# Streams Into Wealth — Stock Intelligence Hub V7

Five-page GitHub Pages website. Extract ZIP and upload **all contents** to repository root (including `.github`, `assets`, `data`, and `scripts`). `index.html` must be in the root.

## What's new in V7
- Research overview: interactive TradingView symbol overview widget with available price/quote metrics (availability/delay depends on TradingView), prominent sector/industry fields, exchange and SEC identifiers.
- SEC company metadata: SEC SIC industry classification, company name and website (where available). Sector remains explicitly **Not verified** until a trustworthy sector taxonomy source is connected; SEC SIC is not identical to GICS sector/industry.
- Annual SEC history table: up to eight fiscal years of revenue, net income, operating cash flow, assets, liabilities, and EPS, if reported in standardized SEC tags.
- More structured moat and competitor research; does not invent moat ratings or competitors for unfamiliar companies.
- Executive profiles and news can render if verified data is supplied; the current free pipeline does **not** populate these fields automatically.
- Expanded economic education, surprise calculator and embedded economic calendar; BLS data refresh covers CPI, core CPI, PPI, unemployment and payrolls only.
- Existing: searchable SEC ticker directory (thousands after refresh), SEC filing links, options and investment calculators, chart/table research, five pages, local watchlist and notes.

## What is NOT implemented
- Reliable real-time quote feed or a guaranteed current market cap/P-E/dividend/52-week range for every ticker. TradingView widget is third-party and can be delayed or omit fields.
- Automatic analyst targets, full company competitor data, moat scores, executive photos, company-specific breaking news, institutional transaction summaries, or economic consensus forecasts.
- Financial snapshots for every ticker: the GitHub Actions job currently refreshes a curated list of roughly 28 companies. Search is broader than financial snapshot coverage.
- Complete macro series coverage. Missing data is labeled.

## GitHub setup
1. Extract ZIP, upload its **contents** to GitHub repository root. Keep directory structure intact.
2. GitHub Settings → Pages → Deploy from branch → main → /(root).
3. GitHub Settings → Secrets and variables → Actions → New repository secret: `SEC_USER_AGENT`. Value must be truthful, such as `StreamsIntoWealth your_real_email@example.com`. Replace with an email you control.
4. GitHub Settings → Actions → General → Workflow permissions → Read and write permissions (if needed).
5. GitHub Actions → **Refresh public market research** → Run workflow. It will fetch SEC directory and curated financials, plus supported BLS series, and commit `data/` changes.
6. Wait for the Pages deployment. Search by ticker or full company name.

## Data interpretation
- SEC latest values are individually selected and can have different reporting periods. Use dates before comparisons.
- Annual history prefers 10-K values and does not interpolate missing data. Some SEC company facts lack standardized tags.
- BLS CPI/PPI are computed from consecutive index levels into month-over-month percentage changes; BLS payrolls are computed from changes in monthly employment levels. Source periods are shown.
- TradingView quote charts are external widgets; this website cannot guarantee update intervals, quote completeness, or exchange entitlements.

## Public sources
- SEC EDGAR API https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- BLS https://www.bls.gov/developers/
- TradingView https://www.tradingview.com/widget-docs/

Educational research only; not investment advice. No fabricated market numbers.
