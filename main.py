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
    st.markdown("# Сводный дашборд")
    st.caption("Все ключевые коэффициенты по всем годам в одной таблице.")

    yrs = active_years()
    if not yrs:
        st.warning("Нет данных. Перейдите в «Ввод данных» и нажмите «Рассчитать».")
    else:
        results = {y: calc_ratios(y) for y in yrs}
        unit = st.session_state.unit

        last_y = yrs[-1]
        r = results[last_y]
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Выручка", fmt_money(r['revenue']), help=unit)
        with c2:
            st.metric("ROE", f"{fmt(r['ROE %'], '%')}")
        with c3:
            st.metric("Net Margin", f"{fmt(r['Net Margin %'], '%')}")
        with c4:
            st.metric("Debt/Equity", f"{fmt(r['Debt/Equity'])}")

        with st.container(border=True):
            st.markdown(f"### 🎯 Все коэффициенты — {st.session_state.company_name} (суммы в {unit})")
            rows = [
                ("Выручка", "revenue", True), ("Чистая прибыль", "net", True),
                ("EBITDA", "ebitda", True), ("Итого активы", "totalassets", True),
                ("Собственный капитал", "equity", True),
                ("Current Ratio", "Current Ratio", False), ("Quick Ratio", "Quick Ratio", False),
                ("ROE %", "ROE %", False), ("ROA %", "ROA %", False),
                ("Net Margin %", "Net Margin %", False), ("EBITDA Margin %", "EBITDA Margin %", False),
                ("Debt/Equity", "Debt/Equity", False), ("Debt/Assets", "Debt/Assets", False),
                ("Net Debt/EBITDA", "Net Debt/EBITDA", False), ("Interest Coverage", "Interest Coverage", False),
                ("Asset Turnover", "Asset Turnover", False), ("DSO (дней)", "DSO (дней)", False),
                ("CFO/Net Income", "CFO/Net Income", False), ("FCF", "FCF", True),
                ("FCF Margin %", "FCF Margin %", False),
            ]
            table = {}
            for name, key, is_money in rows:
                table[name] = {
                    y: (fmt_money(results[y][key]) if is_money else results[y][key])
                       if results[y].get(key) is not None else "н/д"
                    for y in yrs
                }
            st.dataframe(pd.DataFrame(table).T, use_container_width=True)

            csv = pd.DataFrame(table).T.to_csv().encode("utf-8")
            st.download_button("⬇️ Скачать коэффициенты (CSV)", csv, "ratios.csv", "text/csv")

# ──────────────────────────────────────────────────────────────────────
# СТРАНИЦА: СИГНАЛЫ
# ──────────────────────────────────────────────────────────────────────
elif active_page == "🚦 Сигналы":
    st.markdown("# Сигналы и интерпретация")
    st.caption("Автоматическая интерпретация коэффициентов на основе общепринятых норм.")

    yrs = active_years()
    if not yrs:
        st.warning("Нет данных. Перейдите в «Ввод данных» и нажмите «Рассчитать».")
    else:
        last_y = yrs[-1]
        r = calc_ratios(last_y)

        signals = []

        def add(val, lo, hi, name, good_txt, warn_txt, bad_txt, suffix=""):
            if val is None:
                return
            if lo <= val <= hi:
                signals.append(("good", f"{name}: {val}{suffix}", good_txt))
            elif val < lo * 0.6 or val > hi * 1.8:
                signals.append(("bad", f"{name}: {val}{suffix}", bad_txt))
            else:
                signals.append(("warn", f"{name}: {val}{suffix}", warn_txt))

        add(r["Current Ratio"], 1.5, 3, "Current Ratio",
            "Хорошая краткосрочная ликвидность.",
            "Умеренная ликвидность, требует мониторинга.",
            "Низкая ликвидность — риск покрытия обязательств.")
        add(r["ROE %"], 10, 30, "ROE", "Высокая рентабельность капитала.",
            "Умеренная рентабельность капитала.",
            "Низкая рентабельность капитала.", "%")
        add(r["ROA %"], 5, 15, "ROA", "Эффективное использование активов.",
            "Умеренная отдача от активов.",
            "Низкая рентабельность активов.", "%")
        add(r["Net Margin %"], 5, 30, "Net Margin", "Хорошая чистая маржинальность.",
            "Умеренная маржа, чувствительна к расходам.",
            "Очень низкая маржа — риск убытка.", "%")
        add(r["Debt/Equity"], 0, 1, "Debt/Equity", "Умеренный долг к капиталу.",
            "Повышенная долговая нагрузка.",
            "Высокая долговая нагрузка — риск устойчивости.")
        if r.get("CFO/Net Income") is not None:
            if r["CFO/Net Income"] >= 0.8:
                signals.append(("good", f"CFO/Net Income: {r['CFO/Net Income']}×",
                                 "Прибыль подтверждена денежным потоком."))
            else:
                signals.append(("warn", f"CFO/Net Income: {r['CFO/Net Income']}×",
                                 "CFO отличается от прибыли — проверить качество прибыли."))

        with st.container(border=True):
            st.markdown(f"### 🚦 Сигналы по данным {last_y} — {st.session_state.company_name}")
            icons = {"good": "✅", "warn": "⚠️", "bad": "❌"}
            cols = st.columns(2)
            for i, (typ, title, desc) in enumerate(signals):
                with cols[i % 2]:
                    bg = {"good": "#E1F5EE", "warn": "#FAEEDA", "bad": "#FCEBEB"}[typ]
                    color = {"good": "#0F6E56", "warn": "#854F0B", "bad": "#A32D2D"}[typ]
                    st.markdown(f"""
                    <div style="background:{bg};border-radius:8px;padding:12px 14px;margin-bottom:10px;">
                        <div style="font-size:13px;font-weight:600;color:{color};margin-bottom:3px">{icons[typ]} {title}</div>
                        <div style="font-size:12px;color:#5F5E5A;line-height:1.4">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.warning(
            "⚠️ Сигналы — автоматическая интерпретация на основе общепринятых норм. "
            "Нормы варьируются по отраслям. Используйте как отправную точку, а не окончательный вывод."
        )

st.sidebar.markdown("---")
st.sidebar.caption("Индивидуальный проект · Финансовый анализ · АФО 2026")
