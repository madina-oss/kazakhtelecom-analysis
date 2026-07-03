"""
Финансовый анализ — Калькулятор коэффициентов
Веб-приложение для анализа финансовой отчётности (методология АФО)
Отчётность → Качество → Анализ → Прогноз → Вывод
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ──────────────────────────────────────────────────────────────────────
# КОНФИГУРАЦИЯ СТРАНИЦЫ
# ──────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ФинАнализ — Калькулятор коэффициентов",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────
# КАСТОМНЫЙ CSS — визуальное соответствие макету
# ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #f3f1ec;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0ddd6;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    .nav-label {
        font-size: 10.5px;
        font-weight: 600;
        color: #888780;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin: 14px 0 4px 4px;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: transparent;
        border-radius: 6px;
        padding: 6px 10px;
        margin-bottom: 2px;
        font-size: 13.5px;
        color: #5F5E5A;
        transition: all 0.15s;
        width: 100%;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: #f8f7f4;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] input:checked + div {
        color: #185FA5;
        font-weight: 600;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border: 1px solid #e0ddd6 !important;
        border-radius: 12px !important;
        padding: 4px !important;
    }

    h1 {
        font-size: 26px !important;
        font-weight: 600 !important;
        color: #1a1a18 !important;
    }
    h3 {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #888780 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .stTextInput input, .stNumberInput input {
        border: 1px solid #e0ddd6 !important;
        border-radius: 6px !important;
        background: #ffffff !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #378ADD !important;
        box-shadow: 0 0 0 1px #378ADD !important;
    }

    div[data-testid="column"] .stButton button {
        border-radius: 20px !important;
        border: 1px solid #e0ddd6 !important;
        font-size: 12px !important;
        padding: 4px 14px !important;
        background: #ffffff;
        color: #5F5E5A;
    }

    .stButton button[kind="primary"] {
        background: #185FA5 !important;
        border: none !important;
        border-radius: 6px !important;
        color: #fff !important;
        font-weight: 500 !important;
    }
    .stButton button[kind="primary"]:hover {
        background: #0c447c !important;
    }

    div[data-testid="stMetric"] {
        background: #f8f7f4;
        border: 1px solid #e0ddd6;
        border-radius: 8px;
        padding: 10px 14px;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 11px !important;
        color: #888780 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 20px !important;
        color: #1a1a18 !important;
        font-weight: 500 !important;
    }

    .stDataFrame {
        border: 1px solid #e0ddd6 !important;
        border-radius: 8px !important;
    }

    div[data-testid="stNotification"] {
        border-radius: 8px !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

YEARS = [2020, 2021, 2022, 2023, 2024]

FIELDS = [
    ("revenue", "Выручка", "ОПиУ", "Доходы от основной деятельности"),
    ("cogs", "Себестоимость", "ОПиУ", "Прямые затраты на производство"),
    ("gross", "Валовая прибыль", "ОПиУ", "Выручка минус себестоимость"),
    ("opex", "Операционные расходы (SG&A)", "ОПиУ", "Без себестоимости"),
    ("ebit", "Операционная прибыль (EBIT)", "ОПиУ", "Прибыль до % и налогов"),
    ("ebitda", "EBITDA", "ОПиУ", "EBIT + Амортизация"),
    ("interest", "Финансовые расходы (проценты)", "ОПиУ", "Расходы по займам"),
    ("tax", "Расход по налогу", "ОПиУ", ""),
    ("net", "Чистая прибыль", "ОПиУ", "Итоговая строка ОПиУ"),
    ("totalassets", "Итого Активы", "Баланс", "Валюта баланса"),
    ("cash", "Денежные средства", "Баланс", "Касса + р/с + депозиты"),
    ("ar", "Дебиторская задолженность", "Баланс", ""),
    ("inventory", "Запасы", "Баланс", "Если применимо"),
    ("currentassets", "Итого Оборотные активы", "Баланс", ""),
    ("ppe", "Основные средства (PPE)", "Баланс", "За вычетом амортизации"),
    ("intangibles", "Нематериальные активы", "Баланс", "Включая гудвилл"),
    ("totalliab", "Итого Обязательства", "Баланс", "Краткоср. + долгосроч."),
    ("currentliab", "Краткосрочные обязательства", "Баланс", "Срок < 1 года"),
    ("ltdebt", "Долгосрочные займы", "Баланс", "Срок > 1 года"),
    ("stdebt", "Краткосрочные займы", "Баланс", "Часть займов в тек. обяз."),
    ("equity", "Собственный капитал", "Баланс", "Активы минус Обязательства"),
    ("cfo", "CFO (операционный поток)", "ОДС", "Cash from operations"),
    ("cfi", "CFI (инвестиционный поток)", "ОДС", "Обычно отрицательный"),
    ("cff", "CFF (финансовый поток)", "ОДС", "Дивиденды, займы"),
    ("capex", "Capex (капзатраты)", "ОДС", "Положительное число"),
    ("dividends", "Дивиденды выплаченные", "ОДС", "Положительное число"),
]

# Демо-данные Казахтелекома в тысячах тенге (умножено из млрд × 1 000 000)
# Источники: KASE, годовые отчёты Казахтелекома 2020–2024, см. data/sources.md
DEMO_DATA = {
    2020: {"revenue": 419_000_000, "cogs": 319_000_000, "gross": 100_000_000,
           "ebit": 58_000_000, "ebitda": 173_000_000, "net": 60_300_000,
           "totalassets": 847_000_000, "cash": 94_000_000, "currentassets": 180_000_000,
           "totalliab": 410_000_000, "currentliab": 120_000_000, "ltdebt": 290_000_000,
           "equity": 437_000_000},
    2021: {"revenue": 594_200_000, "cogs": 446_000_000, "gross": 148_000_000,
           "ebit": 96_000_000, "ebitda": 250_000_000, "net": 97_200_000,
           "totalassets": 1_150_000_000, "cash": 167_100_000, "currentassets": 250_000_000,
           "totalliab": 490_000_000, "currentliab": 160_000_000, "ltdebt": 330_000_000,
           "equity": 660_000_000},
    2022: {"revenue": 634_500_000, "cogs": 474_000_000, "gross": 160_000_000,
           "ebit": 120_000_000, "ebitda": 275_000_000, "net": 128_800_000,
           "totalassets": 1_287_000_000, "cash": 150_000_000, "currentassets": 260_000_000,
           "totalliab": 580_000_000, "currentliab": 180_000_000, "ltdebt": 400_000_000,
           "equity": 707_000_000},
    2023: {"revenue": 687_800_000, "cogs": 516_000_000, "gross": 172_000_000,
           "ebit": 130_000_000, "ebitda": 298_000_000, "net": 104_400_000,
           "totalassets": 1_483_000_000, "cash": 160_000_000, "currentassets": 280_000_000,
           "totalliab": 679_300_000, "currentliab": 218_000_000, "ltdebt": 461_000_000,
           "equity": 803_700_000},
    2024: {"revenue": 494_600_000, "cogs": 373_400_000, "gross": 121_200_000,
           "ebit": 110_000_000, "ebitda": 309_000_000, "net": 77_200_000,
           "totalassets": 1_643_400_000, "totalliab": 788_600_000, "equity": 854_800_000},
}

# ──────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = {y: {} for y in YEARS}
if "company_name" not in st.session_state:
    st.session_state.company_name = "Казахтелеком"
if "unit" not in st.session_state:
    st.session_state.unit = "тыс. тенге"
if "current_year" not in st.session_state:
    st.session_state.current_year = YEARS[0]
if "calculated" not in st.session_state:
    st.session_state.calculated = False


def safe_div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def calc_ratios(year):
    d = st.session_state.data.get(year, {})
    g = lambda k: d.get(k)

    rev, net, eq, ta = g("revenue"), g("net"), g("equity"), g("totalassets")
    ebit, ebitda, gross = g("ebit"), g("ebitda"), g("gross")
    ca, cl = g("currentassets"), g("currentliab")
    cash, ar, inv = g("cash"), g("ar"), g("inventory")
    ltd, std, totalliab = g("ltdebt"), g("stdebt"), g("totalliab")
    interest, cfo, capex, cogs = g("interest"), g("cfo"), g("capex"), g("cogs")

    total_debt = None
    if ltd is not None or std is not None:
        total_debt = (ltd or 0) + (std or 0)
    debt_for_ratio = total_debt if total_debt is not None else totalliab
    net_debt = (debt_for_ratio - cash) if (debt_for_ratio is not None and cash is not None) else None
    fcf = (cfo - capex) if (cfo is not None and capex is not None) else None
    quick_assets = (ca - inv) if (ca is not None and inv is not None) else ca

    def pct(x):
        return round(x * 100, 1) if x is not None else None

    def rnd(x, d=2):
        return round(x, d) if x is not None else None

    return {
        # Коэффициенты (безразмерные — не зависят от масштаба валюты)
        "Current Ratio": rnd(safe_div(ca, cl)),
        "Quick Ratio": rnd(safe_div(quick_assets, cl)),
        "Cash Ratio": rnd(safe_div(cash, cl)),
        "Рабочий капитал": rnd((ca - cl) if (ca is not None and cl is not None) else None, 0),
        "Gross Margin %": pct(safe_div(gross, rev)),
        "EBIT Margin %": pct(safe_div(ebit, rev)),
        "EBITDA Margin %": pct(safe_div(ebitda, rev)),
        "Net Margin %": pct(safe_div(net, rev)),
        "ROE %": pct(safe_div(net, eq)),
        "ROA %": pct(safe_div(net, ta)),
        "Debt/Equity": rnd(safe_div(debt_for_ratio, eq)),
        "Debt/Assets": rnd(safe_div(debt_for_ratio, ta)),
        "Equity Ratio %": pct(safe_div(eq, ta)),
        "Net Debt": rnd(net_debt, 0),
        "Net Debt/EBITDA": rnd(safe_div(net_debt, ebitda)),
        "Interest Coverage": rnd(safe_div(ebit, interest)),
        "Asset Turnover": rnd(safe_div(rev, ta)),
        "Receivables Turnover": rnd(safe_div(rev, ar)),
        "DSO (дней)": rnd(safe_div(ar, rev) * 365 if safe_div(ar, rev) is not None else None, 0),
        "Inventory Turnover": rnd(safe_div(cogs, inv)),
        "CFO/Net Income": rnd(safe_div(cfo, net)),
        "FCF": rnd(fcf, 0),
        "FCF Margin %": pct(safe_div(fcf, rev)),
        "CFO/Capex": rnd(safe_div(cfo, capex)),
        # Сырые значения (в тыс. тенге — выводятся как есть, без округления масштаба)
        "revenue": rnd(rev, 0), "net": rnd(net, 0), "equity": rnd(eq, 0),
        "totalassets": rnd(ta, 0), "ebitda": rnd(ebitda, 0),
    }


def fmt_money(v):
    """Форматирует крупные суммы в тыс. тенге с разделителями разрядов."""
    if v is None:
        return "н/д"
    return f"{v:,.0f}".replace(",", " ")


def fmt(v, suffix=""):
    if v is None:
        return "н/д"
    if suffix == "" and abs(v) >= 1000:
        return f"{fmt_money(v)}{suffix}"
    return f"{v:,.2f}{suffix}".replace(",", " ")


def active_years():
    return [y for y in YEARS if any(v is not None for v in st.session_state.data[y].values())]


# ──────────────────────────────────────────────────────────────────────
# SIDEBAR — навигация
# ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("### 📊")
    with col2:
        st.markdown("**ФинАнализ**")
        st.caption("Калькулятор")

    st.markdown('<div class="nav-label">ДАННЫЕ</div>', unsafe_allow_html=True)
    page = st.radio(
        "nav1", ["✏️ Ввод данных"],
        label_visibility="collapsed", key="nav_input"
    )

    st.markdown('<div class="nav-label">АНАЛИЗ</div>', unsafe_allow_html=True)
    page2 = st.radio(
        "nav2",
        ["— нет —", "💧 Ликвидность", "📈 Прибыльность", "🏦 Долговая нагрузка",
         "⚙️ Эффективность", "💵 Денежный поток"],
        label_visibility="collapsed", key="nav_analysis", index=0
    )

    st.markdown('<div class="nav-label">ИТОГ</div>', unsafe_allow_html=True)
    page3 = st.radio(
        "nav3", ["— нет —", "🎯 Дашборд", "🚦 Сигналы"],
        label_visibility="collapsed", key="nav_summary", index=0
    )

    st.markdown("---")
    st.caption("Введите данные баланса, ОПиУ и ОДС — все коэффициенты рассчитываются автоматически")
    st.caption(f"Текущая единица: **{st.session_state.unit}**")

if page2 != "— нет —":
    active_page = page2
elif page3 != "— нет —":
    active_page = page3
else:
    active_page = page

# ──────────────────────────────────────────────────────────────────────
# СТРАНИЦА: ВВОД ДАННЫХ
# ──────────────────────────────────────────────────────────────────────
if active_page == "✏️ Ввод данных":
    st.markdown("# Ввод финансовых данных")
    st.markdown(
        "Введите данные компании за нужные годы. Все суммы — в **тысячах тенге** "
        "(стандартный масштаб финансовой отчётности по МСФО в Казахстане). "
        "После ввода — нажмите «Рассчитать»."
    )

    with st.container(border=True):
        st.markdown("### ИНФОРМАЦИЯ О КОМПАНИИ")
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.company_name = st.text_input("Название компании", st.session_state.company_name)
        with c2:
            st.session_state.unit = st.text_input(
                "Валюта / единица", st.session_state.unit,
                help="Все коэффициенты (ROE, ROA, Current Ratio и др.) безразмерны и не зависят "
                     "от выбранной единицы — единица влияет только на отображение сумм."
            )

    with st.container(border=True):
        st.markdown("### ВЫБЕРИТЕ ГОД ДЛЯ ВВОДА")

        cols = st.columns(len(YEARS))
        for i, y in enumerate(YEARS):
            with cols[i]:
                btn_type = "primary" if y == st.session_state.current_year else "secondary"
                if st.button(str(y), key=f"yr_{y}", type=btn_type, use_container_width=True):
                    st.session_state.current_year = y
                    st.rerun()

        year = st.session_state.current_year
        groups = ["ОПиУ", "Баланс", "ОДС"]

        for grp in groups:
            st.markdown(f"**{grp}**")
            grp_fields = [f for f in FIELDS if f[2] == grp]
            fcols = st.columns(2)
            for idx, (key, label, _, hint) in enumerate(grp_fields):
                with fcols[idx % 2]:
                    current_val = st.session_state.data[year].get(key)
                    val = st.number_input(
                        f"{label} (тыс. ₸)",
                        value=float(current_val) if current_val is not None else None,
                        key=f"in_{year}_{key}",
                        placeholder="0",
                        format="%.0f",
                        step=1000.0,
                        help=hint if hint else None,
                    )
                    st.session_state.data[year][key] = val
            st.markdown("")

    bcol1, bcol2 = st.columns([1.3, 1])
    with bcol1:
        if st.button("Рассчитать коэффициенты", type="primary", use_container_width=True):
            if not active_years():
                st.error("Введите данные хотя бы за один год")
            else:
                st.session_state.calculated = True
                st.success("✅ Коэффициенты рассчитаны! Перейдите в раздел «Анализ» слева.")
    with bcol2:
        if st.button("🗑️ Очистить всё", use_container_width=True):
            st.session_state.data = {y: {} for y in YEARS}
            st.session_state.calculated = False
            st.rerun()

    st.info(
        "💡 Введите данные в тысячах тенге (тыс. ₸). "
        "Заполните хотя бы 1 год для расчёта. "
        "Поля можно оставить пустыми — коэффициент просто не рассчитается."
    )

# ──────────────────────────────────────────────────────────────────────
# СТРАНИЦА: ЛИКВИДНОСТЬ
# ──────────────────────────────────────────────────────────────────────
elif active_page == "💧 Ликвидность":
    st.markdown("# Коэффициенты ликвидности")
    st.caption("Способность компании погашать краткосрочные обязательства. Норма: Current Ratio > 1,5–2,0.")

    yrs = active_years()
    if not yrs:
        st.warning("Нет данных. Перейдите в «Ввод данных» и нажмите «Рассчитать».")
    else:
        results = {y: calc_ratios(y) for y in yrs}
        unit = st.session_state.unit

        with st.container(border=True):
            st.markdown(f"### 📋 Коэффициенты ликвидности — {st.session_state.company_name}")
            df = pd.DataFrame({y: {k: results[y][k] for k in
                ["Current Ratio", "Quick Ratio", "Cash Ratio"]} for y in yrs})
            st.dataframe(df, use_container_width=True)

            wc_df = pd.DataFrame({y: {f"Рабочий капитал ({unit})": fmt_money(results[y]["Рабочий капитал"])} for y in yrs})
            st.dataframe(wc_df, use_container_width=True)

            st.info("**Нормы:** Current Ratio > 1,5–2 — хорошо; <1 — риск. Quick Ratio > 1. Cash Ratio > 0,2. "
                    "Коэффициенты безразмерны и не зависят от единицы измерения сумм.")

        with st.container(border=True):
            st.markdown("### Динамика Current Ratio")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=yrs, y=[results[y]["Current Ratio"] for y in yrs],
                mode="lines+markers", line=dict(color="#185FA5", width=3), marker=dict(size=8)))
            fig.update_layout(height=260, template="plotly_white", margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with st.container(border=True):
            st.markdown("### Динамика Quick Ratio")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=yrs, y=[results[y]["Quick Ratio"] for y in yrs],
                mode="lines+markers", line=dict(color="#0F6E56", width=3), marker=dict(size=8)))
            fig.update_layout(height=260, template="plotly_white", margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────
# СТРАНИЦА: ПРИБЫЛЬНОСТЬ
# ──────────────────────────────────────────────────────────────────────
elif active_page == "📈 Прибыльность":
    st.markdown("# Коэффициенты прибыльности")
    st.caption("ROE, ROA, маржинальность. Показывают насколько эффективно компания зарабатывает прибыль.")

    yrs = active_years()
    if not yrs:
        st.warning("Нет данных. Перейдите в «Ввод данных» и нажмите «Рассчитать».")
    else:
        results = {y: calc_ratios(y) for y in yrs}

        with st.container(border=True):
            st.markdown(f"### 📋 Коэффициенты прибыльности — {st.session_state.company_name}")
            df = pd.DataFrame({y: {k: results[y][k] for k in
                ["Gross Margin %", "EBIT Margin %", "EBITDA Margin %", "Net Margin %", "ROE %", "ROA %"]} for y in yrs})
            st.dataframe(df, use_container_width=True)
            st.info("**Нормы:** ROE > 10–15% — приемлемо; ROA > 5% — хорошо. Маржа и рентабельность — "
                    "относительные показатели (%), не зависят от единицы измерения сумм.")

        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("### ROE (%)")
                fig = go.Figure(go.Bar(x=[str(y) for y in yrs], y=[results[y]["ROE %"] for y in yrs],
                    marker_color="#185FA5"))
                fig.update_layout(height=260, template="plotly_white", margin=dict(t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            with st.container(border=True):
                st.markdown("### ROA (%)")
                fig = go.Figure(go.Bar(x=[str(y) for y in yrs], y=[results[y]["ROA %"] for y in yrs],
                    marker_color="#0F6E56"))
                fig.update_layout(height=260, template="plotly_white", margin=dict(t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)

        with st.container(border=True):
            st.markdown("### Net Margin (%)")
            fig = go.Figure(go.Scatter(x=yrs, y=[results[y]["Net Margin %"] for y in yrs],
                mode="lines+markers", line=dict(color="#EF9F27", width=3), marker=dict(size=8)))
            fig.update_layout(height=260, template="plotly_white", margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────
# СТРАНИЦА: ДОЛГОВАЯ НАГРУЗКА
# ──────────────────────────────────────────────────────────────────────
elif active_page == "🏦 Долговая нагрузка":
    st.markdown("# Долговая нагрузка и платёжеспособность")
    st.caption("Debt/Equity, Debt/Assets, Interest Coverage. Финансовая устойчивость компании.")

    yrs = active_years()
    if not yrs:
        st.warning("Нет данных. Перейдите в «Ввод данных» и нажмите «Рассчитать».")
    else:
        results = {y: calc_ratios(y) for y in yrs}
        unit = st.session_state.unit

        with st.container(border=True):
            st.markdown(f"### 📋 Долговая нагрузка — {st.session_state.company_name}")
            df = pd.DataFrame({y: {k: results[y][k] for k in
                ["Debt/Equity", "Debt/Assets", "Equity Ratio %", "Net Debt/EBITDA", "Interest Coverage"]} for y in yrs})
            st.dataframe(df, use_container_width=True)

            nd_df = pd.DataFrame({y: {f"Чистый долг ({unit})": fmt_money(results[y]["Net Debt"])} for y in yrs})
            st.dataframe(nd_df, use_container_width=True)

            st.info("**Нормы:** D/E < 1–1,5 — умеренно; Net Debt/EBITDA < 2,5; Interest Coverage > 3 — хорошо.")

        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("### Debt / Equity")
                fig = go.Figure(go.Scatter(x=yrs, y=[results[y]["Debt/Equity"] for y in yrs],
                    mode="lines+markers", line=dict(color="#E24B4A", width=3), marker=dict(size=8)))
                fig.update_layout(height=260, template="plotly_white", margin=dict(t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            with st.container(border=True):
                st.markdown("### Debt / Assets")
                fig = go.Figure(go.Scatter(x=yrs, y=[results[y]["Debt/Assets"] for y in yrs],
                    mode="lines+markers", line=dict(color="#BA7517", width=3), marker=dict(size=8)))
                fig.update_layout(height=260, template="plotly_white", margin=dict(t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────
# СТРАНИЦА: ЭФФЕКТИВНОСТЬ
# ──────────────────────────────────────────────────────────────────────
elif active_page == "⚙️ Эффективность":
    st.markdown("# Коэффициенты эффективности")
    st.caption("Оборачиваемость активов, дебиторской задолженности, DSO.")

    yrs = active_years()
    if not yrs:
        st.warning("Нет данных. Перейдите в «Ввод данных» и нажмите «Рассчитать».")
    else:
        results = {y: calc_ratios(y) for y in yrs}

        with st.container(border=True):
            st.markdown(f"### 📋 Эффективность — {st.session_state.company_name}")
            df = pd.DataFrame({y: {k: results[y][k] for k in
                ["Asset Turnover", "Receivables Turnover", "DSO (дней)", "Inventory Turnover"]} for y in yrs})
            st.dataframe(df, use_container_width=True)
            st.info("**Нормы:** DSO < 45 дней — хорошо. Asset Turnover зависит от отрасли (телеком ~0,3–0,5).")

        with st.container(border=True):
            st.markdown("### Asset Turnover")
            fig = go.Figure(go.Scatter(x=yrs, y=[results[y]["Asset Turnover"] for y in yrs],
                mode="lines+markers", line=dict(color="#534AB7", width=3), marker=dict(size=8)))
            fig.update_layout(height=260, template="plotly_white", margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────
# СТРАНИЦА: ДЕНЕЖНЫЙ ПОТОК
# ──────────────────────────────────────────────────────────────────────
elif active_page == "💵 Денежный поток":
    st.markdown("# Анализ денежных потоков")
    st.caption("CFO/Net Income, FCF, FCF Margin. Подтверждает ли денежный поток прибыль?")

    yrs = active_years()
    if not yrs:
        st.warning("Нет данных. Перейдите в «Ввод данных» и нажмите «Рассчитать».")
    else:
        results = {y: calc_ratios(y) for y in yrs}
        unit = st.session_state.unit

        with st.container(border=True):
            st.markdown(f"### 📋 Денежный поток — {st.session_state.company_name}")
            df = pd.DataFrame({y: {k: results[y][k] for k in
                ["CFO/Net Income", "FCF Margin %", "CFO/Capex"]} for y in yrs})
            st.dataframe(df, use_container_width=True)

            fcf_df = pd.DataFrame({y: {f"FCF ({unit})": fmt_money(results[y]["FCF"])} for y in yrs})
            st.dataframe(fcf_df, use_container_width=True)

            st.info("**Нормы:** CFO/Net Income > 0,8 — прибыль подтверждена; FCF > 0 — хороший знак.")

        with st.container(border=True):
            st.markdown(f"### FCF ({unit})")
            fig = go.Figure(go.Scatter(x=yrs, y=[results[y]["FCF"] for y in yrs],
                mode="lines+markers", line=dict(color="#1D9E75", width=3), marker=dict(size=8)))
            fig.update_layout(height=260, template="plotly_white", margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────
# СТРАНИЦА: ДАШБОРД
# ──────────────────────────────────────────────────────────────────────
elif active_page == "🎯 Дашборд":
    st.markdown("# 🎯 Сводный дашборд")
    st.caption("Все ключевые коэффициенты по всем годам — с оценкой 🟢 🟡 🔴 и нормами.")

    yrs = active_years()
    if not yrs:
        st.warning("⚠️ Нет данных. Перейдите в «Ввод данных», введите данные и нажмите «Рассчитать».")
    else:
        results = {y: calc_ratios(y) for y in yrs}
        unit = st.session_state.unit
        last_y = yrs[-1]
        r = results[last_y]

        # ── Топ-метрики последнего года ──
        st.markdown(f"#### Ключевые показатели — {last_y} год")
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Выручка", fmt_money(r["revenue"]), help=f"тыс. тенге")
        with c2:
            st.metric("Чистая прибыль", fmt_money(r["net"]), help="тыс. тенге")
        with c3:
            v = r["ROE %"]
            st.metric("ROE", f"{v}%" if v else "н/д", delta="норма > 10%" if v and v >= 10 else ("⚠ ниже нормы" if v else None))
        with c4:
            v = r["Net Margin %"]
            st.metric("Net Margin", f"{v}%" if v else "н/д", delta="норма > 5%" if v and v >= 5 else ("⚠ ниже нормы" if v else None))
        with c5:
            v = r["Debt/Equity"]
            st.metric("Debt/Equity", f"{v}" if v else "н/д", delta="норма < 1.5" if v and v <= 1.5 else ("⚠ выше нормы" if v else None))

        st.markdown("---")

        # ── Определение статуса коэффициента ──
        def get_status(val, good_lo, good_hi, reverse=False):
            """reverse=True когда чем меньше — тем лучше (долги, DSO)"""
            if val is None:
                return "⚪", "#888780"
            if not reverse:
                if val >= good_lo:
                    return "🟢", "#0F6E56"
                elif val >= good_lo * 0.6:
                    return "🟡", "#854F0B"
                else:
                    return "🔴", "#A32D2D"
            else:
                if val <= good_hi:
                    return "🟢", "#0F6E56"
                elif val <= good_hi * 1.5:
                    return "🟡", "#854F0B"
                else:
                    return "🔴", "#A32D2D"

        # ── Таблица коэффициентов со светофором ──
        RATIO_DEFS = [
            # (название, ключ, норма_текст, good_lo, good_hi, reverse, суффикс)
            ("💧 ЛИКВИДНОСТЬ", None, None, None, None, False, ""),
            ("Current Ratio", "Current Ratio", "норма ≥ 1.5 — 2.0", 1.5, 3.0, False, ""),
            ("Quick Ratio", "Quick Ratio", "норма ≥ 1.0", 1.0, 3.0, False, ""),
            ("Cash Ratio", "Cash Ratio", "норма ≥ 0.2", 0.2, 2.0, False, ""),
            ("📈 ПРИБЫЛЬНОСТЬ", None, None, None, None, False, ""),
            ("Gross Margin", "Gross Margin %", "норма ≥ 20%", 20, 100, False, "%"),
            ("EBIT Margin", "EBIT Margin %", "норма ≥ 10%", 10, 100, False, "%"),
            ("EBITDA Margin", "EBITDA Margin %", "норма ≥ 15%", 15, 100, False, "%"),
            ("Net Margin", "Net Margin %", "норма ≥ 5%", 5, 100, False, "%"),
            ("ROE", "ROE %", "норма ≥ 10%", 10, 100, False, "%"),
            ("ROA", "ROA %", "норма ≥ 5%", 5, 100, False, "%"),
            ("🏦 ДОЛГОВАЯ НАГРУЗКА", None, None, None, None, False, ""),
            ("Debt/Equity", "Debt/Equity", "норма < 1.5", 0, 1.5, True, ""),
            ("Debt/Assets", "Debt/Assets", "норма < 0.5", 0, 0.5, True, ""),
            ("Equity Ratio", "Equity Ratio %", "норма ≥ 40%", 40, 100, False, "%"),
            ("Net Debt/EBITDA", "Net Debt/EBITDA", "норма < 2.5", 0, 2.5, True, "×"),
            ("Interest Coverage", "Interest Coverage", "норма ≥ 3×", 3, 100, False, "×"),
            ("⚙️ ЭФФЕКТИВНОСТЬ", None, None, None, None, False, ""),
            ("Asset Turnover", "Asset Turnover", "телеком: 0.3–0.5", 0.3, 0.6, False, ""),
            ("DSO (дней)", "DSO (дней)", "норма < 45 дней", 0, 45, True, " дн."),
            ("💵 ДЕНЕЖНЫЙ ПОТОК", None, None, None, None, False, ""),
            ("CFO/Net Income", "CFO/Net Income", "норма ≥ 0.8", 0.8, 10, False, "×"),
            ("FCF Margin", "FCF Margin %", "норма ≥ 5%", 5, 100, False, "%"),
            ("CFO/Capex", "CFO/Capex", "норма ≥ 1.5", 1.5, 10, False, "×"),
        ]

        # HTML-таблица со светофором
        header_cells = "".join([f"<th style='text-align:center;padding:8px 14px;background:#f8f7f4;font-size:12px;color:#888780'>{y}</th>" for y in yrs])
        rows_html = ""
        for item in RATIO_DEFS:
            name, key, norm, glo, ghi, rev, sfx = item
            if key is None:
                # Заголовок группы
                rows_html += f"<tr><td colspan='{len(yrs)+3}' style='background:#f0ede6;padding:8px 12px;font-size:11px;font-weight:700;color:#5F5E5A;letter-spacing:.05em'>{name}</td></tr>"
                continue
            norm_cell = f"<td style='font-size:11px;color:#888780;padding:6px 12px;white-space:nowrap'>{norm}</td>"
            val_cells = ""
            for y in yrs:
                val = results[y].get(key)
                icon, color = get_status(val, glo, ghi, rev)
                display = f"{val}{sfx}" if val is not None else "н/д"
                val_cells += f"<td style='text-align:center;padding:6px 12px;font-size:13px;color:{color};font-weight:500'>{icon} {display}</td>"
            rows_html += f"<tr style='border-bottom:1px solid #f0ede6'><td style='padding:8px 12px;font-size:13px;color:#1a1a18;white-space:nowrap'>{name}</td>{norm_cell}{val_cells}</tr>"

        html_table = f"""
        <div style='overflow-x:auto;background:#fff;border:1px solid #e0ddd6;border-radius:10px;margin-bottom:16px'>
        <table style='width:100%;border-collapse:collapse;font-family:Inter,system-ui,sans-serif'>
            <thead>
                <tr style='border-bottom:2px solid #e0ddd6'>
                    <th style='text-align:left;padding:10px 12px;background:#f8f7f4;font-size:12px;color:#888780;min-width:160px'>Коэффициент</th>
                    <th style='text-align:left;padding:10px 12px;background:#f8f7f4;font-size:12px;color:#888780;min-width:140px'>Норма</th>
                    {header_cells}
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>
        <div style='font-size:11px;color:#888780;margin-bottom:12px'>
        🟢 В норме &nbsp;&nbsp; 🟡 Требует внимания &nbsp;&nbsp; 🔴 Ниже нормы / риск &nbsp;&nbsp; ⚪ Нет данных
        </div>
        """
        st.markdown(html_table, unsafe_allow_html=True)

        # Скачать CSV
        export = {}
        for item in RATIO_DEFS:
            name, key, norm, glo, ghi, rev, sfx = item
            if key is None:
                continue
            export[name] = {y: results[y].get(key) for y in yrs}
        csv = pd.DataFrame(export).T.to_csv().encode("utf-8")
        st.download_button("⬇️ Скачать коэффициенты (CSV)", csv, "kazakhtelecom_ratios.csv", "text/csv")

# ──────────────────────────────────────────────────────────────────────
# СТРАНИЦА: СИГНАЛЫ
# ──────────────────────────────────────────────────────────────────────
elif active_page == "🚦 Сигналы":
    st.markdown("# 🚦 Сигналы и интерпретация")
    st.caption("Автоматический светофор по каждому коэффициенту — что значит, норма, и вывод.")

    yrs = active_years()
    if not yrs:
        st.warning("⚠️ Нет данных. Перейдите в «Ввод данных», введите данные и нажмите «Рассчитать».")
    else:
        last_y = yrs[-1]
        r = calc_ratios(last_y)

        st.markdown(f"#### Анализ за **{last_y}** год — {st.session_state.company_name}")

        # Полный список сигналов с подробным описанием
        SIGNALS = [
            {
                "group": "💧 Ликвидность",
                "key": "Current Ratio",
                "name": "Current Ratio (Коэффициент текущей ликвидности)",
                "formula": "Оборотные активы ÷ Краткосрочные обязательства",
                "norm": "Норма: ≥ 1.5 — хорошо | 1.0–1.5 — допустимо | < 1.0 — риск",
                "good_lo": 1.5, "good_hi": 999, "reverse": False, "suffix": "",
                "good_msg": "Компания способна покрыть краткосрочные обязательства. Хорошая платёжеспособность.",
                "warn_msg": "Ликвидность на допустимом уровне, но запас прочности небольшой. Требует мониторинга.",
                "bad_msg":  "Низкая ликвидность. Оборотных активов может не хватить для погашения долгов — риск дефолта.",
            },
            {
                "group": "💧 Ликвидность",
                "key": "Quick Ratio",
                "name": "Quick Ratio (Быстрая ликвидность)",
                "formula": "(Оборотные активы − Запасы) ÷ Краткосрочные обязательства",
                "norm": "Норма: ≥ 1.0 — хорошо | 0.7–1.0 — допустимо | < 0.7 — риск",
                "good_lo": 1.0, "good_hi": 999, "reverse": False, "suffix": "",
                "good_msg": "Компания может быстро покрыть обязательства без продажи запасов.",
                "warn_msg": "Умеренный уровень быстрой ликвидности. Зависит от скорости сбора дебиторки.",
                "bad_msg":  "Недостаточно ликвидных активов без учёта запасов — повышенный риск.",
            },
            {
                "group": "📈 Прибыльность",
                "key": "ROE %",
                "name": "ROE (Рентабельность собственного капитала)",
                "formula": "Чистая прибыль ÷ Собственный капитал × 100%",
                "norm": "Норма: ≥ 15% — отлично | 10–15% — хорошо | 5–10% — допустимо | < 5% — низко",
                "good_lo": 10, "good_hi": 999, "reverse": False, "suffix": "%",
                "good_msg": "Хорошая отдача на вложенный акционерами капитал.",
                "warn_msg": "Умеренная рентабельность капитала. Может быть приемлемо для телекоммуникационной отрасли с высоким Capex.",
                "bad_msg":  "Низкая рентабельность капитала. Компания генерирует мало прибыли на вложенный капитал.",
            },
            {
                "group": "📈 Прибыльность",
                "key": "ROA %",
                "name": "ROA (Рентабельность активов)",
                "formula": "Чистая прибыль ÷ Итого активы × 100%",
                "norm": "Норма: ≥ 5% — хорошо | 3–5% — допустимо | < 3% — низко",
                "good_lo": 5, "good_hi": 999, "reverse": False, "suffix": "%",
                "good_msg": "Активы компании эффективно генерируют прибыль.",
                "warn_msg": "Умеренная отдача от активов. Для капиталоёмкого телекома (много ОС) — это нормально.",
                "bad_msg":  "Низкая рентабельность активов. Возможна избыточная нагрузка активов без соответствующей прибыли.",
            },
            {
                "group": "📈 Прибыльность",
                "key": "Net Margin %",
                "name": "Net Margin (Чистая маржа)",
                "formula": "Чистая прибыль ÷ Выручка × 100%",
                "norm": "Норма: ≥ 10% — хорошо | 5–10% — допустимо | < 5% — низко",
                "good_lo": 10, "good_hi": 999, "reverse": False, "suffix": "%",
                "good_msg": "Хорошая чистая маржинальность — компания эффективно контролирует расходы.",
                "warn_msg": "Умеренная маржа. Чувствительна к росту операционных затрат.",
                "bad_msg":  "Очень низкая маржа. Небольшой рост расходов может привести к убытку.",
            },
            {
                "group": "📈 Прибыльность",
                "key": "EBITDA Margin %",
                "name": "EBITDA Margin",
                "formula": "EBITDA ÷ Выручка × 100%",
                "norm": "Норма для телекома: ≥ 35% — хорошо | 25–35% — допустимо | < 25% — низко",
                "good_lo": 35, "good_hi": 999, "reverse": False, "suffix": "%",
                "good_msg": "Высокая EBITDA маржа — компания генерирует хороший операционный кэш.",
                "warn_msg": "Умеренная EBITDA маржа. Требует контроля затрат.",
                "bad_msg":  "Низкая EBITDA маржа для телекома. Высокие операционные затраты снижают доходность.",
            },
            {
                "group": "🏦 Долговая нагрузка",
                "key": "Debt/Equity",
                "name": "Debt/Equity (Долг к капиталу)",
                "formula": "Итого обязательства ÷ Собственный капитал",
                "norm": "Норма: < 1.0 — хорошо | 1.0–1.5 — допустимо | > 2.0 — высокий риск",
                "good_lo": 0, "good_hi": 1.0, "reverse": True, "suffix": "×",
                "good_msg": "Умеренный долг. Компания финансово устойчива.",
                "warn_msg": "Повышенная долговая нагрузка. Допустимо при стабильном денежном потоке.",
                "bad_msg":  "Высокая долговая нагрузка — риск финансовой неустойчивости при росте ставок.",
            },
            {
                "group": "🏦 Долговая нагрузка",
                "key": "Net Debt/EBITDA",
                "name": "Net Debt / EBITDA",
                "formula": "Чистый долг ÷ EBITDA",
                "norm": "Норма: < 2.0 — хорошо | 2.0–3.5 — допустимо | > 3.5 — риск",
                "good_lo": 0, "good_hi": 2.0, "reverse": True, "suffix": "×",
                "good_msg": "Комфортное соотношение долга к EBITDA. Компания может быстро погасить долг.",
                "warn_msg": "Умеренно высокая нагрузка. Стандарт для телекома с большим Capex.",
                "bad_msg":  "Высокая долговая нагрузка по EBITDA — риск рефинансирования.",
            },
            {
                "group": "🏦 Долговая нагрузка",
                "key": "Interest Coverage",
                "name": "Interest Coverage (Покрытие процентов)",
                "formula": "EBIT ÷ Финансовые расходы",
                "norm": "Норма: ≥ 3× — хорошо | 1.5–3× — допустимо | < 1.5× — риск",
                "good_lo": 3, "good_hi": 999, "reverse": False, "suffix": "×",
                "good_msg": "Прибыль уверенно покрывает процентные расходы.",
                "warn_msg": "Умеренное покрытие процентов. Небольшой запас прочности.",
                "bad_msg":  "Низкое покрытие процентов — риск дефолта при снижении операционной прибыли.",
            },
            {
                "group": "⚙️ Эффективность",
                "key": "Asset Turnover",
                "name": "Asset Turnover (Оборачиваемость активов)",
                "formula": "Выручка ÷ Итого активы",
                "norm": "Норма для телекома: 0.3–0.5 — норма | < 0.3 — низко | > 0.7 — высоко",
                "good_lo": 0.3, "good_hi": 0.7, "reverse": False, "suffix": "×",
                "good_msg": "Нормальная оборачиваемость активов для телекоммуникационной отрасли.",
                "warn_msg": "Умеренная оборачиваемость. Телеком — капиталоёмкая отрасль, низкий показатель — норма.",
                "bad_msg":  "Низкая оборачиваемость активов. Активы растут быстрее выручки.",
            },
            {
                "group": "💵 Денежный поток",
                "key": "CFO/Net Income",
                "name": "CFO / Net Income (Качество прибыли)",
                "formula": "Операционный денежный поток ÷ Чистая прибыль",
                "norm": "Норма: ≥ 1.0 — отлично | 0.8–1.0 — хорошо | < 0.8 — требует проверки",
                "good_lo": 0.8, "good_hi": 999, "reverse": False, "suffix": "×",
                "good_msg": "Прибыль подтверждена денежным потоком. Высокое качество прибыли.",
                "warn_msg": "CFO немного ниже прибыли. Возможно влияние изменений оборотного капитала.",
                "bad_msg":  "Прибыль слабо подтверждена денежным потоком. Требует анализа качества прибыли.",
            },
        ]

        # Счётчик по цветам
        total_green = sum(1 for s in SIGNALS if r.get(s["key"]) is not None and
                         (r[s["key"]] >= s["good_lo"] if not s["reverse"] else r[s["key"]] <= s["good_hi"]))
        total_filled = sum(1 for s in SIGNALS if r.get(s["key"]) is not None)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            green = sum(1 for s in SIGNALS if r.get(s["key"]) is not None and
                       (r[s["key"]] >= s["good_lo"] if not s["reverse"] else r[s["key"]] <= s["good_hi"]))
            st.markdown(f"<div style='background:#E1F5EE;border-radius:8px;padding:12px;text-align:center'><div style='font-size:28px'>🟢</div><div style='font-size:22px;font-weight:600;color:#0F6E56'>{green}</div><div style='font-size:12px;color:#5F5E5A'>В норме</div></div>", unsafe_allow_html=True)
        with col_b:
            yellow = sum(1 for s in SIGNALS if r.get(s["key"]) is not None and
                        not (r[s["key"]] >= s["good_lo"] if not s["reverse"] else r[s["key"]] <= s["good_hi"]) and
                        (r[s["key"]] >= s["good_lo"] * 0.6 if not s["reverse"] else r[s["key"]] <= s["good_hi"] * 1.5))
            st.markdown(f"<div style='background:#FAEEDA;border-radius:8px;padding:12px;text-align:center'><div style='font-size:28px'>🟡</div><div style='font-size:22px;font-weight:600;color:#854F0B'>{yellow}</div><div style='font-size:12px;color:#5F5E5A'>Внимание</div></div>", unsafe_allow_html=True)
        with col_c:
            red = total_filled - green - yellow
            st.markdown(f"<div style='background:#FCEBEB;border-radius:8px;padding:12px;text-align:center'><div style='font-size:28px'>🔴</div><div style='font-size:22px;font-weight:600;color:#A32D2D'>{red}</div><div style='font-size:12px;color:#5F5E5A'>Риск / ниже нормы</div></div>", unsafe_allow_html=True)

        st.markdown("")

        # Карточки сигналов
        prev_group = ""
        for s in SIGNALS:
            val = r.get(s["key"])
            if val is None:
                continue

            if s["group"] != prev_group:
                st.markdown(f"**{s['group']}**")
                prev_group = s["group"]

            # Определяем цвет
            if not s["reverse"]:
                is_good = val >= s["good_lo"]
                is_warn = val >= s["good_lo"] * 0.6
            else:
                is_good = val <= s["good_hi"]
                is_warn = val <= s["good_hi"] * 1.5

            if is_good:
                icon, bg, color, msg = "🟢", "#E1F5EE", "#0F6E56", s["good_msg"]
            elif is_warn:
                icon, bg, color, msg = "🟡", "#FAEEDA", "#854F0B", s["warn_msg"]
            else:
                icon, bg, color, msg = "🔴", "#FCEBEB", "#A32D2D", s["bad_msg"]

            display_val = f"{val}{s['suffix']}"

            st.markdown(f"""
            <div style="background:{bg};border-radius:10px;padding:14px 18px;margin-bottom:10px;border-left:4px solid {color}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
                    <div style="font-size:13.5px;font-weight:600;color:{color}">{icon} {s['name']}</div>
                    <div style="font-size:20px;font-weight:700;color:{color};margin-left:12px">{display_val}</div>
                </div>
                <div style="font-size:11.5px;color:#888780;margin-bottom:5px">📐 Формула: {s['formula']}</div>
                <div style="font-size:11.5px;color:#888780;margin-bottom:6px">📏 {s['norm']}</div>
                <div style="font-size:13px;color:#3a3a38;line-height:1.5">💬 {msg}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        st.warning("⚠️ Интерпретация автоматическая — на основе общепринятых финансовых норм. "
                   "Нормы варьируются по отраслям и рыночным условиям. "
                   "Используйте как аналитическую отправную точку, а не окончательный вывод.")

st.sidebar.markdown("---")
st.sidebar.caption("Индивидуальный проект · Финансовый анализ · АФО 2026")
