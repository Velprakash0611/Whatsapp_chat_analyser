import os
import io
import streamlit as st
import pandas as pd
import preprocess
import helper

# Page Configuration
st.set_page_config(
    page_title="WhatsApp Chat Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar: Theme Toggle
st.sidebar.markdown("### Display Settings")
theme_mode = st.sidebar.radio(
    "Interface Theme",
    options=["Dark Mode", "Light Mode"],
    index=0,
    horizontal=True
)
is_dark = (theme_mode == "Dark Mode")

# CSS Variables and Animations
if is_dark:
    bg_main = "#0b0f19"
    bg_sidebar = "#111827"
    card_bg = "#1f2937"
    border_color = "#374151"
    text_primary = "#f9fafb"
    text_secondary = "#9ca3af"
    accent_color = "#38bdf8"
    accent_hover = "#0284c7"
else:
    bg_main = "#f8fafc"
    bg_sidebar = "#ffffff"
    card_bg = "#ffffff"
    border_color = "#e2e8f0"
    text_primary = "#0f172a"
    text_secondary = "#64748b"
    accent_color = "#2563eb"
    accent_hover = "#1d4ed8"

custom_css = f"""
<style>
    /* Main Layout */
    .stApp {{
        background-color: {bg_main};
        color: {text_primary};
        transition: background-color 0.4s ease, color 0.4s ease;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {bg_sidebar};
        border-right: 1px solid {border_color};
    }}

    /* Fade-in Animation */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(12px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    /* Keyframe Shimmer */
    @keyframes shimmer {{
        0% {{ border-color: {border_color}; }}
        50% {{ border-color: {accent_color}; }}
        100% {{ border-color: {border_color}; }}
    }}

    /* Card Styling */
    .custom-card {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        animation: fadeInUp 0.4s ease-out;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }}

    .custom-card:hover {{
        transform: translateY(-3px);
        border-color: {accent_color};
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.09);
    }}

    .card-title {{
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {text_secondary};
        margin-bottom: 6px;
    }}

    .card-value {{
        font-size: 1.85rem;
        font-weight: 700;
        color: {text_primary};
        line-height: 1.2;
    }}

    /* Button Styling */
    .stButton > button {{
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.55rem 1rem;
        transition: all 0.25s ease;
        border: 1px solid {border_color};
    }}

    .stButton > button:hover {{
        border-color: {accent_color};
        color: {accent_color};
        transform: translateY(-1px);
    }}

    /* Header styling */
    .main-title {{
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: {text_primary};
        margin-bottom: 0.3rem;
        animation: fadeInUp 0.3s ease-out;
    }}

    .sub-title {{
        font-size: 0.95rem;
        color: {text_secondary};
        margin-bottom: 1.5rem;
        animation: fadeInUp 0.4s ease-out;
    }}

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.2s ease;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Application Header
st.markdown('<div class="main-title">WhatsApp Chat Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Advanced behavioral, temporal, and sentiment analysis for exported conversations</div>', unsafe_allow_html=True)

# Caching Preprocessing Function
@st.cache_data(show_spinner="Parsing and structuring conversation data...")
def load_and_preprocess(raw_text: str):
    return preprocess.preprocess(raw_text)

# Sidebar: File Upload and Data Source
st.sidebar.markdown("### Conversation Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload exported chat file (.txt)",
    type=["txt"],
    help="Export chat from WhatsApp without media, then upload the generated .txt file."
)

sample_file_path = os.path.join(os.path.dirname(__file__), "MSEC AI&DS-4th-YEAR-2021-2025.txt")
load_sample = False

if os.path.exists(sample_file_path):
    if st.sidebar.button("Load Sample Conversation"):
        st.session_state["use_sample"] = True
        st.session_state["uploaded_filename"] = "MSEC AI&DS-4th-YEAR-2021-2025.txt"

if uploaded_file is not None:
    st.session_state["use_sample"] = False
    st.session_state["uploaded_filename"] = uploaded_file.name

# Load Raw Content
raw_data = None
if uploaded_file is not None and not st.session_state.get("use_sample", False):
    bytes_data = uploaded_file.getvalue()
    raw_data = bytes_data.decode("utf-8", errors="ignore")
elif st.session_state.get("use_sample", False) and os.path.exists(sample_file_path):
    with open(sample_file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_data = f.read()

# Main Logic when data is loaded
if raw_data:
    df = load_and_preprocess(raw_data)

    if df.empty:
        st.error("Could not parse conversation timestamps. Please ensure the file is a valid exported WhatsApp chat.")
        st.stop()

    # User Selection in Sidebar
    unique_users = [u for u in df['user'].unique() if u != 'Group_notification']
    unique_users.sort()
    user_options = ['All Chats'] + unique_users

    st.sidebar.markdown("### Filters")
    selected_user = st.sidebar.selectbox("Select Participant", user_options)

    # Date Range Filter
    min_date = df['only_date'].min()
    max_date = df['only_date'].max()

    date_range = st.sidebar.date_input(
        "Date Interval",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filter dataframe by date range
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df[(df['only_date'] >= start_date) & (df['only_date'] <= end_date)].copy()
    else:
        df_filtered = df.copy()

    if df_filtered.empty:
        st.warning("No messages found within the selected date interval.")
        st.stop()

    # Calculate High-Level Metrics
    num_messages, words, num_media, links, active_days = helper.fetch_stats(selected_user, df_filtered)
    avg_words = round(words / num_messages, 1) if num_messages > 0 else 0

    # Render Metric Cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f"""
        <div class="custom-card">
            <div class="card-title">Total Messages</div>
            <div class="card-value">{num_messages:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="custom-card">
            <div class="card-title">Total Words</div>
            <div class="card-value">{words:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="custom-card">
            <div class="card-title">Media Items</div>
            <div class="card-value">{num_media:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="custom-card">
            <div class="card-title">Shared Links</div>
            <div class="card-value">{links:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="custom-card">
            <div class="card-title">Active Days</div>
            <div class="card-value">{active_days:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with c6:
        st.markdown(f"""
        <div class="custom-card">
            <div class="card-title">Avg Words / Msg</div>
            <div class="card-value">{avg_words}</div>
        </div>
        """, unsafe_allow_html=True)

    # Organized Tabbed Interface
    tab_timelines, tab_heatmaps, tab_users, tab_words, tab_emojis, tab_sentiment, tab_explorer = st.tabs([
        "Timelines",
        "Activity Heatmap",
        "Participants",
        "Vocabulary",
        "Emoji Usage",
        "Sentiment Analysis",
        "Message Explorer"
    ])

    # Tab 1: Timelines
    with tab_timelines:
        st.subheader("Temporal Trends")
        col_t1, col_t2 = st.columns(2)

        with col_t1:
            monthly_df = helper.monthly_timeline(selected_user, df_filtered)
            fig_month = helper.plot_monthly_timeline(monthly_df, is_dark=is_dark)
            if fig_month:
                st.plotly_chart(fig_month, use_container_width=True)
            else:
                st.info("Insufficient monthly data points.")

        with col_t2:
            daily_df = helper.daily_timeline(selected_user, df_filtered)
            fig_daily = helper.plot_daily_timeline(daily_df, is_dark=is_dark)
            if fig_daily:
                st.plotly_chart(fig_daily, use_container_width=True)
            else:
                st.info("Insufficient daily data points.")

        # Cumulative Growth Curve
        st.markdown("#### Cumulative Message Growth")
        fig_growth = helper.plot_cumulative_growth(selected_user, df_filtered, is_dark=is_dark)
        if fig_growth:
            st.plotly_chart(fig_growth, use_container_width=True)

    # Tab 2: Activity Heatmap & 3D Landscape
    with tab_heatmaps:
        st.subheader("Activity Distribution & Patterns")
        col_h1, col_h2 = st.columns([1, 2])

        with col_h1:
            week_df = helper.week_activity(selected_user, df_filtered)
            fig_week = helper.plot_week_activity(week_df, is_dark=is_dark)
            if fig_week:
                st.plotly_chart(fig_week, use_container_width=True)

        with col_h2:
            heatmap_pivot = helper.activity_heatmap(selected_user, df_filtered)
            fig_heatmap = helper.plot_activity_heatmap(heatmap_pivot, is_dark=is_dark)
            if fig_heatmap:
                st.plotly_chart(fig_heatmap, use_container_width=True)

        col_polar, col_3d_info = st.columns([1, 1])
        with col_polar:
            st.markdown("#### Circadian 24-Hour Clock")
            fig_polar = helper.plot_polar_hourly_activity(selected_user, df_filtered, is_dark=is_dark)
            if fig_polar:
                st.plotly_chart(fig_polar, use_container_width=True)

        with col_3d_info:
            st.markdown("#### 3D Activity Landscape Insights")
            st.markdown("""
            The 3D surface model below visualizes conversation intensity across:
            - **X-axis**: Hour of Day (00:00 to 23:00)
            - **Y-axis**: Day of the Week (Monday to Sunday)
            - **Z-axis**: Message Volume & Intensity

            **Interaction**: Click and drag to rotate in 360°, scroll to zoom in/out, or double-click to reset orientation.
            """)

        # 3D Activity Surface Plot
        st.markdown("#### 3D Conversational Volume Topology")
        fig_3d = helper.plot_3d_activity_surface(heatmap_pivot, is_dark=is_dark)
        if fig_3d:
            st.plotly_chart(fig_3d, use_container_width=True)

    # Tab 3: Participants
    with tab_users:
        if selected_user == 'All Chats':
            st.subheader("Participant Participation & Contribution")
            top_users, percent_df = helper.most_busy_users(df_filtered)

            col_u1, col_u2 = st.columns([3, 2])
            with col_u1:
                fig_users = helper.plot_busy_users(top_users, is_dark=is_dark)
                if fig_users:
                    st.plotly_chart(fig_users, use_container_width=True)
            with col_u2:
                st.markdown("#### Contribution Percentage")
                st.dataframe(
                    percent_df,
                    use_container_width=True,
                    height=360
                )

            # Participant Persona Bubble Matrix
            st.markdown("#### Participant Persona Matrix")
            fig_personas = helper.plot_participant_personas(df_filtered, is_dark=is_dark)
            if fig_personas:
                st.plotly_chart(fig_personas, use_container_width=True)
        else:
            st.info("Participant comparison and persona mapping are available when 'All Chats' is selected in the sidebar.")

    # Tab 4: Vocabulary & WordCloud
    with tab_words:
        st.subheader("Vocabulary & Word Frequency")
        col_w1, col_w2 = st.columns([3, 2])

        with col_w1:
            st.markdown("#### Word Cloud")
            wc_image = helper.create_wordcloud_image(selected_user, df_filtered, is_dark=is_dark)
            if wc_image:
                st.image(wc_image.to_image(), use_column_width=True)
            else:
                st.info("No significant text available for word cloud generation.")

        with col_w2:
            st.markdown("#### High-Frequency Words")
            common_words_df = helper.most_common_words(selected_user, df_filtered, top_n=15)
            fig_words = helper.plot_most_common_words(common_words_df, is_dark=is_dark)
            if fig_words:
                st.plotly_chart(fig_words, use_container_width=True)
            else:
                st.info("No frequent words identified.")

    # Tab 5: Emoji Usage
    with tab_emojis:
        st.subheader("Emoji Frequency & Statistics")
        emoji_df = helper.emoji_analyser(selected_user, df_filtered)

        if not emoji_df.empty:
            col_e1, col_e2 = st.columns([2, 3])
            with col_e1:
                st.markdown("#### Frequency Table")
                st.dataframe(emoji_df, use_container_width=True, height=380)
            with col_e2:
                fig_emoji = helper.plot_emoji_distribution(emoji_df, is_dark=is_dark, top_n=10)
                if fig_emoji:
                    st.plotly_chart(fig_emoji, use_container_width=True)
        else:
            st.info("No emojis detected in this conversation subset.")

    # Tab 6: Sentiment Analysis
    with tab_sentiment:
        st.subheader("Emotional Tone & Sentiment Polarity")
        summary_sent, scored_msgs = helper.sentiment_analysis(selected_user, df_filtered)

        if summary_sent is not None and not summary_sent.empty:
            col_s1, col_s2 = st.columns([2, 3])

            with col_s1:
                fig_donut = helper.plot_sentiment_donut(summary_sent, is_dark=is_dark)
                if fig_donut:
                    st.plotly_chart(fig_donut, use_container_width=True)

            with col_s2:
                st.markdown("#### Polarity Breakdown")
                st.dataframe(summary_sent, use_container_width=True, height=220)

                pos_pct = summary_sent[summary_sent['Sentiment'] == 'Positive']['Percentage'].values
                neg_pct = summary_sent[summary_sent['Sentiment'] == 'Negative']['Percentage'].values
                p_val = pos_pct[0] if len(pos_pct) > 0 else 0.0
                n_val = neg_pct[0] if len(neg_pct) > 0 else 0.0

                st.markdown(f"""
                <div class="custom-card" style="margin-top: 15px;">
                    <div class="card-title">Sentiment Ratio</div>
                    <div style="font-size: 1.1rem; font-weight: 600;">
                        Positive: {p_val}% | Negative: {n_val}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Sentiment Polarity Trendline
            st.markdown("#### Sentiment Trend Over Time")
            fig_sent_trend = helper.plot_sentiment_trend(scored_msgs, is_dark=is_dark)
            if fig_sent_trend:
                st.plotly_chart(fig_sent_trend, use_container_width=True)
        else:
            st.info("Sentiment analysis requires plain text messages.")

    # Tab 7: Message Explorer
    with tab_explorer:
        st.subheader("Search & Inspect Messages")
        search_query = st.text_input("Filter messages by keyword", placeholder="Type a word or phrase to search...")

        display_cols = ['date', 'user', 'message']
        filtered_view = helper.filter_user(df_filtered, selected_user)
        filtered_view = filtered_view[filtered_view['user'] != 'Group_notification']

        if search_query.strip():
            filtered_view = filtered_view[
                filtered_view['message'].str.contains(search_query, case=False, na=False)
            ]

        st.caption(f"Showing {len(filtered_view):,} matching messages")
        st.dataframe(filtered_view[display_cols], use_container_width=True, height=420)

        # CSV Download
        csv_buffer = io.StringIO()
        filtered_view[display_cols].to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download Filtered Messages as CSV",
            data=csv_buffer.getvalue(),
            file_name="whatsapp_chat_export.csv",
            mime="text/csv"
        )

else:
    # Empty State Hero Section
    st.markdown("""
    <div class="custom-card" style="text-align: center; padding: 60px 30px; margin-top: 30px;">
        <h2 style="font-weight: 700; margin-bottom: 12px;">Get Started with Chat Analysis</h2>
        <p style="max-width: 600px; margin: 0 auto 24px auto; font-size: 1.05rem; opacity: 0.85;">
            Upload an exported WhatsApp chat text file (.txt) using the sidebar, or click the button below to test immediately with the sample dataset.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        if st.button("Load Sample Conversation", key="hero_sample_btn"):
            st.session_state["use_sample"] = True
            st.rerun()
