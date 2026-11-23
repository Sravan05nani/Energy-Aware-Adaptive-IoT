
import os
import sys

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(PROJECT_DIR, "dashboard_data")
SRC_DIR = os.path.join(PROJECT_DIR, "src")

sys.path.insert(0, SRC_DIR)

from dashboard_engine import ALGORITHMS

st.set_page_config(
    page_title="Adaptive IoT Monitoring",
    page_icon="📡",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

/* ---------- GLOBAL ---------- */

.stApp {
    background: #0b1120;
    color: #e5e7eb;
}

[data-testid="stHeader"] {
    background: rgba(11, 17, 32, 0.85);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* ---------- TYPOGRAPHY ---------- */

h1 {
    color: #f8fafc !important;
    font-weight: 750 !important;
    letter-spacing: -0.8px;
}

h2, h3 {
    color: #e2e8f0 !important;
    font-weight: 650 !important;
}

p, label, li {
    color: #cbd5e1;
}

[data-testid="stCaptionContainer"] {
    color: #94a3b8;
}

/* ---------- METRIC CARDS ---------- */

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #17243a, #111c30);
    border: 1px solid #263852;
    padding: 18px 20px;
    border-radius: 13px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
    transition: border-color 0.2s ease, transform 0.2s ease;
}

[data-testid="stMetric"]:hover {
    border-color: #3b82f6;
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-size: 0.88rem !important;
}

[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-weight: 750 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.82rem;
}

/* ---------- SIDEBAR ---------- */

[data-testid="stSidebar"] {
    background: #101a2b;
    border-right: 1px solid #263852;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #94a3b8;
}

/* ---------- BUTTONS ---------- */

.stButton > button {
    border-radius: 9px;
    border: 1px solid #334965;
    background: #17243a;
    color: #e2e8f0;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    border-color: #60a5fa;
    color: #ffffff;
    background: #1e3554;
}

/* ---------- INPUTS ---------- */

[data-baseweb="select"] > div {
    border-radius: 8px;
}

[data-testid="stSlider"] {
    padding-top: 8px;
    padding-bottom: 8px;
}

/* ---------- TABS ---------- */

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #263852;
}

.stTabs [data-baseweb="tab"] {
    height: 45px;
    padding: 0 16px;
    color: #94a3b8;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    color: #60a5fa !important;
    border-bottom-color: #3b82f6 !important;
}

/* ---------- EXPANDERS ---------- */

[data-testid="stExpander"] {
    background: #111c30;
    border: 1px solid #263852;
    border-radius: 11px;
    margin-bottom: 10px;
}

[data-testid="stExpander"] summary {
    color: #e2e8f0;
    font-weight: 600;
}

/* ---------- TABLES ---------- */

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid #263852;
    border-radius: 10px;
    overflow: hidden;
}

/* ---------- ALERTS ---------- */

[data-testid="stAlert"] {
    border-radius: 10px;
}

/* ---------- DIVIDERS ---------- */

hr {
    border-color: #263852 !important;
    opacity: 0.8;
}

/* ---------- NODE CARDS ---------- */

.node-card {
    background: linear-gradient(145deg, #17243a, #111c30);
    border: 1px solid #263852;
    padding: 17px;
    border-radius: 13px;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

/* ---------- RESPONSIVE LAYOUT ---------- */

@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.8rem 2rem 0.8rem;
    }

    h1 {
        font-size: 1.7rem !important;
    }

    [data-testid="stMetric"] {
        padding: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0 9px;
        font-size: 0.85rem;
    }
}

</style>
""", unsafe_allow_html=True)


# DATA LOADING
# --------------------------------------------------

@st.cache_data
def load_evaluation():

    path = os.path.join(
        DATA_DIR,
        "intel_evaluation_dataset.csv.gz"
    )

    df = pd.read_csv(
        path,
        compression="gzip",
        parse_dates=["timestamp"]
    )

    df = df.sort_values(
        ["timestamp", "moteid"]
    ).reset_index(drop=True)

    return df


@st.cache_data
def load_transmissions():

    results = {}

    for algorithm, filename in ALGORITHMS.items():

        path = os.path.join(DATA_DIR, filename)

        results[algorithm] = pd.read_csv(
            path,
            compression="gzip",
            parse_dates=["timestamp"]
        )

        results[algorithm] = results[algorithm].sort_values(
            ["timestamp", "moteid"]
        )

    return results


@st.cache_data
def load_metrics():

    csv_dir = os.path.join(DATA_DIR)

    files = {
        "transmission": "transmission_comparison.csv",
        "accuracy": "reconstruction_accuracy.csv",
        "freshness": "freshness_comparison.csv",
        "energy": "energy_comparison.csv",
        "node_accuracy": "node_accuracy_comparison.csv",
        "node_freshness": "node_freshness_comparison.csv",
        "node_energy": "node_energy_comparison.csv"
    }

    results = {}

    for key, filename in files.items():

        path = os.path.join(csv_dir, filename)

        results[key] = pd.read_csv(path)

    return results


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:

    evaluation = load_evaluation()

    transmissions = load_transmissions()

    metrics = load_metrics()

except Exception as error:

    st.error(f"Unable to load project data: {error}")

    st.stop()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("📡 Adaptive IoT")

st.sidebar.caption(
    "Energy-Aware Adaptive Sensor Network"
)

st.sidebar.divider()

algorithm = st.sidebar.selectbox(
    "Sampling Algorithm",
    list(ALGORITHMS.keys()),
    index=3,
    key="algorithm_selector"
)

st.sidebar.divider()

st.sidebar.subheader("Historical Playback")

# Initialize persistent widget states
if "timeline_slider" not in st.session_state:
    st.session_state.timeline_slider = 0

if "playback_speed" not in st.session_state:
    st.session_state.playback_speed = 100

if "is_playing" not in st.session_state:
    st.session_state.is_playing = False

if "last_refresh_count" not in st.session_state:
    st.session_state.last_refresh_count = None


# Playback callbacks
def start_playback():
    if st.session_state.timeline_slider >= len(evaluation) - 1:
        st.session_state.timeline_slider = 0

    st.session_state.is_playing = True
    st.session_state.last_refresh_count = None


def pause_playback():
    st.session_state.is_playing = False
    st.session_state.last_refresh_count = None


def move_previous():
    st.session_state.timeline_slider = max(
        0,
        st.session_state.timeline_slider - st.session_state.playback_speed
    )


def move_next():
    st.session_state.timeline_slider = min(
        len(evaluation) - 1,
        st.session_state.timeline_slider + st.session_state.playback_speed
    )


def reset_timeline():
    st.session_state.timeline_slider = 0
    st.session_state.is_playing = False
    st.session_state.last_refresh_count = None


# Playback speed
speed = st.sidebar.selectbox(
    "Playback step size",
    [1, 10, 100, 500, 1000],
    key="playback_speed"
)


# Play and Pause buttons
play_col, pause_col = st.sidebar.columns(2)

play_col.button(
    "▶ Play",
    on_click=start_playback,
    use_container_width=True
)

pause_col.button(
    "⏸ Pause",
    on_click=pause_playback,
    use_container_width=True
)


# Automatic playback refresh
if st.session_state.is_playing:

    from streamlit_autorefresh import st_autorefresh

    # Trigger a Streamlit rerun every 500 milliseconds
    st_autorefresh(
        interval=500,
        key="playback_autorefresh"
    )

    # Advance the timeline on every automatic rerun
    next_position = (
        st.session_state.timeline_slider + speed
    )

    if next_position >= len(evaluation) - 1:
        st.session_state.timeline_slider = len(evaluation) - 1
        st.session_state.is_playing = False
    else:
        st.session_state.timeline_slider = next_position


# Manual navigation
col_a, col_b = st.sidebar.columns(2)

col_a.button(
    "◀ Previous",
    on_click=move_previous
)

col_b.button(
    "Next ▶",
    on_click=move_next
)

st.sidebar.button(
    "Reset Timeline",
    on_click=reset_timeline,
    use_container_width=True
)


# Historical timeline slider
cursor = st.sidebar.slider(
    "Historical record position",
    min_value=0,
    max_value=len(evaluation) - 1,
    key="timeline_slider"
)

st.session_state.cursor = cursor

current_row = evaluation.iloc[cursor]

current_time = current_row["timestamp"]

st.sidebar.caption(
    "Playback status: "
    + ("▶ Playing" if st.session_state.is_playing else "⏸ Paused")
)

st.sidebar.divider()

st.sidebar.caption("Historical deployment")

st.sidebar.write(
    "February 28 – March 24, 2004"
)

st.sidebar.caption(
    "This dashboard replays historical measurements. "
    "It is not a live physical sensor network."
)


# --------------------------------------------------
# TRANSMISSION DATA
# --------------------------------------------------

tx_df = transmissions[algorithm]

eligible_data = evaluation[
    evaluation["environment_valid"] == True
]

current_eligible = eligible_data[
    eligible_data.index <= cursor
]

processed_count = len(current_eligible)

tx_until_now = tx_df[
    (tx_df["timestamp"] < current_time)
    |
    (
        (tx_df["timestamp"] == current_time)
        &
        (tx_df["moteid"] <= current_row["moteid"])
    )
]

transmitted_count = len(tx_until_now)

skipped_count = processed_count - transmitted_count

reduction = (
    skipped_count / processed_count * 100
    if processed_count > 0 else 0
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📡 Adaptive IoT Monitoring Dashboard")

st.caption(
    "Historical replay of Intel Berkeley Research Lab "
    "wireless sensor measurements"
)

st.info(
    "Historical sensor measurements are real recorded data. "
    "Transmission decisions are simulated. Energy values "
    "are model-based estimates."
)


# --------------------------------------------------
# NETWORK OVERVIEW
# --------------------------------------------------

st.subheader("Network Overview")

nodes = sorted(evaluation["moteid"].unique())

col1, col2, col3, col4 = st.columns(4)

col1.metric("Sensor Nodes", len(nodes))

col2.metric(
    "Processed Measurements",
    f"{processed_count:,}"
)

col3.metric(
    "Transmitted Packets",
    f"{transmitted_count:,}"
)

col4.metric(
    "Transmission Reduction",
    f"{reduction:.2f}%"
)

st.caption(
    f"Current historical timestamp: {current_time}"
)


# --------------------------------------------------

# --------------------------------------------------
# NODE MONITORING
# --------------------------------------------------

st.subheader("Sensor Node Monitoring")

st.caption(
    "Node status reflects the latest eligible source measurement "
    "processed at the current historical playback position."
)


def display_value(value, suffix="", precision=2):

    if pd.isna(value):
        return "N/A"

    return f"{float(value):.{precision}f}{suffix}"


for row_start in range(0, len(nodes), 3):

    node_columns = st.columns(3)

    for index, node in enumerate(nodes[row_start:row_start + 3]):

        with node_columns[index]:

            with st.container(border=True):

                st.markdown(f"### Node {node}")

                # Latest eligible source measurement for this node
                node_data = evaluation[
                    (evaluation["moteid"] == node)
                    & (evaluation.index <= cursor)
                    & (evaluation["environment_valid"] == True)
                ]

                # Transmissions processed up to current playback position
                node_tx = tx_until_now[
                    tx_until_now["moteid"] == node
                ]

                latest = (
                    node_data.iloc[-1]
                    if not node_data.empty
                    else None
                )

                latest_tx = (
                    node_tx.iloc[-1]
                    if not node_tx.empty
                    else None
                )

                if latest is None:

                    st.info("No valid measurement processed yet.")

                else:

                    # Determine whether the latest eligible source
                    # measurement was transmitted.
                    latest_key = (
                        pd.Timestamp(latest["timestamp"]),
                        int(latest["moteid"])
                    )

                    transmitted_keys = set(
                        zip(
                            node_tx["timestamp"],
                            node_tx["moteid"].astype(int)
                        )
                    )

                    is_transmitted = latest_key in transmitted_keys

                    if is_transmitted:
                        st.success("● TRANSMITTED")
                    else:
                        st.warning("● SKIPPED")

                    # SOURCE MEASUREMENT
                    st.markdown("**Latest Source Measurement**")

                    st.write(
                        f"🌡️ Temperature: "
                        f"{display_value(latest['temperature_clean'], ' °C')}"
                    )

                    st.write(
                        f"💧 Humidity: "
                        f"{display_value(latest['humidity_clean'], '%')}"
                    )

                    st.write(
                        f"☀️ Light: "
                        f"{display_value(latest['light_clean'])}"
                    )

                    st.write(
                        f"🔋 Recorded Voltage: "
                        f"{display_value(latest['voltage_clean'], ' V', 3)}"
                    )

                    st.caption(
                        f"Source timestamp: {latest['timestamp']}"
                    )

                # LAST TRANSMITTED MEASUREMENT
                st.divider()

                st.markdown("**Last Transmitted Reading**")

                if latest_tx is not None:

                    st.write(
                        f"🌡️ Temperature: "
                        f"{display_value(latest_tx['temperature'], ' °C')}"
                    )

                    st.write(
                        f"💧 Humidity: "
                        f"{display_value(latest_tx['humidity'], '%')}"
                    )

                    st.write(
                        f"☀️ Light: "
                        f"{display_value(latest_tx['light'])}"
                    )

                    st.write(
                        f"🔋 Voltage: "
                        f"{display_value(latest_tx['voltage'], ' V', 3)}"
                    )

                    st.caption(
                        f"Last packet: {latest_tx['timestamp']}"
                    )

                    # Historical data freshness
                    freshness_seconds = (
                        current_time - latest_tx["timestamp"]
                    ).total_seconds()

                    if freshness_seconds < 60:

                        freshness_text = (
                            f"{freshness_seconds:.1f} seconds"
                        )

                    elif freshness_seconds < 3600:

                        freshness_text = (
                            f"{freshness_seconds / 60:.1f} minutes"
                        )

                    else:

                        freshness_text = (
                            f"{freshness_seconds / 3600:.2f} hours"
                        )

                    st.metric(
                        "Data Freshness",
                        freshness_text
                    )

                else:

                    st.info("No packet transmitted yet.")



# --------------------------------------------------
# HISTORICAL SENSOR TRENDS AND TRANSMISSION ANALYSIS
# --------------------------------------------------

st.subheader("Historical Sensor Trends & Transmission Analysis")

st.caption(
    "Compare original sensor measurements with the readings "
    "transmitted by the selected adaptive sampling algorithm."
)

import plotly.graph_objects as go

chart_col1, chart_col2 = st.columns(2)

with chart_col1:

    sensor_choice = st.selectbox(
        "Select sensor",
        ["Temperature", "Humidity", "Light", "Voltage"],
        key="trend_sensor"
    )

with chart_col2:

    node_options = ["All Nodes"] + [
        int(node) for node in nodes
    ]

    selected_node = st.selectbox(
        "Select sensor node",
        node_options,
        key="trend_node"
    )


sensor_mapping = {
    "Temperature": ("temperature_clean", "temperature", "°C"),
    "Humidity": ("humidity_clean", "humidity", "%"),
    "Light": ("light_clean", "light", ""),
    "Voltage": ("voltage_clean", "voltage", "V")
}

source_column, tx_column, unit = sensor_mapping[sensor_choice]

# Original historical source readings up to playback cursor
chart_data = evaluation[
    (evaluation.index <= cursor)
    & evaluation[source_column].notna()
].copy()

if selected_node != "All Nodes":

    chart_data = chart_data[
        chart_data["moteid"] == selected_node
    ]

# Keep the most recent 400 source readings per node
chart_data = (
    chart_data
    .groupby("moteid", group_keys=False)
    .tail(400)
    .sort_values(["timestamp", "moteid"])
)

# Corresponding transmitted readings
chart_tx = tx_df[
    (tx_df["timestamp"] <= current_time)
    & tx_df[tx_column].notna()
].copy()

if selected_node != "All Nodes":

    chart_tx = chart_tx[
        chart_tx["moteid"] == selected_node
    ]

# Restrict transmissions to the visible historical window
if not chart_data.empty:

    chart_start = chart_data["timestamp"].min()

    chart_tx = chart_tx[
        chart_tx["timestamp"] >= chart_start
    ]

# Construct chart
fig = go.Figure()

visible_nodes = (
    [selected_node]
    if selected_node != "All Nodes"
    else sorted(chart_data["moteid"].unique())
)

for node in visible_nodes:

    node_source = chart_data[
        chart_data["moteid"] == node
    ]

    node_transmissions = chart_tx[
        chart_tx["moteid"] == node
    ]

    # Original sensor readings
    fig.add_trace(
        go.Scatter(
            x=node_source["timestamp"],
            y=node_source[source_column],
            mode="lines",
            name=f"Node {node} — Source",
            legendgroup=f"node_{node}",
            line=dict(width=1.8),
            hovertemplate=(
                f"Node {node}<br>"
                "Source reading: %{y:.3f}<br>"
                "Time: %{x}<extra></extra>"
            )
        )
    )

    # Actual transmitted readings
    fig.add_trace(
        go.Scatter(
            x=node_transmissions["timestamp"],
            y=node_transmissions[tx_column],
            mode="markers",
            name=f"Node {node} — Transmitted",
            legendgroup=f"node_{node}",
            marker=dict(
                size=7,
                symbol="circle",
                line=dict(width=1)
            ),
            hovertemplate=(
                f"Node {node}<br>"
                "Transmitted reading: %{y:.3f}<br>"
                "Packet time: %{x}<extra></extra>"
            )
        )
    )

fig.update_layout(
    template="plotly_dark",
    height=550,
    title=f"{sensor_choice}: Source vs Transmitted Measurements",
    xaxis_title="Historical Time",
    yaxis_title=f"{sensor_choice} ({unit})" if unit else sensor_choice,
    hovermode="closest",
    legend_title="Measurement Type",
    margin=dict(l=20, r=20, t=65, b=20)
)

fig.update_xaxes(
    showgrid=True,
    rangeslider_visible=False
)

fig.update_yaxes(
    showgrid=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.caption(
    f"Algorithm: {algorithm} | "
    f"Visible source readings: {len(chart_data):,} | "
    f"Visible transmitted readings: {len(chart_tx):,}"
)



# --------------------------------------------------
# PERFORMANCE ANALYTICS CENTRE
# --------------------------------------------------

st.divider()

st.title("📊 Algorithm Performance Analytics")

st.caption(
    "Comparative evaluation of communication efficiency, "
    "estimated energy consumption, reconstruction accuracy "
    "and data freshness."
)

# Independent copies of experimental results
comparison = metrics["transmission"].copy()
accuracy = metrics["accuracy"].copy()
freshness = metrics["freshness"].copy()
energy = metrics["energy"].copy()

# Consistent algorithm ordering
algorithm_order = [
    "Fixed",
    "Rate",
    "Threshold",
    "Threshold-H120",
    "Threshold-H180"
]

comparison["Algorithm"] = pd.Categorical(
    comparison["Algorithm"],
    categories=algorithm_order,
    ordered=True
)

accuracy["Algorithm"] = pd.Categorical(
    accuracy["Algorithm"],
    categories=algorithm_order,
    ordered=True
)

freshness["Algorithm"] = pd.Categorical(
    freshness["Algorithm"],
    categories=algorithm_order,
    ordered=True
)

energy["Algorithm"] = pd.Categorical(
    energy["Algorithm"],
    categories=algorithm_order,
    ordered=True
)

comparison = comparison.sort_values("Algorithm")
accuracy = accuracy.sort_values(["Sensor", "Algorithm"])
freshness = freshness.sort_values("Algorithm")
energy = energy.sort_values("Algorithm")


# --------------------------------------------------
# KEY EXPERIMENTAL FINDINGS
# --------------------------------------------------

best_reduction = comparison.loc[
    comparison["Transmission_Reduction_Percent"].idxmax()
]

lowest_energy = energy.loc[
    energy["Total_Energy_J"].idxmin()
]

best_accuracy = accuracy.loc[
    accuracy.groupby("Sensor")["RMSE"].idxmin()
]

h120_energy = energy[
    energy["Algorithm"] == "Threshold-H120"
].iloc[0]

h120_reduction = comparison[
    comparison["Algorithm"] == "Threshold-H120"
].iloc[0]

st.subheader("Key Experimental Findings")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Highest Transmission Reduction",
    f"{best_reduction['Transmission_Reduction_Percent']:.2f}%",
    str(best_reduction["Algorithm"])
)

k2.metric(
    "Highest Estimated Energy Savings",
    f"{energy['Energy_Savings_Percent'].max():.2f}%",
    str(energy.loc[energy["Energy_Savings_Percent"].idxmax(), "Algorithm"])
)

k3.metric(
    "H120 Energy Savings",
    f"{h120_energy['Energy_Savings_Percent']:.2f}%"
)

k4.metric(
    "H120 Transmission Reduction",
    f"{h120_reduction['Transmission_Reduction_Percent']:.2f}%"
)

st.info(
    "Threshold-H120 achieved the lowest observed RMSE for "
    "temperature, humidity and light among the five evaluated "
    "configurations. Threshold achieved greater communication "
    "and estimated energy reductions, but had substantially "
    "worse freshness."
)


# --------------------------------------------------
# ANALYTICS TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📡 Communication",
    "⚡ Energy",
    "🎯 Accuracy",
    "⏱️ Freshness",
    "⚖️ Trade-off Analysis"
])


# --------------------------------------------------
# TAB 1: COMMUNICATION
# --------------------------------------------------

with tab1:

    st.subheader("Communication Efficiency")

    fig_transmission = px.bar(
        comparison,
        x="Algorithm",
        y="Transmission_Reduction_Percent",
        color="Algorithm",
        text="Transmission_Reduction_Percent",
        title="Transmission Reduction by Algorithm",
        labels={
            "Transmission_Reduction_Percent": "Transmission Reduction (%)",
            "Algorithm": "Algorithm"
        }
    )

    fig_transmission.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_transmission.update_layout(
        template="plotly_dark",
        height=450,
        showlegend=False,
        yaxis_range=[
            0,
            comparison["Transmission_Reduction_Percent"].max() * 1.2
        ]
    )

    st.plotly_chart(fig_transmission, use_container_width=True)

    fig_packets = px.bar(
        comparison,
        x="Algorithm",
        y="Transmissions",
        color="Algorithm",
        text="Transmissions",
        title="Total Transmitted Packets",
        labels={
            "Transmissions": "Number of Transmissions",
            "Algorithm": "Algorithm"
        }
    )

    fig_packets.update_layout(
        template="plotly_dark",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig_packets, use_container_width=True)

    with st.expander("View communication metrics"):

        st.dataframe(
            comparison,
            use_container_width=True,
            hide_index=True
        )


# --------------------------------------------------
# TAB 2: ENERGY
# --------------------------------------------------

with tab2:

    st.subheader("Estimated Energy Consumption")

    st.warning(
        "Energy results are model-based estimates, not physical "
        "measurements from ESP32 hardware. The model includes "
        "sensing, processing and transmission energy."
    )

    fig_energy = px.bar(
        energy,
        x="Algorithm",
        y=[
            "Sensing_Energy_J",
            "Processing_Energy_J",
            "Transmission_Energy_J"
        ],
        title="Energy Consumption Breakdown",
        labels={
            "value": "Energy (Joules)",
            "variable": "Energy Component",
            "Algorithm": "Algorithm"
        },
        barmode="stack"
    )

    fig_energy.update_layout(
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(fig_energy, use_container_width=True)

    fig_savings = px.bar(
        energy,
        x="Algorithm",
        y="Energy_Savings_Percent",
        color="Algorithm",
        text="Energy_Savings_Percent",
        title="Estimated Energy Savings Relative to Fixed Sampling",
        labels={
            "Energy_Savings_Percent": "Energy Savings (%)"
        }
    )

    fig_savings.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_savings.update_layout(
        template="plotly_dark",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig_savings, use_container_width=True)

    with st.expander("View energy metrics"):

        st.dataframe(
            energy,
            use_container_width=True,
            hide_index=True
        )


# --------------------------------------------------
# TAB 3: RECONSTRUCTION ACCURACY
# --------------------------------------------------

with tab3:

    st.subheader("Reconstruction Accuracy")

    selected_accuracy_sensor = st.selectbox(
        "Select sensor for accuracy analysis",
        ["temperature", "humidity", "light"],
        key="accuracy_sensor"
    )

    selected_accuracy_metric = st.radio(
        "Accuracy metric",
        ["MAE", "RMSE"],
        horizontal=True,
        key="accuracy_metric"
    )

    sensor_accuracy = accuracy[
        accuracy["Sensor"] == selected_accuracy_sensor
    ].copy()

    fig_accuracy = px.bar(
        sensor_accuracy,
        x="Algorithm",
        y=selected_accuracy_metric,
        color="Algorithm",
        text=selected_accuracy_metric,
        title=(
            f"{selected_accuracy_sensor.title()} "
            f"{selected_accuracy_metric} Comparison"
        ),
        labels={
            selected_accuracy_metric: selected_accuracy_metric,
            "Algorithm": "Algorithm"
        }
    )

    fig_accuracy.update_layout(
        template="plotly_dark",
        height=450,
        showlegend=False
    )

    st.plotly_chart(fig_accuracy, use_container_width=True)

    st.caption(
        "Lower MAE and RMSE indicate better reconstruction accuracy. "
        "Metrics are compared separately for each sensor because "
        "their physical units and numerical scales differ."
    )

    with st.expander("View all reconstruction metrics"):

        st.dataframe(
            accuracy,
            use_container_width=True,
            hide_index=True
        )


# --------------------------------------------------
# TAB 4: DATA FRESHNESS
# --------------------------------------------------

with tab4:

    st.subheader("Data Freshness Analysis")

    st.caption(
        "Freshness represents the age of the most recently "
        "transmitted measurement when each source observation "
        "was evaluated."
    )

    fig_freshness = px.bar(
        freshness,
        x="Algorithm",
        y=["Median_Age_sec", "P95_Age_sec"],
        barmode="group",
        title="Median and 95th Percentile Data Age",
        labels={
            "value": "Data Age (seconds)",
            "variable": "Freshness Metric",
            "Algorithm": "Algorithm"
        }
    )

    fig_freshness.update_layout(
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(fig_freshness, use_container_width=True)

    fig_max_age = px.bar(
        freshness,
        x="Algorithm",
        y="Maximum_Age_sec",
        color="Algorithm",
        title="Maximum Observed Data Age",
        labels={
            "Maximum_Age_sec": "Maximum Data Age (seconds)"
        }
    )

    fig_max_age.update_layout(
        template="plotly_dark",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig_max_age, use_container_width=True)

    with st.expander("View freshness metrics"):

        st.dataframe(
            freshness,
            use_container_width=True,
            hide_index=True
        )


# --------------------------------------------------
# TAB 5: ENERGY-ACCURACY TRADE-OFF
# --------------------------------------------------

with tab5:

    st.subheader("Energy–Accuracy Trade-off")

    selected_tradeoff_sensor = st.selectbox(
        "Select sensor for trade-off analysis",
        ["temperature", "humidity", "light"],
        key="tradeoff_sensor"
    )

    tradeoff = energy.merge(
        accuracy[
            accuracy["Sensor"] == selected_tradeoff_sensor
        ][["Algorithm", "MAE", "RMSE"]],
        on="Algorithm"
    )

    tradeoff = tradeoff.merge(
        comparison[
            ["Algorithm", "Transmission_Reduction_Percent"]
        ],
        on="Algorithm"
    )

    tradeoff = tradeoff.merge(
        freshness[
            ["Algorithm", "P95_Age_sec"]
        ],
        on="Algorithm"
    )

    fig_tradeoff = px.scatter(
        tradeoff,
        x="Total_Energy_J",
        y="RMSE",
        color="Algorithm",
        size="Transmission_Reduction_Percent",
        text="Algorithm",
        hover_data={
            "Energy_Savings_Percent": ":.2f",
            "Transmission_Reduction_Percent": ":.2f",
            "P95_Age_sec": ":.2f",
            "MAE": ":.5f"
        },
        title=(
            f"Energy Consumption vs Reconstruction Error — "
            f"{selected_tradeoff_sensor.title()}"
        ),
        labels={
            "Total_Energy_J": "Estimated Total Energy (J)",
            "RMSE": "Reconstruction RMSE",
            "Transmission_Reduction_Percent": "Transmission Reduction (%)"
        }
    )

    fig_tradeoff.update_traces(
        textposition="top center"
    )

    fig_tradeoff.update_layout(
        template="plotly_dark",
        height=550
    )

    st.plotly_chart(fig_tradeoff, use_container_width=True)

    st.caption(
        "Lower energy and lower RMSE are desirable. Marker size "
        "represents transmission reduction. This visualisation "
        "shows the trade-off; it does not establish a universally "
        "optimal algorithm."
    )

    with st.expander("View combined trade-off dataset"):

        st.dataframe(
            tradeoff,
            use_container_width=True,
            hide_index=True
        )




# --------------------------------------------------
# NODE-WISE PERFORMANCE ANALYSIS
# --------------------------------------------------

st.divider()

st.title("🔬 Node-wise Performance Analysis")

st.markdown("""
This section examines algorithm performance across individual sensor
nodes. It helps determine whether aggregate improvements are consistent
across the selected nodes or concentrated in particular nodes.

All energy values are model-based estimates, not physical measurements.
""")

import plotly.express as px

node_accuracy = metrics["node_accuracy"].copy()
node_freshness = metrics["node_freshness"].copy()
node_energy = metrics["node_energy"].copy()

# Consistent node ordering
node_order = sorted(
    node_energy["Node"].unique(),
    key=lambda x: int(x)
)

for df in [node_accuracy, node_freshness, node_energy]:
    df["Node"] = df["Node"].astype(str)

node_order = [str(n) for n in node_order]


# --------------------------------------------------
# ANALYSIS TABS
# --------------------------------------------------

node_tab1, node_tab2, node_tab3, node_tab4 = st.tabs([
    "📡 Communication & Energy",
    "🎯 Reconstruction Accuracy",
    "⏱️ Data Freshness",
    "📈 H120 Consistency"
])


# ==================================================
# TAB 1 — COMMUNICATION & ENERGY
# ==================================================

with node_tab1:

    st.subheader("Node-wise Transmission and Energy Comparison")

    selected_node_algorithm = st.selectbox(
        "Select algorithm",
        sorted(node_energy["Algorithm"].unique()),
        key="node_energy_algorithm"
    )

    selected_node_data = node_energy[
        node_energy["Algorithm"] == selected_node_algorithm
    ].copy()

    selected_node_data["Node"] = pd.Categorical(
        selected_node_data["Node"],
        categories=node_order,
        ordered=True
    )

    col1, col2 = st.columns(2)

    with col1:

        fig_node_tx = px.bar(
            selected_node_data.sort_values("Node"),
            x="Node",
            y="Transmissions",
            text_auto=True,
            title=f"Transmissions per Node — {selected_node_algorithm}",
            labels={
                "Node": "Sensor Node",
                "Transmissions": "Transmission Count"
            }
        )

        fig_node_tx.update_layout(
            template="plotly_dark",
            height=430
        )

        st.plotly_chart(
            fig_node_tx,
            use_container_width=True
        )

    with col2:

        fig_node_energy = px.bar(
            selected_node_data.sort_values("Node"),
            x="Node",
            y="Estimated_Energy_J",
            text_auto=".2f",
            title=f"Estimated Energy per Node — {selected_node_algorithm}",
            labels={
                "Node": "Sensor Node",
                "Estimated_Energy_J": "Estimated Energy (J)"
            }
        )

        fig_node_energy.update_layout(
            template="plotly_dark",
            height=430
        )

        st.plotly_chart(
            fig_node_energy,
            use_container_width=True
        )

    st.caption(
        "Energy includes estimated sensing, processing, and transmission "
        "costs under the configured energy model."
    )

    with st.expander("View node-wise communication and energy data"):

        st.dataframe(
            selected_node_data.sort_values("Node"),
            use_container_width=True,
            hide_index=True
        )


# ==================================================
# TAB 2 — RECONSTRUCTION ACCURACY
# ==================================================

with node_tab2:

    st.subheader("Reconstruction Accuracy Across Sensor Nodes")

    accuracy_col1, accuracy_col2 = st.columns(2)

    with accuracy_col1:

        selected_accuracy_sensor = st.selectbox(
            "Select sensor",
            ["Temperature", "Humidity", "Light"],
            key="node_accuracy_sensor"
        )

    with accuracy_col2:

        selected_accuracy_metric = st.selectbox(
            "Select accuracy metric",
            ["MAE", "RMSE"],
            key="node_accuracy_metric"
        )

    accuracy_filtered = node_accuracy[
        node_accuracy["Sensor"] == selected_accuracy_sensor
    ].copy()

    accuracy_pivot = accuracy_filtered.pivot(
        index="Algorithm",
        columns="Node",
        values=selected_accuracy_metric
    )

    accuracy_pivot = accuracy_pivot.reindex(
        columns=node_order
    )

    fig_accuracy_heatmap = px.imshow(
        accuracy_pivot,
        text_auto=".5f",
        aspect="auto",
        color_continuous_scale="Viridis",
        labels={
            "x": "Sensor Node",
            "y": "Algorithm",
            "color": selected_accuracy_metric
        },
        title=(
            f"{selected_accuracy_metric} Across Nodes — "
            f"{selected_accuracy_sensor.title()}"
        )
    )

    fig_accuracy_heatmap.update_layout(
        template="plotly_dark",
        height=480
    )

    st.plotly_chart(
        fig_accuracy_heatmap,
        use_container_width=True
    )

    st.caption(
        "Lower MAE and RMSE indicate lower reconstruction error. "
        "Compare algorithms within each node; sensor units differ."
    )

    with st.expander("View detailed node-wise accuracy metrics"):

        st.dataframe(
            accuracy_filtered.sort_values(
                ["Algorithm", "Node"]
            ),
            use_container_width=True,
            hide_index=True
        )


# ==================================================
# TAB 3 — DATA FRESHNESS
# ==================================================

with node_tab3:

    st.subheader("Data Freshness Across Sensor Nodes")

    freshness_metric = st.radio(
        "Select freshness metric",
        [
            "Mean_Age_sec",
            "Median_Age_sec",
            "P95_Age_sec",
            "Max_Age_sec"
        ],
        horizontal=True,
        format_func=lambda x: x.replace("_", " ").replace("sec", "(s)"),
        key="node_freshness_metric"
    )

    freshness_plot_data = node_freshness.copy()

    freshness_plot_data["Node"] = pd.Categorical(
        freshness_plot_data["Node"],
        categories=node_order,
        ordered=True
    )

    fig_node_freshness = px.bar(
        freshness_plot_data.sort_values("Node"),
        x="Node",
        y=freshness_metric,
        color="Algorithm",
        barmode="group",
        title=(
            f"{freshness_metric.replace('_', ' ')} "
            "Across Sensor Nodes"
        ),
        labels={
            "Node": "Sensor Node",
            freshness_metric: "Data Age (seconds)"
        }
    )

    fig_node_freshness.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(
        fig_node_freshness,
        use_container_width=True
    )

    st.caption(
        "Data age measures how old the most recently transmitted "
        "reading is at each source observation time. Lower values "
        "indicate fresher data."
    )

    with st.expander("View detailed node-wise freshness metrics"):

        st.dataframe(
            node_freshness.sort_values(
                ["Algorithm", "Node"]
            ),
            use_container_width=True,
            hide_index=True
        )


# ==================================================
# TAB 4 — H120 CONSISTENCY
# ==================================================

with node_tab4:

    st.subheader("Threshold-H120: Node-wise Consistency")

    fixed_energy = node_energy[
        node_energy["Algorithm"] == "Fixed"
    ][["Node", "Estimated_Energy_J"]].rename(
        columns={
            "Estimated_Energy_J": "Fixed_Energy_J"
        }
    )

    h120_energy = node_energy[
        node_energy["Algorithm"] == "Threshold-H120"
    ][["Node", "Estimated_Energy_J", "Transmissions"]].rename(
        columns={
            "Estimated_Energy_J": "H120_Energy_J",
            "Transmissions": "H120_Transmissions"
        }
    )

    h120_comparison = fixed_energy.merge(
        h120_energy,
        on="Node",
        how="inner"
    )

    h120_comparison["Energy_Savings_Percent"] = (
        (
            h120_comparison["Fixed_Energy_J"]
            - h120_comparison["H120_Energy_J"]
        )
        / h120_comparison["Fixed_Energy_J"]
    ) * 100

    h120_comparison["Node"] = pd.Categorical(
        h120_comparison["Node"],
        categories=node_order,
        ordered=True
    )

    h120_comparison = h120_comparison.sort_values("Node")

    avg_h120_savings = h120_comparison[
        "Energy_Savings_Percent"
    ].mean()

    min_h120_savings = h120_comparison[
        "Energy_Savings_Percent"
    ].min()

    max_h120_savings = h120_comparison[
        "Energy_Savings_Percent"
    ].max()

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Average node energy savings",
        f"{avg_h120_savings:.2f}%"
    )

    metric2.metric(
        "Lowest node savings",
        f"{min_h120_savings:.2f}%"
    )

    metric3.metric(
        "Highest node savings",
        f"{max_h120_savings:.2f}%"
    )

    fig_h120_savings = px.bar(
        h120_comparison,
        x="Node",
        y="Energy_Savings_Percent",
        text_auto=".2f",
        title="Threshold-H120 Estimated Energy Savings per Node",
        labels={
            "Node": "Sensor Node",
            "Energy_Savings_Percent": "Energy Savings (%)"
        }
    )

    fig_h120_savings.update_layout(
        template="plotly_dark",
        height=430
    )

    st.plotly_chart(
        fig_h120_savings,
        use_container_width=True
    )

    st.markdown("""
    **Interpretation:** This comparison evaluates whether the estimated
    energy savings of Threshold-H120 are distributed consistently
    across the five selected nodes. It does not establish that the
    same performance will occur on other datasets or physical networks.
    """)

    with st.expander("View H120 versus Fixed node-wise comparison"):

        st.dataframe(
            h120_comparison,
            use_container_width=True,
            hide_index=True
        )



# --------------------------------------------------

# --------------------------------------------------
# EXPERIMENT DESIGN AND METHODOLOGY
# --------------------------------------------------

st.divider()

st.title("🔬 Experiment Design & Methodology")

st.markdown("""
This section documents the dataset, experimental procedure, algorithm
configurations, evaluation metrics, energy assumptions and limitations
underlying the dashboard results.
""")

with st.expander("1. Dataset and Study Scope", expanded=True):

    st.markdown("""
    **Dataset:** Intel Berkeley Research Lab Wireless Sensor Network dataset.

    **Data source:** [Intel Berkeley Research Lab Dataset](https://db.csail.mit.edu/labdata/labdata.html)

    **Selected sensor nodes:** 22, 31, 45, 47 and 48.

    **Study period:**
    - Start: 28 February 2004, 01:06:46
    - End: 24 March 2004, 05:57:47

    **Selected records:** 272,278.

    The dataset contains historical sensor measurements, including
    temperature, humidity, light and voltage. The experiments replay
    these observations chronologically and evaluate simulated
    transmission decisions.
    """)

with st.expander("2. Data Preprocessing and Quality Control"):

    st.markdown("""
    The following provisional validity boundaries were applied:

    | Parameter | Validity condition |
    |---|---|
    | Temperature | -10°C to 50°C |
    | Humidity | 0% to 100% |
    | Light | Greater than or equal to 0 |
    | Voltage | 1.8V to 3.3V |

    Invalid sensor values were treated as missing for the corresponding
    measurement. The original raw dataset was preserved separately.

    Environmental eligibility was determined using valid temperature,
    humidity and light measurements.

    Voltage was retained for monitoring and quality analysis.
    """)

with st.expander("3. Experimental Design and Data Partitioning"):

    st.markdown("""
    A chronological partition was used to prevent future evaluation
    observations from influencing calibration.

    | Partition | Records |
    |---|---:|
    | Calibration | 61,680 |
    | Evaluation | 210,598 |
    | Eligible evaluation observations | 209,275 |

    **Calibration end:** 4 March 2004, approximately 02:04:58.

    Calibration observations were used to derive node-specific
    environmental change thresholds and rate thresholds.

    **Outage segmentation:**
    - A gap greater than 300 seconds between consecutive observations
      for a node defines a new operational segment.
    - Each segment begins with a mandatory transmission of its first
      valid environmental observation.
    - Reconstruction is restricted to the same node and segment.

    The 300-second boundary is an experimental segmentation rule,
    not a claim about the dataset's original outage definition.
    """)

with st.expander("4. Adaptive Transmission Algorithms"):

    st.markdown("""
    Five transmission strategies were evaluated.

    **Fixed**
    - Uses a fixed transmission interval of 60 seconds.

    **Rate**
    - Uses node-specific calibration thresholds based on the
      90th and 95th percentiles of observed change rates.
    - Low activity: 90-second interval.
    - Medium activity: 60-second interval.
    - High activity: 30-second interval.

    **Threshold**
    - Transmits when at least one valid environmental measurement
      changes by an amount greater than or equal to its calibrated
      node-specific threshold.
    - Does not impose the additional maximum-hold interval used
      by the H120 and H180 variants.

    **Threshold-H120**
    - Uses threshold-based transmission decisions with a
      120-second maximum hold interval.

    **Threshold-H180**
    - Uses threshold-based transmission decisions with a
      180-second maximum hold interval.

    The threshold values are derived from calibration observations.
    The first valid observation of each operational segment is
    transmitted by every algorithm.
    """)

with st.expander("5. Energy Consumption Model"):

    st.markdown("""
    Energy consumption is estimated using the following assumed costs:

    | Operation | Assumed energy |
    |---|---:|
    | Sensing per eligible observation | 0.5 mJ |
    | Processing per eligible observation | 0.2 mJ |
    | Transmission per packet | 50 mJ |

    **Calculation:**

    Estimated total energy is calculated as:

    `E_total = E_sensing + E_processing + E_transmission`

    Sensing and processing costs are charged for every eligible
    evaluation observation across all algorithms.

    Transmission energy varies according to the number of transmitted
    packets.

    These are model assumptions, not measurements from physical
    hardware. Consequently, the results represent estimated energy
    consumption rather than experimentally measured battery savings.
    """)

with st.expander("6. Evaluation Metrics"):

    st.markdown("""
    **Communication efficiency**
    - Transmission count: number of simulated transmitted packets.
    - Transmission reduction: percentage reduction relative to
      the eligible source observations.

    **Reconstruction accuracy**
    - Mean Absolute Error (MAE).
    - Root Mean Squared Error (RMSE).
    - Reconstruction uses segment-aware,
      last-observation-carried-forward (LOCF).

    **Data freshness**
    - Age of the most recently transmitted observation at each
      source observation time.
    - Mean, median, 95th percentile and maximum age.

    **Estimated energy**
    - Sensing, processing and transmission energy.
    - Estimated energy savings relative to the Fixed algorithm.

    All algorithms are evaluated against the same chronological
    evaluation observations.
    """)

with st.expander("7. Experimental Limitations and Interpretation"):

    st.warning("""
    **Important research limitations**
    """)

    st.markdown("""
    1. The experiments use historical Intel Berkeley sensor data,
       not a currently deployed physical sensor network.

    2. Transmission decisions are simulated. Actual radio transmission,
       packet loss, interference and network reliability were not
       experimentally measured.

    3. Energy costs are assumed model parameters. Actual hardware
       consumption depends on the microcontroller, radio, sensor,
       operating state and communication environment.

    4. Historical voltage readings are not treated as direct evidence
       of battery depletion or battery lifetime.

    5. Reconstruction coverage does not independently establish
       acceptable data freshness. Both accuracy and freshness must
       be considered.

    6. The 300-second outage segmentation threshold and data-quality
       boundaries are experimental choices.

    7. Threshold-H120 performs best among the configurations tested
       in this dataset. This does not establish that it is universally
       optimal for every sensor network or deployment environment.

    **Overall scope:** This work evaluates energy-aware adaptive
    transmission strategies through historical dataset replay and
    model-based energy estimation. Physical deployment validation
    remains future work.
    """)

# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Adaptive IoT | Energy-Aware Adaptive Sensor Network"
)

st.caption(
    "Dataset: Intel Berkeley Research Lab Wireless Sensor Network"
)

st.caption(
    "Research prototype | Historical dataset replay"
)
