
from google import genai
import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Supermarket Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)


# --------------------------------------------------
# GEMINI CLIENT
# --------------------------------------------------

try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
except Exception:
    client = None


# --------------------------------------------------
# CUSTOM DASHBOARD DESIGN
# --------------------------------------------------

st.markdown("""

<style>

/* MAIN BACKGROUND */

.stApp {
    background: #F1F5F9;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #172554;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] label {
    font-weight: 600 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] {
    background: #FFFFFF;
    border-radius: 8px;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #0F172A !important;
}

/* HEADINGS */

h1 {
    color: #0F172A !important;
    font-size: 2.3rem !important;
    font-weight: 850 !important;
}

h2, h3 {
    color: #1E293B !important;
    font-weight: 750 !important;
}

/* KPI CARDS */

[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 3px 12px rgba(15,23,42,0.05);
    min-height: 115px;
}

[data-testid="stMetricLabel"] {
    color: #64748B !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: #0F172A !important;
    font-size: clamp(1.2rem, 2vw, 2rem) !important;
    font-weight: 850 !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}

/* GENERAL TEXT */

.stApp p,
.stApp li {
    color: #334155;
    font-weight: 500;
}

[data-testid="stCaptionContainer"] {
    color: #64748B !important;
}

/* TABS */

.stTabs [data-baseweb="tab"] {
    font-weight: 700;
    font-size: 14px;
    color: #334155;
}

.stTabs [aria-selected="true"] {
    color: #2563EB !important;
}

/* BUTTONS */

.stButton button,
.stDownloadButton button {
    background: #2563EB;
    color: white !important;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    padding: 10px 16px;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background: #1D4ED8;
    color: white !important;
}

/* CHART CONTAINERS */

[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    padding: 12px;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(15,23,42,0.04);
}

/* DIVIDERS */

hr {
    border-color: #CBD5E1;
}

/* FLOATING CHATBOT */

.st-key-floating_chatbot {
    position: fixed;
    bottom: 25px;
    left: 25px;
    z-index: 999999;
    width: auto;
}

.st-key-floating_chatbot [data-testid="stPopover"] > button {
    background: #2563EB;
    color: white;
    border-radius: 50%;
    width: 58px;
    height: 58px;
    font-size: 24px;
    border: none;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}

.st-key-floating_chatbot [data-testid="stPopover"] > button:hover {
    background: #1D4ED8;
    color: white;
}

/* FOOTER */

footer {
    visibility: hidden;
}

</style>

""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

@st.cache_data
def load_data():

    data = pd.read_csv(
        "dataset/SuperMarket Analysis.csv"
    )

    data["Date"] = pd.to_datetime(data["Date"])

    data["Month"] = data["Date"].dt.strftime("%b %Y")

    data["Time"] = pd.to_datetime(
        data["Time"],
        format="%I:%M:%S %p"
    )

    data["Hour"] = data["Time"].dt.hour

    data["Time Period"] = pd.cut(
        data["Hour"],
        bins=[-1, 11, 17, 23],
        labels=["Morning", "Afternoon", "Evening"]
    )

    return data


df = load_data()


# --------------------------------------------------
# CITY WISE CURRENCY MAPPING
# --------------------------------------------------

city_currency = {

    # Myanmar
    "Yangon": ("MMK", "K"),
    "Mandalay": ("MMK", "K"),
    "Naypyitaw": ("MMK", "K"),

    # India
    "Mumbai": ("INR", "₹"),
    "Delhi": ("INR", "₹"),
    "Bangalore": ("INR", "₹"),
    "Chennai": ("INR", "₹"),

    # United Kingdom
    "London": ("GBP", "£"),

    # United States
    "New York": ("USD", "$"),

    # Japan
    "Tokyo": ("JPY", "¥")
}


# --------------------------------------------------
# DASHBOARD TITLE
# --------------------------------------------------

st.title("🛒 Supermarket Sales Analysis Dashboard")

st.caption(
    "Interactive dashboard to analyze supermarket sales, "
    "customer behavior, product performance and payment methods."
)


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.title("📊 Dashboard Filters")


# Default filter values

if "city_filter" not in st.session_state:
    st.session_state.city_filter = df["City"].unique().tolist()

if "gender_filter" not in st.session_state:
    st.session_state.gender_filter = df["Gender"].unique().tolist()

if "product_filter" not in st.session_state:
    st.session_state.product_filter = df["Product line"].unique().tolist()

if "branch_filter" not in st.session_state:
    st.session_state.branch_filter = df["Branch"].unique().tolist()

if "date_filter" not in st.session_state:
    st.session_state.date_filter = (
        df["Date"].min().date(),
        df["Date"].max().date()
    )


# Reset filters

if st.sidebar.button(
    "🔄 Reset All Filters",
    use_container_width=True
):

    st.session_state.city_filter = df["City"].unique().tolist()

    st.session_state.gender_filter = df["Gender"].unique().tolist()

    st.session_state.product_filter = df["Product line"].unique().tolist()

    st.session_state.branch_filter = df["Branch"].unique().tolist()

    st.session_state.date_filter = (
        df["Date"].min().date(),
        df["Date"].max().date()
    )

    st.rerun()


# City filter

st.sidebar.multiselect(
    "Select City",
    options=df["City"].unique().tolist(),
    key="city_filter"
)


# Gender filter

st.sidebar.multiselect(
    "Select Gender",
    options=df["Gender"].unique().tolist(),
    key="gender_filter"
)


# Product filter

st.sidebar.multiselect(
    "Select Product Line",
    options=df["Product line"].unique().tolist(),
    key="product_filter"
)


# Branch filter

st.sidebar.multiselect(
    "Select Branch",
    options=df["Branch"].unique().tolist(),
    key="branch_filter"
)


# Date filter

st.sidebar.date_input(
    "Select Date Range",
    min_value=df["Date"].min().date(),
    max_value=df["Date"].max().date(),
    key="date_filter"
)


# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

filtered_data = df.copy()


filtered_data = filtered_data[
    filtered_data["City"].isin(
        st.session_state.city_filter
    )
]


filtered_data = filtered_data[
    filtered_data["Gender"].isin(
        st.session_state.gender_filter
    )
]


filtered_data = filtered_data[
    filtered_data["Product line"].isin(
        st.session_state.product_filter
    )
]


filtered_data = filtered_data[
    filtered_data["Branch"].isin(
        st.session_state.branch_filter
    )
]


# Date filter

selected_dates = st.session_state.date_filter

if len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered_data = filtered_data[
        (filtered_data["Date"].dt.date >= start_date) &
        (filtered_data["Date"].dt.date <= end_date)
    ]


# Sidebar transaction count

st.sidebar.divider()

st.sidebar.write(
    f"**Transactions:** {len(filtered_data):,}"
)


# --------------------------------------------------
# CHECK EMPTY DATA
# --------------------------------------------------

if filtered_data.empty:

    st.warning(
        "No data available for the selected filters. "
        "Please change your filters."
    )

    st.stop()


# --------------------------------------------------
# CALCULATE KPIs
# --------------------------------------------------

total_sales = filtered_data["Sales"].sum()

total_quantity = filtered_data["Quantity"].sum()

total_transactions = filtered_data["Invoice ID"].nunique()

average_rating = filtered_data["Rating"].mean()

total_gross_income = filtered_data["gross income"].sum()


# --------------------------------------------------
# DETERMINE SELECTED CURRENCY
# --------------------------------------------------

selected_cities = filtered_data["City"].unique().tolist()

selected_currencies = {
    city_currency.get(city, ("UNKNOWN", ""))[0]
    for city in selected_cities
}


if len(selected_currencies) == 1:

    currency_code = list(selected_currencies)[0]

    currency_symbol = next(
        (
            city_currency.get(city, ("UNKNOWN", ""))[1]
            for city in selected_cities
        ),
        ""
    )

    formatted_sales = (
        f"{currency_symbol}{total_sales:,.2f} {currency_code}"
    )

    chart_currency_prefix = currency_symbol

else:

    currency_code = "MIXED"

    currency_symbol = ""

    formatted_sales = "Multiple currencies"

    chart_currency_prefix = ""


# --------------------------------------------------
# DASHBOARD NAVIGATION
# --------------------------------------------------

overview_tab, sales_tab, customer_tab, product_tab, time_tab, data_tab = st.tabs(
    [
        "🏠 Overview",
        "📈 Sales Analysis",
        "👥 Customer Analysis",
        "📦 Product & Payment",
        "🕒 Time Analysis",
        "📂 Data & AI"
    ]
)


# ==================================================
# TAB 1: OVERVIEW
# ==================================================

with overview_tab:

    st.subheader("📌 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Sales",
            value=formatted_sales
        )

    with col2:
        st.metric(
            label="Total Quantity Sold",
            value=f"{total_quantity:,}"
        )

    with col3:
        st.metric(
            label="Total Transactions",
            value=f"{total_transactions:,}"
        )

    with col4:
        st.metric(
            label="Average Rating",
            value=f"{average_rating:.2f} ⭐"
        )


    if currency_code == "MIXED":

        st.warning(
            "Selected cities use different currencies. "
            "A combined sales total is not displayed as a single currency."
        )


    st.divider()

    st.subheader("💡 Business Insights")


    # Best product category

    category_sales = (
        filtered_data.groupby("Product line")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    best_category = category_sales.idxmax()

    best_category_sales = category_sales.max()


    # Top performing city

    city_sales = (
        filtered_data.groupby("City")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    top_city = city_sales.idxmax()

    top_city_sales = city_sales.max()


    # Popular payment method

    payment_counts = filtered_data["Payment"].value_counts()

    popular_payment = payment_counts.idxmax()


    insight_col1, insight_col2, insight_col3 = st.columns(3)


    with insight_col1:

        st.metric(
            label="🏆 Best Product Category",
            value=best_category,
            delta=f"Sales: {chart_currency_prefix}{best_category_sales:,.2f}"
        )


    with insight_col2:

        st.metric(
            label="📍 Top Performing City",
            value=top_city,
            delta=f"Sales: {chart_currency_prefix}{top_city_sales:,.2f}"
        )


    with insight_col3:

        st.metric(
            label="💳 Popular Payment Method",
            value=popular_payment,
            delta=f"{payment_counts.max()} transactions"
        )


    st.caption(
        f"Total Gross Income: {chart_currency_prefix}{total_gross_income:,.2f}"
    )

    st.divider()


    # Overview chart

    st.subheader("📊 Sales by City")

    overview_city_sales = (
        filtered_data.groupby("City")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )

    overview_fig = px.bar(
        overview_city_sales,
        x="City",
        y="Sales",
        color="City",
        text_auto=".2s",
        title="City-wise Sales Performance",
        template="plotly_white"
    )

    overview_fig.update_layout(
        xaxis_title="City",
        yaxis_title="Total Sales",
        showlegend=False,
        yaxis_tickprefix=chart_currency_prefix
    )

    st.plotly_chart(
        overview_fig,
        use_container_width=True
    )


# ==================================================
# TAB 2: SALES ANALYSIS
# ==================================================

with sales_tab:

    st.subheader("📈 Monthly Sales Analysis")


    # Monthly sales

    monthly_sales = (
        filtered_data.groupby("Month")["Sales"]
        .sum()
        .reset_index()
    )


    monthly_order = (
        filtered_data[["Month", "Date"]]
        .drop_duplicates(subset="Month")
        .sort_values("Date")["Month"]
        .tolist()
    )


    monthly_sales["Month"] = pd.Categorical(
        monthly_sales["Month"],
        categories=monthly_order,
        ordered=True
    )

    monthly_sales = monthly_sales.sort_values("Month")


    monthly_fig = px.line(
        monthly_sales,
        x="Month",
        y="Sales",
        markers=True,
        title="Monthly Sales Trend",
        template="plotly_white"
    )

    monthly_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Sales",
        hovermode="x unified",
        yaxis_tickprefix=chart_currency_prefix
    )

    st.plotly_chart(
        monthly_fig,
        use_container_width=True
    )


    st.divider()


    sales_col1, sales_col2 = st.columns(2)


    # City sales

    with sales_col1:

        city_sales_data = (
            filtered_data.groupby("City")["Sales"]
            .sum()
            .reset_index()
            .sort_values("Sales", ascending=False)
        )

        city_fig = px.bar(
            city_sales_data,
            x="City",
            y="Sales",
            color="City",
            text_auto=".2s",
            title="Sales by City",
            template="plotly_white"
        )

        city_fig.update_layout(
            xaxis_title="City",
            yaxis_title="Total Sales",
            showlegend=False,
            yaxis_tickprefix=chart_currency_prefix
        )

        st.plotly_chart(
            city_fig,
            use_container_width=True
        )


    # Branch sales

    with sales_col2:

        branch_data = (
            filtered_data.groupby("Branch")["Sales"]
            .sum()
            .reset_index()
            .sort_values(by="Sales", ascending=False)
        )

        branch_fig = px.bar(
            branch_data,
            x="Branch",
            y="Sales",
            color="Branch",
            text_auto=".2s",
            title="Total Sales by Branch",
            template="plotly_white"
        )

        branch_fig.update_layout(
            xaxis_title="Branch",
            yaxis_title="Total Sales",
            showlegend=False,
            yaxis_tickprefix=chart_currency_prefix
        )

        st.plotly_chart(
            branch_fig,
            use_container_width=True
        )


# ==================================================
# TAB 3: CUSTOMER ANALYSIS
# ==================================================

with customer_tab:

    st.subheader("👥 Customer Analysis")


    customer_col1, customer_col2 = st.columns(2)


    # Gender analysis

    with customer_col1:

        gender_data = (
            filtered_data.groupby("Gender")["Sales"]
            .sum()
            .reset_index()
        )

        gender_fig = px.pie(
            gender_data,
            names="Gender",
            values="Sales",
            title="Sales by Gender",
            hole=0.4,
            template="plotly_white"
        )

        gender_fig.update_traces(
            textinfo="label+percent"
        )

        st.plotly_chart(
            gender_fig,
            use_container_width=True
        )


    # Customer type analysis

    with customer_col2:

        customer_data = (
            filtered_data.groupby("Customer type")["Sales"]
            .sum()
            .reset_index()
        )

        customer_fig = px.bar(
            customer_data,
            x="Customer type",
            y="Sales",
            color="Customer type",
            text_auto=".2s",
            title="Sales by Customer Type",
            template="plotly_white"
        )

        customer_fig.update_layout(
            xaxis_title="Customer Type",
            yaxis_title="Total Sales",
            showlegend=False,
            yaxis_tickprefix=chart_currency_prefix
        )

        st.plotly_chart(
            customer_fig,
            use_container_width=True
        )


    st.divider()


    # Customer rating analysis

    st.subheader("⭐ Customer Rating Distribution")

    rating_fig = px.histogram(
        filtered_data,
        x="Rating",
        nbins=10,
        title="Customer Rating Distribution",
        template="plotly_white"
    )

    rating_fig.update_layout(
        xaxis_title="Customer Rating",
        yaxis_title="Number of Customers"
    )

    st.plotly_chart(
        rating_fig,
        use_container_width=True
    )


# ==================================================
# TAB 4: PRODUCT AND PAYMENT ANALYSIS
# ==================================================

with product_tab:

    st.subheader("📦 Product Category Analysis")


    product_sales = (
        filtered_data.groupby("Product line")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )


    product_fig = px.bar(
        product_sales,
        x="Product line",
        y="Sales",
        color="Product line",
        text_auto=".2s",
        title="Sales by Product Category",
        template="plotly_white"
    )

    product_fig.update_layout(
        xaxis_title="Product Category",
        yaxis_title="Total Sales",
        showlegend=False,
        yaxis_tickprefix=chart_currency_prefix
    )

    st.plotly_chart(
        product_fig,
        use_container_width=True
    )


    st.divider()


    # Top 5 products

    st.subheader("🏆 Top 5 Product Lines")


    top_products = (
        filtered_data.groupby("Product line")["Sales"]
        .sum()
        .reset_index()
        .sort_values(by="Sales", ascending=False)
        .head(5)
    )


    top_products_fig = px.bar(
        top_products,
        x="Sales",
        y="Product line",
        orientation="h",
        color="Sales",
        text_auto=".2s",
        title="Top 5 Product Lines by Sales",
        template="plotly_white"
    )

    top_products_fig.update_layout(
        xaxis_title="Total Sales",
        yaxis_title="Product Line",
        yaxis={"categoryorder": "total ascending"},
        xaxis_tickprefix=chart_currency_prefix
    )

    st.plotly_chart(
        top_products_fig,
        use_container_width=True
    )


    st.divider()


    # Payment analysis

    st.subheader("💳 Payment Method Analysis")


    payment_analysis = (
        filtered_data.groupby("Payment")
        .agg(
            Total_Sales=("Sales", "sum"),
            Transaction_Count=("Invoice ID", "nunique")
        )
        .reset_index()
    )


    payment_analysis["Sales_Percentage"] = (
        payment_analysis["Total_Sales"] /
        payment_analysis["Total_Sales"].sum()
    ) * 100


    payment_col1, payment_col2 = st.columns(2)


    # Payment sales chart

    with payment_col1:

        payment_sales_fig = px.bar(
            payment_analysis,
            x="Payment",
            y="Total_Sales",
            color="Payment",
            text_auto=".2s",
            title="Total Sales by Payment Method",
            template="plotly_white"
        )

        payment_sales_fig.update_layout(
            xaxis_title="Payment Method",
            yaxis_title="Total Sales",
            showlegend=False,
            yaxis_tickprefix=chart_currency_prefix
        )

        st.plotly_chart(
            payment_sales_fig,
            use_container_width=True
        )


    # Payment transaction chart

    with payment_col2:

        payment_count_fig = px.bar(
            payment_analysis,
            x="Payment",
            y="Transaction_Count",
            color="Payment",
            text_auto=True,
            title="Transactions by Payment Method",
            template="plotly_white"
        )

        payment_count_fig.update_layout(
            xaxis_title="Payment Method",
            yaxis_title="Number of Transactions",
            showlegend=False
        )

        st.plotly_chart(
            payment_count_fig,
            use_container_width=True
        )


    # Payment contribution

    payment_contribution_fig = px.pie(
        payment_analysis,
        names="Payment",
        values="Sales_Percentage",
        title="Sales Contribution by Payment Method",
        hole=0.4,
        template="plotly_white"
    )

    payment_contribution_fig.update_traces(
        textinfo="label+percent"
    )

    st.plotly_chart(
        payment_contribution_fig,
        use_container_width=True
    )


# ==================================================
# TAB 5: TIME ANALYSIS
# ==================================================

with time_tab:

    st.subheader("🕒 Sales by Time Period")


    time_data = (
        filtered_data.groupby(
            "Time Period",
            observed=False
        )["Sales"]
        .sum()
        .reset_index()
    )


    time_fig = px.bar(
        time_data,
        x="Time Period",
        y="Sales",
        color="Time Period",
        text_auto=".2s",
        title="Sales by Time Period",
        template="plotly_white"
    )

    time_fig.update_layout(
        xaxis_title="Time Period",
        yaxis_title="Total Sales",
        showlegend=False,
        yaxis_tickprefix=chart_currency_prefix
    )

    st.plotly_chart(
        time_fig,
        use_container_width=True
    )


    st.caption(
        "Morning: 12 AM–11 AM | "
        "Afternoon: 12 PM–5 PM | "
        "Evening: 6 PM–11 PM"
    )


# ==================================================
# TAB 6: DATA AND AI
# ==================================================

with data_tab:

    st.subheader("📂 Dataset Preview")


    st.write(
        f"Showing {len(filtered_data):,} filtered transactions"
    )


    st.dataframe(
        filtered_data,
        use_container_width=True,
        height=350
    )


    st.divider()


    # Download filtered data

    st.subheader("📥 Download Filtered Data")


    csv = filtered_data.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_supermarket_sales.csv",
        mime="text/csv"
    )


    st.divider()


    # Dataset information

    st.subheader("📊 Dataset Information")

    info_col1, info_col2, info_col3 = st.columns(3)

    with info_col1:
        st.metric(
            "Rows",
            f"{len(filtered_data):,}"
        )

    with info_col2:
        st.metric(
            "Columns",
            f"{len(filtered_data.columns):,}"
        )

    with info_col3:
        st.metric(
            "Cities",
            f"{filtered_data['City'].nunique():,}"
        )


# --------------------------------------------------
# AI SALES ASSISTANT - SIDEBAR
# --------------------------------------------------


# --------------------------------------------------
# AI SALES ASSISTANT - MAIN DASHBOARD
# --------------------------------------------------

st.divider()

st.subheader("🤖 AI Sales Assistant")

chat_col, info_col = st.columns([2, 1])

with chat_col:

    st.caption("Ask questions about your current filtered sales data.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show recent conversation
    for message in st.session_state.messages[-4:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.text_input(
        "Ask your sales question",
        key="main_ai_input",
        placeholder="e.g. Which city has highest sales?"
    )

    if st.button("Send to AI 🤖", key="main_ai_send") and user_prompt.strip():

        st.session_state.messages.append({
            "role": "user",
            "content": user_prompt
        })

        if client is None:
            st.error("Gemini API key not configured.")

        else:
            try:
                sales_summary = f"""
                You are a Supermarket Sales Analyst.

                Current filtered dashboard data:

                Total Sales: {total_sales:.2f}
                Currency: {selected_currencies}
                Total Transactions: {total_transactions}
                Total Quantity: {total_quantity}
                Average Rating: {average_rating:.2f}

                Sales by City:
                {filtered_data.groupby('City')['Sales'].sum().to_string()}

                Sales by Branch:
                {filtered_data.groupby('Branch')['Sales'].sum().to_string()}

                Sales by Product:
                {filtered_data.groupby('Product line')['Sales'].sum().to_string()}

                Payment Analysis:
                {filtered_data.groupby('Payment')['Sales'].sum().to_string()}
                """

                history = "\n".join(
                    f"{m['role']}: {m['content']}"
                    for m in st.session_state.messages[-7:]
                )

                with st.spinner("AI is thinking..."):

                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=f"""
                        {sales_summary}

                        Conversation:
                        {history}

                        Answer using only the provided data.
                        Use simple language.
                        Do not combine different currencies.
                        """
                    )

                    ai_response = response.text or "No response generated."

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response
                })

            except Exception as e:
                st.error(f"AI error: {e}")

        st.rerun()

with info_col:

    st.markdown("**📊 Current Dashboard Context**")

    st.metric("Transactions", f"{total_transactions:,}")
    st.metric("Cities Selected", len(selected_cities))

    if st.button("🗑️ Clear Chat", key="main_clear_chat"):
        st.session_state.messages = []
        st.rerun()

st.divider()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align: center; color: gray;">
        Supermarket Sales Analysis Dashboard
        <br>
        Built using Python, Pandas, Streamlit, Plotly and Gemini AI
    </div>
    """,
    unsafe_allow_html=True
)
