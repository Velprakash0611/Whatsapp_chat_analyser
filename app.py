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

# Custom CSS leveraging Streamlit native theme variables
custom_css = """
<style>
    /* Keyframe Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(14px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.2); }
        70% { box-shadow: 0 0 0 10px rgba(37, 99, 235, 0); }
        100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
    }

    /* Modern Card Container */
    .custom-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 14px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        animation: fadeInUp 0.4s ease-out;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }

    .custom-card:hover {
        transform: translateY(-3px);
        border-color: var(--primary-color);
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
    }

    .card-title {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.75;
        margin-bottom: 6px;
    }

    .card-value {
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.2;
    }

    /* Hero Styling */
    .hero-badge {
        display: inline-block;
        padding: 5px 14px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        border-radius: 20px;
        background-color: rgba(37, 99, 235, 0.12);
        color: var(--primary-color);
        margin-bottom: 12px;
        border: 1px solid rgba(37, 99, 235, 0.25);
    }

    .hero-title {
        font-size: 2.35rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.15;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        opacity: 0.82;
        max-width: 780px;
        margin-bottom: 24px;
        line-height: 1.55;
    }

    /* Feature Grid Card */
    .feature-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.16);
        border-radius: 12px;
        padding: 20px 22px;
        height: 100%;
        animation: fadeInUp 0.5s ease-out;
        transition: transform 0.25s ease, border-color 0.25s ease;
    }

    .feature-card:hover {
        transform: translateY(-2px);
        border-color: var(--primary-color);
    }

    .feature-tag {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--primary-color);
        margin-bottom: 6px;
    }

    .feature-heading {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .feature-desc {
        font-size: 0.88rem;
        opacity: 0.8;
        line-height: 1.5;
    }

    /* Workflow Step */
    .step-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: var(--primary-color);
        color: #ffffff;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 10px;
    }

    /* General Button Polish */
    .stButton > button {
        border-radius: 9px;
        font-weight: 600;
        padding: 0.55rem 1.1rem;
        transition: all 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }

    /* Tab Polish */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Caching Preprocessing Function
@st.cache_data(show_spinner="Parsing and structuring conversation data...")
def load_and_preprocess(raw_text: str):
    return preprocess.preprocess(raw_text)

# Sidebar: File Upload and Data Source
st.sidebar.markdown("### Conversation Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload chat export (.txt)",
    type=["txt"],
    help="Export chat from WhatsApp without media, then select the resulting .txt file."
)

# Load Raw Content
raw_data = None
active_file = uploaded_file or st.session_state.get("main_page_uploader")
if active_file is not None:
    bytes_data = active_file.getvalue()
    raw_data = bytes_data.decode("utf-8", errors="ignore")

# Main Flow
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

    # Application Header
    st.markdown('<div class="hero-title">WhatsApp Chat Intelligence</div>', unsafe_allow_html=True)
    active_label = f"Displaying records for: **{selected_user}**"
    date_label = f"({min_date.strftime('%b %d, %Y')} to {max_date.strftime('%b %d, %Y')})"
    st.caption(f"{active_label} {date_label}")

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
        "Activity Heatmap & 3D",
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
            fig_month = helper.plot_monthly_timeline(monthly_df)
            if fig_month:
                st.plotly_chart(fig_month, use_container_width=True)
            else:
                st.info("Insufficient monthly data points.")

        with col_t2:
            daily_df = helper.daily_timeline(selected_user, df_filtered)
            fig_daily = helper.plot_daily_timeline(daily_df)
            if fig_daily:
                st.plotly_chart(fig_daily, use_container_width=True)
            else:
                st.info("Insufficient daily data points.")

        # Cumulative Growth Curve
        st.markdown("#### Cumulative Message Growth")
        fig_growth = helper.plot_cumulative_growth(selected_user, df_filtered)
        if fig_growth:
            st.plotly_chart(fig_growth, use_container_width=True)

    # Tab 2: Activity Heatmap & 3D Landscape
    with tab_heatmaps:
        st.subheader("Activity Distribution & Temporal Rhythms")
        col_h1, col_h2 = st.columns([1, 2])

        with col_h1:
            week_df = helper.week_activity(selected_user, df_filtered)
            fig_week = helper.plot_week_activity(week_df)
            if fig_week:
                st.plotly_chart(fig_week, use_container_width=True)

        with col_h2:
            heatmap_pivot = helper.activity_heatmap(selected_user, df_filtered)
            fig_heatmap = helper.plot_activity_heatmap(heatmap_pivot)
            if fig_heatmap:
                st.plotly_chart(fig_heatmap, use_container_width=True)

        col_polar, col_3d_info = st.columns([1, 1])
        with col_polar:
            st.markdown("#### Circadian 24-Hour Clock")
            fig_polar = helper.plot_polar_hourly_activity(selected_user, df_filtered)
            if fig_polar:
                st.plotly_chart(fig_polar, use_container_width=True)

        with col_3d_info:
            st.markdown("#### 3D Activity Landscape Insights")
            st.markdown("""
            The 3D surface model below visualizes conversational concentration across:
            - **X-axis**: Hour of Day (00:00 to 23:00)
            - **Y-axis**: Day of the Week (Monday to Sunday)
            - **Z-axis**: Message Volume Density

            **Interactive Controls**: Click and drag to rotate in 360 degrees, scroll to zoom in/out, or double-click to reset the camera perspective.
            """)

        # 3D Activity Surface Plot
        st.markdown("#### 3D Conversational Volume Topology")
        fig_3d = helper.plot_3d_activity_surface(heatmap_pivot)
        if fig_3d:
            st.plotly_chart(fig_3d, use_container_width=True)

    # Tab 3: Participants
    with tab_users:
        if selected_user == 'All Chats':
            st.subheader("Participant Participation & Contribution")
            top_users, percent_df = helper.most_busy_users(df_filtered)

            col_u1, col_u2 = st.columns([3, 2])
            with col_u1:
                fig_users = helper.plot_busy_users(top_users)
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
            fig_personas = helper.plot_participant_personas(df_filtered)
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
            wc_image = helper.create_wordcloud_image(selected_user, df_filtered)
            if wc_image:
                st.image(wc_image.to_image(), use_container_width=True)
            else:
                st.info("No significant text available for word cloud generation.")

        with col_w2:
            st.markdown("#### High-Frequency Words")
            common_words_df = helper.most_common_words(selected_user, df_filtered, top_n=15)
            fig_words = helper.plot_most_common_words(common_words_df)
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
                fig_emoji = helper.plot_emoji_distribution(emoji_df, top_n=10)
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
                fig_donut = helper.plot_sentiment_donut(summary_sent)
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
            fig_sent_trend = helper.plot_sentiment_trend(scored_msgs)
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
    # Rich Modern Landing Experience
    st.markdown("""
    <div style="text-align: center; padding: 25px 15px 35px 15px;">
        <span class="hero-badge">Conversational Intelligence Platform</span>
        <div class="hero-title">Turn WhatsApp Chat Logs into Deep Analytics</div>
        <div class="hero-subtitle" style="margin: 0 auto 30px auto;">
            Uncover behavioral patterns, 24-hour circadian rhythms, 3D conversational volume topologies,
            sentiment shifts, and participant personas in minutes.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Centered Main Upload Hub
    col_l, col_center, col_r = st.columns([1, 4, 1])
    with col_center:
        st.markdown("""
        <div class="custom-card" style="text-align: center; padding: 30px 24px 18px 24px;">
            <div class="card-title">Conversation Ingestion</div>
            <h3 style="font-size: 1.4rem; font-weight: 700; margin-bottom: 8px;">Upload Your WhatsApp Chat Log</h3>
            <p style="font-size: 0.94rem; opacity: 0.82; max-width: 600px; margin: 0 auto 16px auto; line-height: 1.5;">
                Select or drag and drop your exported <code>.txt</code> file here. Supports both 12-hour and 24-hour Android formats and iOS square-bracket exports without media.
            </p>
        </div>
        """, unsafe_allow_html=True)
        main_upload = st.file_uploader(
            "Upload WhatsApp chat file (.txt)",
            type=["txt"],
            key="main_page_uploader",
            label_visibility="collapsed"
        )
        if main_upload is not None:
            st.rerun()

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # Core Analytical Capabilities Showcase Grid
    st.markdown("### Analytical Modules")
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-tag">Temporal & Spatial</div>
            <div class="feature-heading">3D Volume & Circadian Clock</div>
            <div class="feature-desc">
                Interactive 360° volume surface mapping Day vs. Hour, paired with a 24-hour circular polar clock revealing natural conversation rhythms.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-tag">Behavioral</div>
            <div class="feature-heading">Participant Persona Matrix</div>
            <div class="feature-desc">
                Multi-dimensional bubble chart mapping total activity against verbosity and media habits to identify conversational archetypes.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-tag">NLP & Emotion</div>
            <div class="feature-heading">VADER Sentiment Dynamics</div>
            <div class="feature-desc">
                Rule-based lexicon scoring classifying positive, neutral, and negative messages, with monthly emotional trajectory line charts.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with f4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-tag">Lexical & Search</div>
            <div class="feature-heading">Word Cloud & Live Explorer</div>
            <div class="feature-desc">
                Stopword-filtered vocabulary rankings, top emoji frequencies, real-time message keyword search, and CSV export.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

    # Workflow Steps
    st.markdown("### How to Export Your WhatsApp Chat")
    s1, s2, s3 = st.columns(3)

    with s1:
        st.markdown("""
        <div class="custom-card">
            <div class="step-badge">1</div>
            <h4 style="font-weight: 700; margin-bottom: 6px;">Open WhatsApp</h4>
            <p style="font-size: 0.88rem; opacity: 0.8; line-height: 1.45;">
                Open any private or group conversation on your phone. Tap the <strong>three dots</strong> (Android) or the <strong>contact name</strong> (iOS).
            </p>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown("""
        <div class="custom-card">
            <div class="step-badge">2</div>
            <h4 style="font-weight: 700; margin-bottom: 6px;">Export Without Media</h4>
            <p style="font-size: 0.88rem; opacity: 0.8; line-height: 1.45;">
                Select <strong>More -> Export chat</strong>. Choose <strong>Without Media</strong> to generate a compact, clean <code>.txt</code> file.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with s3:
        st.markdown("""
        <div class="custom-card">
            <div class="step-badge">3</div>
            <h4 style="font-weight: 700; margin-bottom: 6px;">Upload & Analyze</h4>
            <p style="font-size: 0.88rem; opacity: 0.8; line-height: 1.45;">
                Upload the exported <code>.txt</code> file here or via the sidebar to instantly generate full interactive intelligence reports.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Privacy Assurance Banner
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; padding: 18px 24px; border-radius: 12px; background-color: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.15);">
        <span style="font-weight: 600; font-size: 0.92rem;">Local Processing Guarantee:</span>
        <span style="font-size: 0.9rem; opacity: 0.85;"> Your chat data never leaves your computer. All parsing, sentiment scoring, and charting occur strictly on your local machine.</span>
    </div>
    """, unsafe_allow_html=True)
