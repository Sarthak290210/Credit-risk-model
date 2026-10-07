import math

import streamlit as st
from prediction_helper import predict  # Ensure this is correctly linked to your prediction_helper.py

# ---------------------------------------------------------------------------
# Optional: shown in the footer. Leave a link empty to hide it.
# ---------------------------------------------------------------------------
AUTHOR = "Sarthak"
GITHUB_URL = ""
LINKEDIN_URL = ""

st.set_page_config(page_title="Credit Risk Scorecard", page_icon="📊", layout="wide")


# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
SCORE_MIN, SCORE_MAX = 300, 900

# Same cut-offs as get_rating() in prediction_helper.py
BANDS = [
    (300, 500, "Poor", "300–499"),
    (500, 650, "Average", "500–649"),
    (650, 750, "Good", "650–749"),
    (750, 900, "Excellent", "750–900"),
]
TONES = {
    "Poor": "#B3261E",
    "Average": "#C98A12",
    "Good": "#2A8A82",
    "Excellent": "#1D6B43",
}
VERDICTS = {
    "Poor": "High risk of default.",
    "Average": "Moderate risk of default.",
    "Good": "Low risk of default.",
    "Excellent": "Very low risk of default.",
}
NEUTRAL_TONE = "#9AA5B3"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Public+Sans:wght@400;500;600&display=swap');

:root {
  --ink: #14283C;
  --paper: #F2F4F6;
  --surface: #FFFFFF;
  --rule: #D5DBE2;
  --muted: #5A6778;
  --display: 'Bricolage Grotesque', 'Segoe UI', system-ui, sans-serif;
  --body: 'Public Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

/* ---- page frame ---- */
.stApp { background: var(--paper); color: var(--ink); font-family: var(--body); color-scheme: light; }
.stApp .block-container { max-width: 1120px; padding: 2rem 1.5rem 4rem; }
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, [data-testid="stDeployButton"], .stAppDeployButton { display: none; }
.stApp input, .stApp button { font-family: var(--body); }

/* ---- masthead ---- */
.stApp h1.title {
  font-family: var(--display); font-weight: 700; color: var(--ink);
  font-size: clamp(2rem, 4.2vw, 2.9rem); line-height: 1.05; letter-spacing: -0.02em;
  margin: 0 0 0.7rem !important; padding: 0 !important;
}
.lede { max-width: 58ch; margin: 0; color: var(--muted); font-size: 1.05rem; line-height: 1.55; }
.lede + .lede { margin-top: 0.5rem; }
.lede strong { color: var(--ink); font-weight: 600; }

/* ---- form ---- */
.sec {
  font-family: var(--display); font-weight: 600; font-size: 1.08rem; color: var(--ink);
  margin: 1.9rem 0 0.9rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--rule);
}
.sec.first { margin-top: 2.2rem; }
.stApp [data-testid="stWidgetLabel"] p { font-size: 0.84rem; font-weight: 500; color: var(--ink); }
.stApp [data-testid="stNumberInputContainer"],
.stApp [data-testid="stSelectbox"] [role="group"],
.stApp [data-baseweb="input"],
.stApp [data-baseweb="select"] > div {
  background: var(--surface); border: 1px solid #C3CBD5; border-radius: 8px; box-shadow: none;
}
.stApp [data-baseweb="input"] > div { background: transparent; }
.stApp [data-testid="stNumberInputContainer"]:focus-within,
.stApp [data-testid="stSelectbox"] [role="group"]:focus-within,
.stApp [data-baseweb="input"]:focus-within,
.stApp [data-baseweb="select"] > div:focus-within {
  border-color: var(--ink); box-shadow: 0 0 0 3px rgba(20, 40, 60, 0.14);
}
.stApp [data-testid="stNumberInputContainer"] input, .stApp [data-testid="stSelectbox"] input { background: transparent; }
.stApp input { font-variant-numeric: tabular-nums; color: var(--ink); }
.stApp [data-testid="stCaptionContainer"] { color: var(--muted); font-size: 0.8rem; margin-top: -0.4rem; font-variant-numeric: tabular-nums; }

.readout {
  display: flex; justify-content: space-between; align-items: baseline; gap: 1rem;
  padding: 0.65rem 0.85rem; margin: 0.2rem 0 0.4rem;
  background: rgba(20, 40, 60, 0.05); border-radius: 8px; font-size: 0.88rem;
}
.readout span { color: var(--muted); }
.readout strong { font-family: var(--display); font-size: 1.1rem; font-variant-numeric: tabular-nums; }

.stApp [data-testid="stButton"] { width: 100% !important; margin-top: 2.2rem; }
.stApp [data-testid="stButton"] button { width: 100%; }
.stApp [data-testid="stBaseButton-primary"] {
  background: var(--ink); color: #fff; border: 1px solid var(--ink); border-radius: 8px;
  padding: 0.7rem 1.2rem; font-weight: 600; font-size: 0.98rem; letter-spacing: 0.01em;
  transition: background 0.15s ease;
}
.stApp [data-testid="stBaseButton-primary"] p { font-size: 1rem; font-weight: 600; }
.stApp [data-testid="stBaseButton-primary"]:hover { background: #24425F; border-color: #24425F; color: #fff; }
.stApp [data-testid="stBaseButton-primary"]:focus-visible { outline: 3px solid #2A8A82; outline-offset: 2px; }

/* ---- result panel ---- */
.result {
  background: var(--surface); border: 1px solid var(--rule); border-top: 4px solid var(--tone, #9AA5B3);
  border-radius: 12px; padding: 1.6rem 1.6rem 1.3rem; margin-top: 1.1rem;
}
.result svg { display: block; width: 100%; height: auto; max-width: 400px; margin: 0 auto; }
.score { text-align: center; font-family: var(--display); font-weight: 700; font-size: 3.6rem; line-height: 1; letter-spacing: -0.03em; margin-top: 0.1rem; font-variant-numeric: tabular-nums; }
.score.empty { color: #B8C0CB; }
.score-label { text-align: center; color: var(--muted); font-size: 0.85rem; margin: 0.3rem 0 1rem; }
.metric { display: flex; justify-content: space-between; align-items: baseline; padding: 0.7rem 0; border-top: 1px solid var(--rule); font-size: 0.92rem; }
.metric span { color: var(--muted); }
.metric strong { font-family: var(--display); font-size: 1.15rem; font-weight: 600; font-variant-numeric: tabular-nums; display: inline-flex; align-items: center; gap: 0.5rem; }
.metric .dot { width: 0.7rem; height: 0.7rem; border-radius: 50%; background: var(--tone); display: inline-block; }
.meter { height: 6px; background: #E6EAEF; border-radius: 3px; overflow: hidden; margin: -0.15rem 0 0.7rem; }
.meter i { display: block; height: 100%; background: var(--tone); border-radius: 3px; }
.verdict { margin: 0.9rem 0 0; font-size: 0.95rem; line-height: 1.5; }
.legend { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem 1rem; max-width: 300px; margin: 0 auto; font-size: 0.8rem; color: var(--muted); }
.legend span { display: inline-flex; align-items: center; gap: 0.4rem; }
.legend i { width: 0.65rem; height: 0.65rem; border-radius: 2px; display: inline-block; }
.legend .on { color: var(--ink); font-weight: 600; }
.formula { margin: 1.3rem 0 0; padding-top: 1rem; border-top: 1px solid var(--rule); color: var(--muted); font-size: 0.8rem; line-height: 1.5; }

.needle { transform-box: view-box; transform-origin: 210px 200px; transform: rotate(var(--end, 0deg)); animation: sweep 0.95s cubic-bezier(0.2, 0.7, 0.2, 1); }
@keyframes sweep { from { transform: rotate(0deg); } to { transform: rotate(var(--end, 0deg)); } }
@media (prefers-reduced-motion: reduce) { .needle { animation: none; } }
@media (max-width: 640px) { .stApp [data-testid="stButton"] { margin-top: 1.2rem; } .score { font-size: 3.2rem; } }

/* ---- about the model ---- */
.about-title { font-family: var(--display); font-weight: 700; font-size: 1.6rem; letter-spacing: -0.01em; margin: 3.4rem 0 0.4rem; padding-top: 1.6rem; border-top: 1px solid var(--rule); }
.about-intro { max-width: 62ch; color: var(--muted); line-height: 1.55; margin: 0 0 1.4rem; }
.sub { font-family: var(--display); font-weight: 600; font-size: 1.02rem; margin: 0 0 0.8rem; }
.steps { list-style: none; counter-reset: step; margin: 0; padding: 0; }
.steps li { counter-increment: step; position: relative; padding: 0 0 0.95rem 2.2rem; font-size: 0.92rem; line-height: 1.5; }
.steps li::before {
  content: counter(step); position: absolute; left: 0; top: 0.05rem; width: 1.45rem; height: 1.45rem; border-radius: 50%;
  border: 1px solid var(--ink); font-size: 0.75rem; font-weight: 600; display: flex; align-items: center; justify-content: center;
}
.steps li::after { content: ""; position: absolute; left: 0.725rem; top: 1.6rem; bottom: 0.15rem; width: 1px; background: var(--rule); }
.steps li:last-child::after { display: none; }
.steps b { font-weight: 600; }
.stats { margin: 0 0 1.1rem; padding: 0; }
.stats div { display: flex; justify-content: space-between; align-items: baseline; padding: 0.6rem 0; border-bottom: 1px solid var(--rule); font-size: 0.92rem; }
.stats div:first-child { border-top: 1px solid var(--rule); }
.stats dt { color: var(--muted); }
.stats dd { margin: 0; font-family: var(--display); font-weight: 600; font-size: 1.1rem; font-variant-numeric: tabular-nums; }
.note { font-size: 0.88rem; line-height: 1.55; color: var(--muted); margin: 0 0 1.2rem; max-width: 60ch; }
.note strong { color: var(--ink); font-weight: 600; }
.colophon { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--rule); color: var(--muted); font-size: 0.82rem; line-height: 1.6; }
.colophon a { color: var(--ink); font-weight: 600; text-decoration: underline; text-underline-offset: 3px; }
</style>
"""


# ---------------------------------------------------------------------------
# Helpers (presentation only)
# ---------------------------------------------------------------------------
def html(markup: str) -> None:
    """Render raw HTML. Whitespace is collapsed so Markdown never splits the block."""
    st.markdown(" ".join(markup.split()), unsafe_allow_html=True)


def fmt_inr(value) -> str:
    """12,00,000 style digit grouping."""
    digits = str(int(value))
    if len(digits) <= 3:
        return digits
    head, tail = digits[:-3], digits[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups + [tail])


def section(title: str, first: bool = False) -> None:
    html(f'<div class="sec{" first" if first else ""}">{title}</div>')


CX, CY, RADIUS, BAND_WIDTH = 210, 200, 150, 22


def _point(score: float, radius: float):
    angle = math.radians(180 - 180 * (score - SCORE_MIN) / (SCORE_MAX - SCORE_MIN))
    return CX + radius * math.cos(angle), CY - radius * math.sin(angle)


def gauge_svg(score=None, rating=None) -> str:
    """Semicircle gauge: four bands that match the rating cut-offs, plus a needle."""
    parts = []
    for low, high, name, _ in BANDS:
        x0, y0 = _point(low + 2, RADIUS)
        x1, y1 = _point(high - 2, RADIUS)
        dim = rating is not None and name != rating
        parts.append(
            f'<path d="M {x0:.2f} {y0:.2f} A {RADIUS} {RADIUS} 0 0 1 {x1:.2f} {y1:.2f}" '
            f'fill="none" stroke="{TONES[name]}" stroke-width="{BAND_WIDTH}" '
            f'opacity="{0.22 if dim else 1}"/>'
        )
    for tick in (300, 500, 650, 750, 900):
        tx, ty = _point(tick, RADIUS + 30)
        parts.append(
            f'<text x="{tx:.1f}" y="{ty + 4:.1f}" text-anchor="middle" font-size="12" '
            f'fill="#5A6778" style="font-variant-numeric:tabular-nums">{tick}</text>'
        )
    if score is not None:
        end = 180 * (score - SCORE_MIN) / (SCORE_MAX - SCORE_MIN)
        tip = CX - 128
        parts.append(
            f'<g class="needle" style="--end:{end:.1f}deg">'
            f'<polygon points="{tip},{CY} {CX},{CY - 5} {CX + 16},{CY} {CX},{CY + 5}" fill="#14283C"/></g>'
        )
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="10" fill="#14283C"/><circle cx="{CX}" cy="{CY}" r="3.5" fill="#fff"/>')
    label = f"Credit score {score}, rated {rating}" if score is not None else "Credit score gauge from 300 to 900"
    return (
        f'<svg viewBox="0 0 420 216" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg">'
        + "".join(parts)
        + "</svg>"
    )


def legend_html(active=None) -> str:
    items = []
    for _, _, name, span in BANDS:
        cls = ' class="on"' if name == active else ""
        items.append(f'<span{cls}><i style="background:{TONES[name]}"></i>{name} {span}</span>')
    return f'<div class="legend">{"".join(items)}</div>'


def render_placeholder() -> None:
    html(
        f"""
        <div class="result" style="--tone:{NEUTRAL_TONE}">
          {gauge_svg()}
          <div class="score empty">—</div>
          <div class="score-label">Credit score</div>
          {legend_html()}
          <div class="formula">Enter the borrower's details, then select <strong>Calculate risk</strong>
          to see the default probability, credit score and rating.</div>
        </div>
        """
    )


def render_result(probability, credit_score, rating) -> None:
    tone = TONES.get(rating, NEUTRAL_TONE)
    verdict = VERDICTS.get(rating, "")
    meter = max(min(float(probability) * 100, 100), 1)
    html(
        f"""
        <div class="result" style="--tone:{tone}">
          {gauge_svg(credit_score, rating)}
          <div class="score">{credit_score}</div>
          <div class="score-label">Credit score</div>
          {legend_html(rating)}
          <div class="metric" style="margin-top:1.1rem"><span>Default probability</span><strong>{probability:.2%}</strong></div>
          <div class="meter"><i style="width:{meter:.1f}%"></i></div>
          <div class="metric"><span>Rating</span><strong><i class="dot"></i>{rating}</strong></div>
          <div class="verdict">{verdict}</div>
          <div class="formula">Score = 300 + (1 − default probability) × 600, so every borrower lands between 300 and 900.</div>
        </div>
        """
    )


html(CSS)

# ---------------------------------------------------------------------------
# Masthead
# ---------------------------------------------------------------------------
html(
    """
    <h1 class="title">Credit risk scorecard</h1>
    <p class="lede">Enter a borrower's loan and credit details to estimate the probability of default
    and a credit score from 300 to 900.</p>
    <p class="lede">Behind it is a logistic regression model trained on 50,000 loans.
    On held-out loans it <strong>catches 94% of the borrowers who default</strong>.</p>
    """
)

left, right = st.columns([1.12, 1], gap="large")

# ---------------------------------------------------------------------------
# Inputs (same widgets, ranges and defaults as before)
# ---------------------------------------------------------------------------
with left:
    section("Applicant", first=True)
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input('Age', min_value=18, step=1, max_value=100, value=28)
    with c2:
        residence_type = st.selectbox('Residence type', ['Owned', 'Rented', 'Mortgage'])
    income = st.number_input('Income (₹)', min_value=0, step=10000, value=1200000)
    st.caption(f"₹ {fmt_inr(income)}")

    section("Loan")
    c1, c2 = st.columns(2)
    with c1:
        loan_purpose = st.selectbox('Loan purpose', ['Education', 'Home', 'Auto', 'Personal'])
    with c2:
        loan_type = st.selectbox('Loan type', ['Unsecured', 'Secured'])
    c1, c2 = st.columns(2)
    with c1:
        loan_amount = st.number_input('Loan amount (₹)', min_value=0, step=10000, value=2560000)
        st.caption(f"₹ {fmt_inr(loan_amount)}")
    with c2:
        loan_tenure_months = st.number_input('Loan tenure (months)', min_value=0, step=1, value=36)

    loan_to_income_ratio = loan_amount / income if income > 0 else 0
    html(
        f'<div class="readout"><span>Loan-to-income ratio (loan amount ÷ income)</span>'
        f'<strong>{loan_to_income_ratio:.2f}</strong></div>'
    )

    section("Credit history")
    c1, c2 = st.columns(2)
    with c1:
        num_open_accounts = st.number_input(
            'Open loan accounts', min_value=1, max_value=4, step=1, value=2,
            help="Number of loan accounts currently open (1 to 4).",
        )
        delinquency_ratio = st.number_input(
            'Delinquency ratio (%)', min_value=0, max_value=100, step=1, value=30,
            help="Share of the borrower's loan months that were delinquent.",
        )
    with c2:
        credit_utilization_ratio = st.number_input(
            'Credit utilization (%)', min_value=0, max_value=100, step=1, value=30,
            help="Share of available credit the borrower is currently using.",
        )
        avg_dpd_per_delinquency = st.number_input(
            'Avg days past due', min_value=0, value=20,
            help="Average days past due in each delinquent month.",
        )


# ---------------------------------------------------------------------------
# Result (the button lives here so the answer appears right beneath it)
# ---------------------------------------------------------------------------
with right:
    try:
        calculate = st.button('Calculate risk', type="primary", width="stretch")
    except TypeError:  # older Streamlit versions
        calculate = st.button('Calculate risk', type="primary", use_container_width=True)
    if calculate:
        # Call the predict function from the helper module
        probability, credit_score, rating = predict(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
                                                    delinquency_ratio, credit_utilization_ratio, num_open_accounts,
                                                    residence_type, loan_purpose, loan_type)
        render_result(probability, credit_score, rating)
    else:
        render_placeholder()

# ---------------------------------------------------------------------------
# About the model
# ---------------------------------------------------------------------------
html(
    """
    <div class="about-title">About the model</div>
    <p class="about-intro">The form asks for the ten inputs the final model uses: age, residence type,
    loan purpose, loan type, loan tenure, open accounts, credit utilization, delinquency ratio,
    average days past due, and loan-to-income ratio (from income and loan amount).</p>
    """
)

about_left, about_right = st.columns([1.12, 1], gap="large")

with about_left:
    html(
        """
        <div class="sub">How it was built</div>
        <ol class="steps">
          <li><b>Data.</b> Joined customer, loan and bureau tables into 50,000 loans, 8.6% of which defaulted.
          The train and test split happens before cleaning, to avoid data leakage.</li>
          <li><b>Cleaning.</b> Fixed a loan-purpose typo, filled missing residence types, and removed loans
          whose processing fee was above 3% of the amount.</li>
          <li><b>Feature engineering.</b> Created loan-to-income, delinquency ratio, and average days past due
          per delinquent month.</li>
          <li><b>Feature selection.</b> Dropped collinear columns (VIF above 10), then kept features with
          information value above 0.02.</li>
          <li><b>Class balance.</b> Rebalanced the training set with SMOTE-Tomek.</li>
          <li><b>Model.</b> Logistic regression tuned with Optuna on cross-validated macro F1. It beat XGBoost
          on recall for defaults (0.94 against 0.92) and is easier to explain to stakeholders.</li>
        </ol>
        """
    )

with about_right:
    html(
        """
        <div class="sub">Results on 14,997 held-out loans</div>
        <dl class="stats">
          <div><dt>ROC AUC</dt><dd>0.983</dd></div>
          <div><dt>Gini coefficient</dt><dd>0.966</dd></div>
          <div><dt>KS statistic</dt><dd>85.7%</dd></div>
          <div><dt>Recall on defaults</dt><dd>94%</dd></div>
          <div><dt>Precision on defaults</dt><dd>56%</dd></div>
        </dl>
        <div class="note"><strong>The trade-off is deliberate.</strong> Missing a borrower who defaults costs more
        than reviewing a good one by mistake, so the model favors recall. The price is lower precision:
        some safe borrowers get flagged.</div>
        """
    )

links = []
if GITHUB_URL:
    links.append(f'<a href="{GITHUB_URL}" target="_blank" rel="noopener">GitHub</a>')
if LINKEDIN_URL:
    links.append(f'<a href="{LINKEDIN_URL}" target="_blank" rel="noopener">LinkedIn</a>')
link_text = (" Find me on " + " and ".join(links) + ".") if links else ""

html(
    f"""
    <div class="colophon">Built by {AUTHOR} with scikit-learn, imbalanced-learn, Optuna, FastAPI and Streamlit.
    The same model is available as a REST endpoint.{link_text}</div>
    """
)