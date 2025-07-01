import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Financial Statement Dashboard", layout="wide")

st.title("📊 Financial Statement Dashboard – Income & Balance Sheet")

# --- Sidebar: Choose ticker and period (annual/quarter) ---
st.sidebar.header("Indstillinger")
ticker = st.sidebar.text_input("Ticker (e.g. AAPL, MSFT, TSLA):", value="AAPL").upper()
period = st.sidebar.radio("Vælg periode:", ["Årlig (annual)", "Kvartal (quarter)"])
if period.startswith("Årlig"):
    period_param = "annual"
else:
    period_param = "quarter"

# --- Number of periods to show (slider) ---
max_periods = 20 if period_param == "annual" else 40
default_periods = 3 if period_param == "annual" else 8
num_periods = st.sidebar.slider("Antal perioder (år/kvartaler):", min_value=1, max_value=max_periods, value=default_periods)

API_KEY = "7tm9pNymiv83LoOtSYfEjho3BMcFc6Nw"

# --- Income Statement ---
url_is = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period={period_param}&limit={max_periods}&apikey={API_KEY}"
response_is = requests.get(url_is)

# --- Balance Sheet ---
url_bs = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period={period_param}&limit={max_periods}&apikey={API_KEY}"
response_bs = requests.get(url_bs)

# --- Data Processing & Plots ---
if response_is.status_code == 200 and response_bs.status_code == 200:
    df_is = pd.DataFrame(response_is.json())
    df_bs = pd.DataFrame(response_bs.json())

    # Check for necessary columns before proceeding
    is_cols = ['calendarYear', 'period', 'revenue', 'grossProfit', 'operatingIncome', 'netIncome',
               'grossProfitRatio', 'operatingIncomeRatio', 'netIncomeRatio']
    bs_cols = ['calendarYear', 'period', 'totalDebt', 'cashAndShortTermInvestments', 'totalAssets']

    if all(col in df_is.columns for col in is_cols) and all(col in df_bs.columns for col in bs_cols):
        # Merge on date for easy plotting (date + period used as index for uniqueness)
        df_is['date_period'] = df_is['calendarYear'].astype(str) + " " + df_is['period']
        df_bs['date_period'] = df_bs['calendarYear'].astype(str) + " " + df_bs['period']

        # Only show as many periods as requested (latest periods)
        df_is = df_is.sort_values(['calendarYear', 'period'], ascending=[True, True]).tail(num_periods)
        df_bs = df_bs.sort_values(['calendarYear', 'period'], ascending=[True, True]).tail(num_periods)

        # X-axis labels: year (and quarter, if relevant)
        x_labels = df_is['calendarYear'] if period_param == "annual" else df_is['calendarYear'] + " " + df_is['period']

        # --- Income Statement Bar Chart ---
        fig_is = go.Figure()
        fig_is.add_bar(x=x_labels, y=df_is['revenue'] / 1e9, name='Revenue (Omsætning)')
        fig_is.add_bar(x=x_labels, y=df_is['grossProfit'] / 1e9, name='Gross Profit')
        fig_is.add_bar(x=x_labels, y=df_is['operatingIncome'] / 1e9, name='Operating Profit')
        fig_is.add_bar(x=x_labels, y=df_is['netIncome'] / 1e9, name='Net Profit')
        fig_is.update_layout(
            barmode='group',
            title=f"{ticker} – {'Årlige' if period_param == 'annual' else 'Kvartalsvise'} Nøgletal (Resultabottomgørelse)",
            xaxis_title="År" if period_param == "annual" else "År + Periode",
            yaxis_title="Milliarder USD",
            bargap=0.2,
            width=950,
            height=500,
            legend=dict(
                orientation="h",            # Horisontal
                yanchor="top",           # Fastgør bunden af legenden
                y=-0.2,                     # Lidt over selve figuren
                xanchor="center",           # Centreret på x-aksen
                x=0.5
            )
        )
        st.plotly_chart(fig_is, use_container_width=True)

        # --- Margins Line Chart ---
        fig_marg = go.Figure()
        fig_marg.add_trace(go.Scatter(x=x_labels, y=100 * df_is['grossProfitRatio'], mode='lines+markers', name='Gross Margin'))
        fig_marg.add_trace(go.Scatter(x=x_labels, y=100 * df_is['operatingIncomeRatio'], mode='lines+markers', name='Operating Margin'))
        fig_marg.add_trace(go.Scatter(x=x_labels, y=100 * df_is['netIncomeRatio'], mode='lines+markers', name='Profit Margin'))
        fig_marg.update_layout(
            title=f"{ticker} – {'Årlige' if period_param == 'annual' else 'Kvartalsvise'} Marginer",
            xaxis_title="År" if period_param == "annual" else "År + Periode",
            yaxis_title="Margin (%)",
            width=950,
            height=400,
            legend=dict(
                orientation="h",            # Horisontal
                yanchor="top",           # Fastgør bunden af legenden
                y=-0.25,                     # Lidt over selve figuren
                xanchor="center",           # Centreret på x-aksen
                x=0.5
            )
        )
        st.plotly_chart(fig_marg, use_container_width=True)

        # --- Balance Sheet Bar Chart ---
        fig_bs = go.Figure()
        fig_bs.add_bar(x=x_labels, y=df_bs['totalAssets'] / 1e9, name='Total Assets')
        fig_bs.add_bar(x=x_labels, y=df_bs['totalDebt'] / 1e9, name='Total Debt')
        fig_bs.add_bar(x=x_labels, y=df_bs['cashAndShortTermInvestments'] / 1e9, name='Cash, Cash equivalents & Short term investments')
        
        fig_bs.update_layout(
            barmode='group',
            title=f"{ticker} – {'Årlige' if period_param == 'annual' else 'Kvartalsvise'} Balance Sheet",
            xaxis_title="År" if period_param == "annual" else "År + Periode",
            yaxis_title="Milliarder USD",
            bargap=0.2,
            width=950,
            height=500,
            legend=dict(
                orientation="h",            # Horisontal
                yanchor="top",           # Fastgør bunden af legenden
                y=-0.2,                     # Lidt over selve figuren
                xanchor="center",           # Centreret på x-aksen
                x=0.5
            )
        )
        st.plotly_chart(fig_bs, use_container_width=True)

    else:
        st.warning("Kunne ikke finde alle nødvendige kolonner i dataen. Prøv evt. en anden ticker.")
else:
    st.warning("Kunne ikke hente data fra API. Tjek din ticker eller prøv igen senere.")

# --- Cash Flow Statement from FMP ---
url_cf = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?period={period_param}&limit={max_periods}&apikey={API_KEY}"
response_cf = requests.get(url_cf)

if response_cf.status_code == 200:
    df_cf = pd.DataFrame(response_cf.json())
    cf_cols = ['calendarYear', 'period', 'operatingCashFlow', 'capitalExpenditure', 'freeCashFlow']
    if all(col in df_cf.columns for col in cf_cols):
        df_cf = df_cf.sort_values(['calendarYear', 'period'], ascending=[True, True]).tail(num_periods)
        x_labels = df_cf['calendarYear'] if period_param == "annual" else df_cf['calendarYear'] + " " + df_cf['period']

        # Plot line chart for cash flow
        fig_cf = go.Figure()
        fig_cf.add_trace(go.Scatter(
            x=x_labels,
            y=df_cf['operatingCashFlow'] / 1e9,
            mode='lines+markers',
            name='Operating Cash Flow'
        ))
        fig_cf.add_trace(go.Scatter(
            x=x_labels,
            y=df_cf['capitalExpenditure'] / 1e9,
            mode='lines+markers',
            name='Capital Expenditure'
        ))
        fig_cf.add_trace(go.Scatter(
            x=x_labels,
            y=df_cf['freeCashFlow'] / 1e9,
            mode='lines+markers',
            name='Free Cash Flow'
        ))

        fig_cf.update_layout(
            title=f"{ticker} – {'Årlig' if period_param == 'annual' else 'Kvartalsvis'} Cash Flow",
            xaxis_title="År" if period_param == "annual" else "År + Periode",
            yaxis_title="Milliarder USD",
            width=950,
            height=500,
            legend=dict(
                orientation="h",            # Horisontal
                yanchor="top",           # Fastgør bunden af legenden
                y=-0.2,                     # Lidt over selve figuren
                xanchor="center",           # Centreret på x-aksen
                x=0.5
            )
        )
        st.plotly_chart(fig_cf, use_container_width=True)
    else:
        st.warning("Mangler cash flow værdier til plot.")
else:
    st.warning("Kunne ikke hente cash flow data fra API.")

# --- Daglig PE-ratio med forward-filled EPS ---
st.subheader("Daglig PE-ratio baseret på årlig EPS (forward-fill)")

# Brug samme ticker som resten af appen!
price_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line&apikey={API_KEY}"
price_response = requests.get(price_url)
if price_response.status_code == 200 and "historical" in price_response.json():
    price_data = price_response.json()
    prices = pd.DataFrame(price_data["historical"])
    prices['date'] = pd.to_datetime(prices['date'])
    prices = prices.set_index('date').sort_index()
else:
    st.warning("Kunne ikke hente prisdata for valgt ticker.")
    st.stop()

eps_url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?limit=30&apikey={API_KEY}"
eps_response = requests.get(eps_url)
if eps_response.status_code == 200:
    eps_data = eps_response.json()
    eps_df = pd.DataFrame(eps_data)
    if 'date' in eps_df.columns and 'netIncomePerShare' in eps_df.columns:
        eps_df['date'] = pd.to_datetime(eps_df['date'])
        eps_df = eps_df.set_index('date').sort_index()
        eps_df = eps_df[['netIncomePerShare']].rename(columns={'netIncomePerShare': 'eps'})
    else:
        st.warning("EPS-data findes ikke for denne ticker.")
        st.stop()
else:
    st.warning("Kunne ikke hente EPS-data for valgt ticker.")
    st.stop()

# Forward-fill EPS til hver dag
daily_eps = eps_df.reindex(prices.index, method='ffill')
df_pe = prices[['close']].join(daily_eps)
df_pe['pe'] = df_pe['close'] / df_pe['eps']

# Valgfri: Vælg visningsperiode
with st.expander("Vælg periode for PE-graf"):
    start_date = st.date_input("Startdato", value=df_pe.index.min().date())
    end_date = st.date_input("Slutdato", value=df_pe.index.max().date())
df_pe_show = df_pe[(df_pe.index >= pd.to_datetime(start_date)) & (df_pe.index <= pd.to_datetime(end_date))]

st.write("Pris-data shape:", prices.shape)
st.write("EPS-data shape:", eps_df.shape)
st.write("PE-data shape:", df_pe.shape)
st.write(df_pe.tail())

# Plot PE interaktivt
fig_pe = go.Figure()
fig_pe.add_trace(go.Scatter(
    x=df_pe_show.index, y=df_pe_show['pe'],
    mode='lines',
    name='PE-ratio'
))
fig_pe.update_layout(
    title=f"Daglig PE (Årlig EPS, forward-fill) for {ticker}",
    xaxis_title="Dato",
    yaxis_title="PE",
    width=950,
    height=500,
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,
        xanchor="center",
        x=0.5
    )
)
st.plotly_chart(fig_pe, use_container_width=True)

