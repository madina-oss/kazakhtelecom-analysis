"""
Финансовый анализ — Калькулятор коэффициентов
Веб-приложение для анализа финансовой отчётности (методология АФО)
Отчётность → Качество → Анализ → Прогноз → Вывод
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit.components.v1 as components

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

    /* ─── БРЕНД-БАННЕР САЙДБАРА (декор «финансовый анализ») ─── */
    .brand-banner {
        position: relative;
        background: linear-gradient(145deg, #123b63 0%, #185FA5 55%, #2f86d6 100%);
        border-radius: 16px;
        padding: 22px 18px 18px 18px;
        margin: 2px 0 18px 0;
        overflow: hidden;
        box-shadow: 0 6px 18px rgba(24, 95, 165, 0.28);
    }
    .brand-banner::before {
        content: "";
        position: absolute;
        top: -30px; right: -30px;
        width: 120px; height: 120px;
        background: radial-gradient(circle, rgba(255,255,255,0.16) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
    }
    .brand-banner .brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
        position: relative;
        z-index: 2;
    }
    .brand-banner .brand-icon {
        width: 46px; height: 46px;
        flex-shrink: 0;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.35);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
    }
    .brand-banner .brand-title {
        font-size: 17px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.01em;
        line-height: 1.15;
    }
    .brand-banner .brand-subtitle {
        font-size: 10.5px;
        font-weight: 500;
        color: rgba(255,255,255,0.78);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 2px;
    }
    .brand-banner .brand-chart {
        position: relative;
        z-index: 2;
        margin-top: 14px;
    }
    .brand-banner .brand-tags {
        position: relative;
        z-index: 2;
        display: flex;
        gap: 6px;
        margin-top: 12px;
        flex-wrap: wrap;
    }
    .brand-banner .brand-tag {
        font-size: 9.5px;
        font-weight: 600;
        color: #ffffff;
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.3);
        padding: 3px 9px;
        border-radius: 20px;
        letter-spacing: 0.02em;
    }

    /* ─── МИНИ-КАЛЬКУЛЯТОР В САЙДБАРЕ ─── */
    .calc-wrap {
        font-family: 'Inter', sans-serif;
    }
    .calc-display {
        background: #1a1a18;
        color: #ffffff;
        border-radius: 8px;
        padding: 10px 12px;
        text-align: right;
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 6px;
        min-height: 28px;
        overflow-x: auto;
        white-space: nowrap;
        letter-spacing: 0.02em;
    }
    .calc-sub {
        color: #9a9a95;
        font-size: 10.5px;
        text-align: right;
        min-height: 14px;
        margin-bottom: 2px;
    }
    .calc-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 5px;
    }
    .calc-btn {
        border: 1px solid #e0ddd6;
        background: #ffffff;
        color: #3a3a36;
        border-radius: 7px;
        padding: 7px 0;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.12s;
        user-select: none;
    }
    .calc-btn:hover { background: #f3f1ec; }
    .calc-btn:active { transform: scale(0.94); }
    .calc-btn.op { background: #185FA5; color: #fff; border: none; }
    .calc-btn.op:hover { background: #0c447c; }
    .calc-btn.eq { background: #2fa35c; color: #fff; border: none; }
    .calc-btn.eq:hover { background: #23803f; }
    .calc-btn.clear { background: #fff; color: #b3453a; border: 1px solid #e0ddd6; }
    .calc-btn.wide { grid-column: span 2; }
</style>
""", unsafe_allow_html=True)

DEFAULT_YEARS = [2020, 2021, 2022, 2023, 2024]

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
if "years" not in st.session_state:
    st.session_state.years = list(DEFAULT_YEARS)
if "data" not in st.session_state:
    st.session_state.data = {y: {} for y in st.session_state.years}
if "company_name" not in st.session_state:
    st.session_state.company_name = "Казахтелеком"
if "unit" not in st.session_state:
    st.session_state.unit = "тыс. тенге"
if "current_year" not in st.session_state:
    st.session_state.current_year = st.session_state.years[0]
if "calculated" not in st.session_state:
    st.session_state.calculated = False


def add_year(y):
    """Добавляет новый год в список годов, сохраняя данные всех остальных лет."""
    if y not in st.session_state.years:
        st.session_state.years.append(y)
        st.session_state.years.sort()
    if y not in st.session_state.data:
        st.session_state.data[y] = {}
    st.session_state.current_year = y


def remove_year(y):
    """Удаляет год и его данные, не затрагивая остальные годы."""
    if y in st.session_state.years:
        st.session_state.years.remove(y)
    if y in st.session_state.data:
        del st.session_state.data[y]
    if st.session_state.current_year == y:
        st.session_state.current_year = st.session_state.years[0] if st.session_state.years else None


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
    return [y for y in sorted(st.session_state.years)
            if any(v is not None for v in st.session_state.data.get(y, {}).values())]


# ──────────────────────────────────────────────────────────────────────
# SIDEBAR — навигация
# ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-banner">
        <div class="brand-row">
            <div class="brand-icon">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 21h18" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round"/>
                    <rect x="5" y="13" width="3.2" height="6" rx="0.8" fill="#ffffff" fill-opacity="0.9"/>
                    <rect x="10.4" y="8.5" width="3.2" height="10.5" rx="0.8" fill="#ffffff"/>
                    <rect x="15.8" y="4" width="3.2" height="15" rx="0.8" fill="#ffffff" fill-opacity="0.95"/>
                    <path d="M4.5 10.5L9 6.5L13 9.5L19 3.5" stroke="#7CD6A3" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M15.3 3.5H19V7.2" stroke="#7CD6A3" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div>
                <div class="brand-title">ФинАнализ</div>
                <div class="brand-subtitle">Калькулятор коэффициентов</div>
            </div>
        </div>
        <div class="brand-tags">
            <span class="brand-tag">📄 Отчётность</span>
            <span class="brand-tag">📊 Анализ</span>
            <span class="brand-tag">🎯 Прогноз</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-label">ДАННЫЕ</div>', unsafe_allow_html=True)
    page = st.radio(
        "nav1", ["✏️ Ввод данных"],
        label_visibility="collapsed", key="nav_input"
    )

    st.markdown('<div class="nav-label">АНАЛИЗ</div>', unsafe_allow_html=True)
    page2 = st.radio(
        "nav2",
        ["— нет —", "💧 Ликвидность", "📈 Прибыльность", "🏦 Долговая нагрузка",
         "⚙️ Эффективность", "💵 Денежный поток", "📉 Прогноз", "📝 Вывод"],
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

    st.markdown("---")
    with st.expander("🧮 Калькулятор", expanded=False):
        components.html("""
        <style>
            .calc-wrap { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
            .calc-display {
                background: #1a1a18; color: #ffffff; border-radius: 8px;
                padding: 10px 12px; text-align: right; font-size: 20px; font-weight: 600;
                margin-bottom: 6px; min-height: 28px; overflow-x: auto; white-space: nowrap;
                letter-spacing: 0.02em;
            }
            .calc-sub { color: #9a9a95; font-size: 10.5px; text-align: right; min-height: 14px; margin-bottom: 2px; }
            .calc-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; }
            .calc-btn {
                border: 1px solid #e0ddd6; background: #ffffff; color: #3a3a36;
                border-radius: 7px; padding: 7px 0; font-size: 13px; font-weight: 500;
                cursor: pointer; transition: all 0.12s; user-select: none;
            }
            .calc-btn:hover { background: #f3f1ec; }
            .calc-btn:active { transform: scale(0.94); }
            .calc-btn.op { background: #185FA5; color: #fff; border: none; }
            .calc-btn.op:hover { background: #0c447c; }
            .calc-btn.eq { background: #2fa35c; color: #fff; border: none; }
            .calc-btn.eq:hover { background: #23803f; }
            .calc-btn.clear { background: #fff; color: #b3453a; border: 1px solid #e0ddd6; }
            .calc-btn.wide { grid-column: span 2; }
            body { margin: 0; padding: 2px; background: transparent; }
        </style>
        <div class="calc-wrap">
            <div class="calc-sub" id="calcSub">&nbsp;</div>
            <div class="calc-display" id="calcDisplay">0</div>
            <div class="calc-grid">
                <button class="calc-btn clear" onclick="calcClear()">C</button>
                <button class="calc-btn clear" onclick="calcBackspace()">⌫</button>
                <button class="calc-btn op" onclick="calcOp('%')">%</button>
                <button class="calc-btn op" onclick="calcOp('/')">÷</button>

                <button class="calc-btn" onclick="calcNum('7')">7</button>
                <button class="calc-btn" onclick="calcNum('8')">8</button>
                <button class="calc-btn" onclick="calcNum('9')">9</button>
                <button class="calc-btn op" onclick="calcOp('*')">×</button>

                <button class="calc-btn" onclick="calcNum('4')">4</button>
                <button class="calc-btn" onclick="calcNum('5')">5</button>
                <button class="calc-btn" onclick="calcNum('6')">6</button>
                <button class="calc-btn op" onclick="calcOp('-')">−</button>

                <button class="calc-btn" onclick="calcNum('1')">1</button>
                <button class="calc-btn" onclick="calcNum('2')">2</button>
                <button class="calc-btn" onclick="calcNum('3')">3</button>
                <button class="calc-btn op" onclick="calcOp('+')">+</button>

                <button class="calc-btn wide" onclick="calcNum('0')">0</button>
                <button class="calc-btn" onclick="calcNum('.')">.</button>
                <button class="calc-btn eq" onclick="calcEquals()">=</button>
            </div>
        </div>
        <script>
            let current = "0";
            let previous = null;
            let operator = null;
            let justEvaluated = false;

            function fmt(n) {
                if (n === "" || n === "-" ) return "0";
                let num = parseFloat(n);
                if (!isFinite(num)) return "Ошибка";
                let s = num.toString();
                if (s.length > 14) s = num.toPrecision(10).toString();
                return s;
            }

            function render() {
                document.getElementById("calcDisplay").innerText = fmt(current);
                let sub = "";
                if (previous !== null && operator) {
                    let opSym = {"+":"+","-":"−","*":"×","/":"÷","%":"%"}[operator];
                    sub = fmt(previous) + " " + opSym;
                }
                document.getElementById("calcSub").innerText = sub || "\\u00a0";
            }

            function calcNum(d) {
                if (justEvaluated) { current = "0"; justEvaluated = false; }
                if (d === "." && current.includes(".")) return;
                if (current === "0" && d !== ".") current = d;
                else current += d;
                render();
            }

            function calcOp(op) {
                if (operator && previous !== null && !justEvaluated) {
                    calcEquals();
                }
                previous = current;
                operator = op;
                current = "0";
                justEvaluated = false;
                render();
            }

            function calcEquals() {
                if (operator === null || previous === null) return;
                let a = parseFloat(previous);
                let b = parseFloat(current);
                let r = 0;
                if (operator === "+") r = a + b;
                else if (operator === "-") r = a - b;
                else if (operator === "*") r = a * b;
                else if (operator === "/") r = b === 0 ? NaN : a / b;
                else if (operator === "%") r = a * (b / 100);
                current = isFinite(r) ? r.toString() : "Ошибка";
                operator = null;
                previous = null;
                justEvaluated = true;
                render();
            }

            function calcClear() {
                current = "0"; previous = null; operator = null; justEvaluated = false;
                render();
            }

            function calcBackspace() {
                if (justEvaluated) { calcClear(); return; }
                current = current.length > 1 ? current.slice(0, -1) : "0";
                render();
            }

            render();
        </script>
        """, height=230, scrolling=False)

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
        st.caption("Данные каждого года сохраняются отдельно — можно добавить новый год или удалить ненужный, не теряя остальные.")

        yrs_sorted = sorted(st.session_state.years)
        if yrs_sorted:
            cols = st.columns(len(yrs_sorted))
            for i, y in enumerate(yrs_sorted):
                with cols[i]:
                    btn_type = "primary" if y == st.session_state.current_year else "secondary"
                    if st.button(str(y), key=f"yr_{y}", type=btn_type, use_container_width=True):
                        st.session_state.current_year = y
                        st.rerun()
        else:
            st.info("Нет добавленных годов. Добавьте год ниже.")

        acol1, acol2, acol3 = st.columns([1.3, 1, 1.3])
        with acol1:
            new_year = st.number_input(
                "Добавить год", min_value=1990, max_value=2100,
                value=(max(yrs_sorted) + 1) if yrs_sorted else 2024,
                step=1, key="new_year_input", label_visibility="collapsed",
            )
        with acol2:
            if st.button("➕ Добавить год", use_container_width=True):
                add_year(int(new_year))
                st.rerun()
        with acol3:
            if st.session_state.current_year is not None and st.button(
                f"🗑️ Удалить год {st.session_state.current_year}", use_container_width=True
            ):
                remove_year(st.session_state.current_year)
                st.rerun()

    if st.session_state.current_year is None:
        st.warning("Добавьте хотя бы один год, чтобы начать ввод данных.")
    else:
      with st.container(border=True):
        year = st.session_state.current_year
        st.markdown(f"### ДАННЫЕ ЗА {year} ГОД")
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
        if st.button("🗑️ Очистить все данные", use_container_width=True):
            st.session_state.data = {y: {} for y in st.session_state.years}
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

        def get_signals(year):
            r = calc_ratios(year)
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
            return signals

        icons = {"good": "✅", "warn": "⚠️", "bad": "❌"}

        if len(yrs) == 1:
            tabs = [None]
        else:
            tabs = st.tabs([str(y) for y in yrs])

        for i, y in enumerate(yrs):
            ctx = tabs[i] if tabs[0] is not None else st.container()
            with ctx:
                signals = get_signals(y)
                with st.container(border=True):
                    st.markdown(f"### 🚦 Сигналы по данным {y} — {st.session_state.company_name}")
                    n_good = sum(1 for s in signals if s[0] == "good")
                    n_warn = sum(1 for s in signals if s[0] == "warn")
                    n_bad = sum(1 for s in signals if s[0] == "bad")
                    st.caption(f"✅ Хорошо: {n_good}   ⚠️ Внимание: {n_warn}   ❌ Риск: {n_bad}")
                    cols = st.columns(2)
                    for j, (typ, title, desc) in enumerate(signals):
                        with cols[j % 2]:
                            bg = {"good": "#E1F5EE", "warn": "#FAEEDA", "bad": "#FCEBEB"}[typ]
                            color = {"good": "#0F6E56", "warn": "#854F0B", "bad": "#A32D2D"}[typ]
                            st.markdown(f"""
                            <div style="background:{bg};border-radius:8px;padding:12px 14px;margin-bottom:10px;">
                                <div style="font-size:13px;font-weight:600;color:{color};margin-bottom:3px">{icons[typ]} {title}</div>
                                <div style="font-size:12px;color:#5F5E5A;line-height:1.4">{desc}</div>
                            </div>
                            """, unsafe_allow_html=True)

        if len(yrs) > 1:
            with st.container(border=True):
                st.markdown(f"### 📊 Сравнение сигналов по годам — {st.session_state.company_name}")
                comp = {}
                for y in yrs:
                    signals = get_signals(y)
                    by_name = {title.split(":")[0]: icons[typ] for typ, title, _ in signals}
                    comp[y] = by_name
                all_names = []
                for y in yrs:
                    for name in comp[y]:
                        if name not in all_names:
                            all_names.append(name)
                comp_df = pd.DataFrame({y: {name: comp[y].get(name, "—") for name in all_names} for y in yrs})
                st.dataframe(comp_df, use_container_width=True)

        st.warning(
            "⚠️ Сигналы — автоматическая интерпретация на основе общепринятых норм. "
            "Нормы варьируются по отраслям. Используйте как отправную точку, а не окончательный вывод."
        )



# ──────────────────────────────────────────────────────────────────────
# СТРАНИЦА: ПРОГНОЗ
# ──────────────────────────────────────────────────────────────────────
elif active_page == "📉 Прогноз":
    st.markdown("# 📉 Прогноз на 3 года")
    st.caption(
        "Base case и Stress case — два сценария развития. "
        "**Не является инвестиционной рекомендацией** — показывает возможные исходы при заданных допущениях."
    )

    yrs = active_years()
    if len(yrs) < 2:
        st.warning("Введите данные минимум за 2 года в «Вводе данных» для расчёта исторического тренда.")
    else:
        last_year = yrs[-1]
        last_rev = st.session_state.data[last_year].get("revenue")
        last_eq = st.session_state.data[last_year].get("equity")
        last_ta = st.session_state.data[last_year].get("totalassets")

        if last_rev is None:
            st.error("Введите выручку за последний год в разделе «Ввод данных».")
        else:
            r_last = calc_ratios(last_year)
            sorted_yrs = sorted(yrs)

            # Исторический рост выручки
            rev_growths = []
            for i in range(1, len(sorted_yrs)):
                pv = st.session_state.data[sorted_yrs[i-1]].get("revenue")
                cv = st.session_state.data[sorted_yrs[i]].get("revenue")
                if pv and cv and pv != 0:
                    rev_growths.append((cv - pv) / pv * 100)
            hist_growth = round(sum(rev_growths) / len(rev_growths), 1) if rev_growths else 5.0

            last_net_margin = r_last.get("Net Margin %") or 10.0
            last_roe = r_last.get("ROE %") or 10.0
            last_de = r_last.get("Debt/Equity") or 1.0

            st.markdown(f"#### Исторические данные (база для прогноза)")
            mc1, mc2, mc3, mc4 = st.columns(4)
            with mc1:
                st.metric("Ср. рост выручки", f"{hist_growth}%", help="Среднее за введённые годы")
            with mc2:
                st.metric("Net Margin посл. год", f"{last_net_margin}%")
            with mc3:
                st.metric("ROE посл. год", f"{last_roe}%")
            with mc4:
                st.metric("Debt/Equity посл. год", f"{last_de}")

            st.markdown("---")
            st.markdown("#### Допущения — настройте сценарии")

            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    st.markdown("**🟢 Base Case — умеренный сценарий**")
                    base_rev_g = st.slider("Рост выручки (%)", -10.0, 30.0, max(round(hist_growth * 0.7, 1), 2.0), 0.5, key="b_rev")
                    base_margin = st.slider("Net Margin (%)", 0.0, 40.0, float(last_net_margin), 0.5, key="b_margin")
                    base_debt_g = st.slider("Рост долга (%)", -10.0, 20.0, 5.0, 0.5, key="b_debt")
                    st.caption(f"Допущение: выручка +{base_rev_g}%, маржа {base_margin}%, долг +{base_debt_g}%")

            with col2:
                with st.container(border=True):
                    st.markdown("**🔴 Stress Case — стресс-сценарий**")
                    stress_rev_g = st.slider("Рост выручки (%)", -20.0, 15.0, max(round(hist_growth * 0.2, 1), -2.0), 0.5, key="s_rev")
                    stress_margin = st.slider("Net Margin (%)", 0.0, 30.0, max(float(last_net_margin) - 5.0, 2.0), 0.5, key="s_margin")
                    stress_debt_g = st.slider("Рост долга (%)", -5.0, 30.0, 12.0, 0.5, key="s_debt")
                    st.caption(f"Допущение: выручка {stress_rev_g}%, маржа {stress_margin}%, долг +{stress_debt_g}%")

            fwd_years = [last_year + 1, last_year + 2, last_year + 3]
            base_rev_f, stress_rev_f = [last_rev], [last_rev]
            for _ in range(3):
                base_rev_f.append(base_rev_f[-1] * (1 + base_rev_g / 100))
                stress_rev_f.append(stress_rev_f[-1] * (1 + stress_rev_g / 100))
            base_rev_f, stress_rev_f = base_rev_f[1:], stress_rev_f[1:]
            base_net_f = [r * base_margin / 100 for r in base_rev_f]
            stress_net_f = [r * stress_margin / 100 for r in stress_rev_f]
            base_roe_f = [round(n / (last_eq or 1) * 100, 1) if last_eq else None for n in base_net_f]
            stress_roe_f = [round(n / (last_eq or 1) * 100, 1) if last_eq else None for n in stress_net_f]

            last_debt = st.session_state.data[last_year].get("totalliab")
            base_debt_f, stress_debt_f = [], []
            if last_debt:
                bd, sd = last_debt, last_debt
                for _ in range(3):
                    bd = bd * (1 + base_debt_g / 100)
                    sd = sd * (1 + stress_debt_g / 100)
                    base_debt_f.append(bd)
                    stress_debt_f.append(sd)

            st.markdown("---")
            st.markdown("#### Таблица прогноза")
            col_a, col_b = st.columns(2)
            with col_a:
                with st.container(border=True):
                    st.markdown("**🟢 Base Case**")
                    df_base = pd.DataFrame({
                        "Год": fwd_years,
                        "Выручка (тыс. ₸)": [fmt_money(v) for v in base_rev_f],
                        "Чист. прибыль": [fmt_money(v) for v in base_net_f],
                        "Net Margin": [f"{base_margin}%"] * 3,
                        "ROE (оценка)": [f"{v}%" if v else "н/д" for v in base_roe_f],
                    })
                    st.dataframe(df_base, hide_index=True, use_container_width=True)
                    if base_debt_f:
                        st.caption(f"Долг к {fwd_years[-1]}: {fmt_money(base_debt_f[-1])} тыс. ₸")
            with col_b:
                with st.container(border=True):
                    st.markdown("**🔴 Stress Case**")
                    df_stress = pd.DataFrame({
                        "Год": fwd_years,
                        "Выручка (тыс. ₸)": [fmt_money(v) for v in stress_rev_f],
                        "Чист. прибыль": [fmt_money(v) for v in stress_net_f],
                        "Net Margin": [f"{stress_margin}%"] * 3,
                        "ROE (оценка)": [f"{v}%" if v else "н/д" for v in stress_roe_f],
                    })
                    st.dataframe(df_stress, hide_index=True, use_container_width=True)
                    if stress_debt_f:
                        st.caption(f"Долг к {fwd_years[-1]}: {fmt_money(stress_debt_f[-1])} тыс. ₸")

            with st.container(border=True):
                st.markdown("#### График: Выручка — факт + прогноз (тыс. ₸)")
                fig = go.Figure()
                fact_revs = [st.session_state.data[y].get("revenue") for y in sorted_yrs]
                fig.add_trace(go.Scatter(x=sorted_yrs, y=fact_revs, mode="lines+markers", name="Факт",
                    line=dict(color="#5F5E5A", width=3), marker=dict(size=8)))
                fig.add_trace(go.Scatter(x=[last_year]+fwd_years, y=[last_rev]+base_rev_f,
                    mode="lines+markers", name="Base case",
                    line=dict(color="#0F6E56", width=3), marker=dict(size=8)))
                fig.add_trace(go.Scatter(x=[last_year]+fwd_years, y=[last_rev]+stress_rev_f,
                    mode="lines+markers", name="Stress case",
                    line=dict(color="#E24B4A", width=3, dash="dash"), marker=dict(size=8)))
                fig.update_layout(height=360, template="plotly_white",
                    legend=dict(orientation="h", y=-0.15), margin=dict(t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)

            st.info("💡 Прогноз — top-down модель на основе введённых данных. Все допущения задаются вручную через слайдеры выше.")
            st.warning("⚠️ Прогноз показывает возможные исходы, а не инвестиционную рекомендацию.")


# ──────────────────────────────────────────────────────────────────────
# СТРАНИЦА: ВЫВОД
# ──────────────────────────────────────────────────────────────────────
elif active_page == "📝 Вывод":
    st.markdown("# 📝 Итоговый вывод")
    st.caption("Сухой аналитический вывод на основе фактов. Без инвестиционных рекомендаций.")

    yrs = active_years()
    if not yrs:
        st.warning("Нет данных. Перейдите в «Ввод данных».")
    else:
        first_y, last_y = yrs[0], yrs[-1]
        r_first = calc_ratios(first_y)
        r_last = calc_ratios(last_y)
        unit = st.session_state.unit
        cname = st.session_state.company_name

        rev_f = st.session_state.data[first_y].get("revenue")
        rev_l = st.session_state.data[last_y].get("revenue")
        net_l = st.session_state.data[last_y].get("net")

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            delta = f"{(rev_l-rev_f)/abs(rev_f)*100:+.0f}% к {first_y}" if rev_f and rev_l else None
            st.metric(f"Выручка {last_y}", fmt_money(rev_l), delta)
        with mc2:
            v = r_last.get("ROE %")
            st.metric("ROE", f"{v}%" if v else "н/д")
        with mc3:
            v = r_last.get("Net Margin %")
            st.metric("Net Margin", f"{v}%" if v else "н/д")
        with mc4:
            v = r_last.get("Debt/Equity")
            st.metric("Debt/Equity", f"{v}" if v else "н/д")

        with st.container(border=True):
            st.markdown(f"### Структурированный вывод — {cname} ({first_y}–{last_y})")

            if rev_f and rev_l:
                d = (rev_l - rev_f) / abs(rev_f) * 100
                trend = "выросла" if d > 0 else "снизилась"
                st.markdown(f"**1. Динамика выручки.** Выручка {trend} с {fmt_money(rev_f)} до {fmt_money(rev_l)} {unit} ({'+' if d>=0 else ''}{d:.0f}% за {first_y}–{last_y}).")

            nm = r_last.get("Net Margin %"); roe = r_last.get("ROE %"); roa = r_last.get("ROA %")
            qual_roe = "Рентабельность капитала в норме (ROE ≥ 10%)." if roe and roe >= 10 else "ROE ниже нормы (<10%) — требует внимания." if roe else ""
            st.markdown(f"**2. Прибыльность ({last_y}).** Net Margin = {f'{nm}%' if nm else 'н/д'}, ROE = {f'{roe}%' if roe else 'н/д'}, ROA = {f'{roa}%' if roa else 'н/д'}. {qual_roe}")

            de = r_last.get("Debt/Equity"); ic = r_last.get("Interest Coverage"); nd = r_last.get("Net Debt/EBITDA")
            qual_de = "Долговая нагрузка умеренная (D/E ≤ 1.5)." if de and de <= 1.5 else "Повышенная долговая нагрузка (D/E > 1.5)." if de else ""
            st.markdown(f"**3. Финансовая устойчивость.** D/E = {f'{de}×' if de else 'н/д'}, Net Debt/EBITDA = {f'{nd}×' if nd else 'н/д'}, Interest Coverage = {f'{ic}×' if ic else 'н/д'}. {qual_de}")

            cfo_ni = r_last.get("CFO/Net Income")
            if cfo_ni:
                qual = "Прибыль подтверждена операционным кэшем." if cfo_ni >= 0.8 else "CFO отстаёт от прибыли — требует проверки качества прибыли."
                st.markdown(f"**4. Качество прибыли.** CFO/Net Income = {cfo_ni}×. {qual}")
            else:
                st.markdown("**4. Качество прибыли.** CFO не введён — для оценки добавьте данные ОДС.")

            cr = r_last.get("Current Ratio"); qr = r_last.get("Quick Ratio")
            qual_cr = "Ликвидность в норме." if cr and cr >= 1.5 else "Ликвидность ниже нормы (<1.5)." if cr else ""
            st.markdown(f"**5. Ликвидность.** Current Ratio = {cr if cr else 'н/д'}, Quick Ratio = {qr if qr else 'н/д'}. {qual_cr}")

            missing = [lbl for k, lbl in [("cfo","CFO"),("capex","Capex"),("ar","Дебиторка"),("interest","% расходы")]
                       if not st.session_state.data[last_y].get(k)]
            if missing:
                st.markdown(f"**6. Ограничения.** Не введены данные за {last_y}: {', '.join(missing)}. Это снижает точность части коэффициентов. Рекомендуется дополнить из отчётности KASE.")

        st.warning("⚠️ Вывод не является инвестиционной рекомендацией. Нормы — общепринятые; отраслевые бенчмарки могут отличаться.")


st.sidebar.markdown("---")
st.sidebar.caption("Индивидуальный проект · Финансовый анализ · АФО 2026")
