import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# ATUR LEBAR HALAMAN
st.set_page_config(layout="wide")

st.title("📈 Supermarket Analysis Dashboard")  # Judul Halaman

# 1. LOAD DATA
df = pd.read_csv("supermarket_sales.csv")

# 2. Cleaning & Feature Engineering
cols_to_convert = [
    'Unit price',
    'Tax 5%',
    'Total',
    'gross margin percentage',
    'gross income',
    'cogs',
    'Rating',
]
for col in cols_to_convert:
  if col in df.columns:
    df[col] = df[col].astype(str).str.replace(',', '.')
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Konversi kolom Date ke tipe datetime
df['Date'] = pd.to_datetime(df['Date'])

# Ekstrak Year dan Month
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month

# 3. SIDEBAR : SORTED
st.sidebar.header("Filters")

# Sorted by Branch
branches = sorted(df['Branch'].dropna().unique())
supermarket_branch = st.sidebar.pills(
    "Choose Branch", 
    options=branches,
    default=branches,
    selection_mode="multi"
)

# Sorted by Product Category
product_lines = sorted(df['Product line'].dropna().unique())
selected_products = st.sidebar.multiselect(
    "Choose Product Line",
    options=product_lines,
    default=product_lines,
)

# Sorted by Customer type
cus_types = ["All"] + sorted(df['Customer type'].dropna().unique().tolist())
customer_types = st.sidebar.radio(
    "Choose Customer type", 
    options=cus_types
)

# Sorted by Payment
available_payments = sorted(df['Payment'].dropna().unique().tolist())
payments = st.sidebar.multiselect(
    "Choose Gender", 
    options=available_payments,
    default = available_payments
)

# Sorted by Year
available_years = sorted(df['Year'].dropna().unique())
selected_years = st.sidebar.multiselect(
    "Choose Year",
    options=available_years,
    default = available_years
)

# Sorted by Month
month_range = st.sidebar.slider(
    "Choose Month Range",
    min_value=1,
    max_value=12,
    value=(1, 12)
)

# 4. FILTER DATA
if customer_types == "All":
    df_filtered = df[
        (df['Branch'].isin(supermarket_branch)) &
        (df['Product line'].isin(selected_products)) &
        (df['Payment'].isin(payments)) &
        (df['Year'].isin(selected_years)) &
        (df['Month'].between(month_range[0], month_range[1]))
    ]
else:
    df_filtered = df[
        (df['Branch'].isin(supermarket_branch)) &
        (df['Customer type'].isin(customer_types)) &
        (df['Product line'].isin(selected_products)) &
        (df['Payment'].isin(payments)) &
        (df['Year'].isin(selected_years)) &
        (df['Month'].between(month_range[0], month_range[1]))
    ]

# 5. TMPILKAN DATA
left, middle, right = st.columns(3, border=True)

total_transactions = len(df_filtered)
total_sales = df_filtered['Total'].sum() if not df_filtered.empty else 0
avg_rating = df_filtered['Rating'].mean() if not df_filtered.empty else 0

with left:
    st.badge("Transaction Amount", color="blue")
    st.metric(
        label="Transaction Amount", 
        value=f"{total_transactions:,}", 
        label_visibility="collapsed"
    )

with middle:
    st.badge("Total Sales", color="green")
    st.metric(
        label="Total Sales", 
        value=f"$ {total_sales:,.2f}", 
        label_visibility="collapsed"
    )
    
with right:
    st.badge("Average Rating", color="orange")
    st.metric(
        label="Average Rating", 
        value=f"{avg_rating:.2f}", 
        label_visibility="collapsed"
    )

# Penggunaan Tab untuk Memisahkan Tampilan Visual dan Data
tab1, tab2 = st.tabs(["📊 Analysis Graphics", "📋 Data Table"])

with tab1:
    if not df_filtered.empty:
        # Menampilkan grafik Sales berdasrkan gross income by Branch
        df_gross_income = df_filtered.groupby('Branch')['gross income'].sum().reset_index()

        fig_gross_income = px.bar(
            df_gross_income,
            x='Branch',
            y='gross income',
            color='Branch',
            title='Total Gross Income by Branch',
            labels={'Branch': 'Branch', 'gross income': 'Total Gross Income ($)'},
        )
            
        st.plotly_chart(fig_gross_income, use_container_width=True)
        
        # Layout 2 Kolom Grafik di Bawahnya
        #col1, col2 = st.columns(2)

        #with col1:
            # Menampilkan grafik Sales by Product by branch
        df_product_line = (
            df_filtered.groupby('Product line')["Total"]
            .sum()
            .reset_index()
           .sort_values("Product line")
        )
            
        fig_product_line_bar = px.bar(
            df_product_line,
            x='Product line',
            y='Total',
            color='Product line',
            title='Product Category Sales',
            labels={
                'Product line': 'Product Category',
                'Total': 'Total Sales ($)',
            },
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        st.plotly_chart(fig_product_line_bar, use_container_width=True)
            
            # Layout 2 Kolom Grafik di Bawahnya
            #col_a, col_b = st.columns(2)
            
        #with col2:
            # Menampilkan grafik Sales by Product by branch
        df_product_by_branch = (
            df_filtered.groupby(['Product line', 'Branch'])["Total"]
            .sum()
            .reset_index()
            .sort_values("Product line")
        )
            
        fig_product_bar = px.bar(
            df_product_by_branch,
            x='Total',
            y='Product line',
            color='Branch',
            barmode='group',
            title='Product Category Sales by Branch',
            labels={
                'Product line': 'Product Category',
                'Total': 'Total Sales ($)',
                'Branch': 'Branch'
            },
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        st.plotly_chart(fig_product_bar, use_container_width=True)
            
        # Layout 2 Kolom Grafik di Bawahnya
        #col_a, col_b = st.columns(2)
                
        #with col_a:
            # Menampilkan grafik Proporsi Penjualan berdasarkan Customer type by Branch
        df_customer_by_branch = df_filtered.groupby(['Branch', 'Customer type'])['Total'].sum().reset_index()

        fig_customer_sb = px.bar(
            df_customer_by_branch,
            x='Branch',
            y='Total',
            color='Customer type',
            barmode='group',
            title='Proportion of Sales by Customer Type in Each Branch',
            labels={
                'Branch': 'Branch',
                'Total': 'Total Sales ($)',
                'Customer type': 'Customer Type'
            },
            color_discrete_sequence=px.colors.qualitative.Set2
        )
            
        st.plotly_chart(fig_customer_sb, use_container_width=True)
        #with col_b:
            # Menampilkan grafik Proporsi Penjualan berdasarkan Payment by Branch
        df_pay_by_branch = df_filtered.groupby(['Branch', 'Payment'])['Total'].mean().reset_index()

        fig_pay_sb = px.bar(
            df_pay_by_branch,
            x='Branch',
            y='Total',
            color='Payment',
            barmode='group',
            title='Proportion of Sales by Payment Method in Each Branch',
            labels={
                'Branch': 'Branch',
                'Total': 'Total Sales ($)',
                'Payment': 'Payment Method'
           },
            color_discrete_sequence=px.colors.qualitative.Prism
        )
            
        st.plotly_chart(fig_pay_sb, use_container_width=True)
                
            
        # Menampilkan grafik Sales berdasrkan rata-rata rating by Branch
        df_avg_rating = df_filtered.groupby('Product line')['Rating'].mean().reset_index()

        fig_rating = px.bar(
            df_avg_rating,
            x='Product line',
            y='Rating',
            color='Product line',
            title='Average Sales Rating by Product Category',
            labels={'Product line': 'Product Category', 'Rating': 'Average Rating'},
        )
            
        st.plotly_chart(fig_rating, use_container_width=True)
        
    else:
        st.warning("Tidak ada data untuk ditampilkan berdasarkan filter terpilih.")
    
with tab2:
    if not df_filtered.empty:
        st.subheader("Sales Data Filter")
        st.write(f"Filtered Data ({len(df_filtered)} rows):")
        st.dataframe(df_filtered)
    else:
        st.warning("Tidak ada data untuk ditampilkan berdasarkan filter terpilih.")
