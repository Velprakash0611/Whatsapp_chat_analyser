import os
import re
from collections import Counter
import pandas as pd
import numpy as np
import emoji
from urlextract import URLExtract
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
import nltk

extract = URLExtract()

# Ensure VADER lexicon is available for sentiment analysis
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    try:
        sia = SentimentIntensityAnalyzer()
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
        sia = SentimentIntensityAnalyzer()
except Exception:
    sia = None


def load_stopwords():
    """Loads stopwords using relative path to avoid machine-specific errors."""
    stop_words = set()
    file_path = os.path.join(os.path.dirname(__file__), 'stop_hinglish.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            stop_words = set(f.read().split())

    # Add common general stopwords
    common_stops = {
        'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'in', 'to', 'for', 'of',
        'with', 'it', 'this', 'that', 'you', 'i', 'we', 'they', 'he', 'she', 'me', 'my',
        'your', 'our', 'their', 'was', 'were', 'be', 'been', 'are', 'have', 'has', 'had',
        'do', 'does', 'did', 'but', 'so', 'if', 'from', 'by', 'as', 'up', 'down', 'in', 'out',
        'media', 'omitted', 'message', 'deleted', 'pm', 'am', 'https', 'http', 'www', 'com'
    }
    stop_words.update(common_stops)
    return stop_words


def filter_user(df: pd.DataFrame, sel_user: str) -> pd.DataFrame:
    """Filters dataframe by selected user or returns full conversation."""
    if sel_user != 'All Chats':
        return df[df['user'] == sel_user].copy()
    return df.copy()


def fetch_stats(sel_user: str, df: pd.DataFrame):
    """Calculates high-level conversation metrics."""
    filtered_df = filter_user(df, sel_user)
    # Exclude system notifications for accurate user-level counts
    user_msgs_df = filtered_df[filtered_df['user'] != 'Group_notification']

    num_messages = user_msgs_df.shape[0]

    # Count words excluding media omitted messages
    content_msgs = user_msgs_df[~user_msgs_df['is_media'] & ~user_msgs_df['is_deleted']]
    words = sum(len(msg.split()) for msg in content_msgs['message'])

    # Total media messages
    num_media_msg = int(user_msgs_df['is_media'].sum())

    # Total links shared
    total_links = 0
    for msg in user_msgs_df['message']:
        total_links += len(extract.find_urls(msg))

    # Active days
    num_active_days = user_msgs_df['only_date'].nunique() if not user_msgs_df.empty else 0

    return num_messages, words, num_media_msg, total_links, num_active_days


def most_busy_users(df: pd.DataFrame, top_n: int = 8):
    """Returns top active users and overall contribution percentage."""
    clean_df = df[df['user'] != 'Group_notification']
    if clean_df.empty:
        return pd.DataFrame(columns=['user', 'count']), pd.DataFrame(columns=['name', 'percent'])

    user_counts = clean_df['user'].value_counts()
    top_users_df = user_counts.head(top_n).reset_index()
    top_users_df.columns = ['user', 'count']

    percent_df = round((user_counts / clean_df.shape[0]) * 100, 2).reset_index()
    percent_df.columns = ['name', 'percent']

    return top_users_df, percent_df


def plot_busy_users(top_users_df: pd.DataFrame, is_dark: bool = False):
    """Creates a responsive Plotly horizontal bar chart for top contributors."""
    if top_users_df.empty:
        return None

    template = "plotly_dark" if is_dark else "plotly_white"
    fig = px.bar(
        top_users_df,
        x='count',
        y='user',
        orientation='h',
        labels={'count': 'Messages', 'user': 'Participant'},
        title='Most Active Participants',
        color='count',
        color_continuous_scale='Teal' if is_dark else 'Blues',
        template=template
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380
    )
    return fig


def monthly_timeline(sel_user: str, df: pd.DataFrame):
    """Aggregates messages per month chronologically."""
    filtered_df = filter_user(df, sel_user)
    clean_df = filtered_df[filtered_df['user'] != 'Group_notification']
    if clean_df.empty:
        return pd.DataFrame()

    timeline = clean_df.groupby(['year', 'month_num', 'month']).size().reset_index(name='message_count')
    timeline = timeline.sort_values(by=['year', 'month_num'])
    timeline['time'] = timeline['month'] + ' ' + timeline['year'].astype(str)
    return timeline


def plot_monthly_timeline(timeline: pd.DataFrame, is_dark: bool = False):
    """Interactive monthly message volume chart."""
    if timeline.empty:
        return None

    template = "plotly_dark" if is_dark else "plotly_white"
    line_color = '#38bdf8' if is_dark else '#2563eb'

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timeline['time'],
        y=timeline['message_count'],
        mode='lines+markers',
        line=dict(color=line_color, width=2.5),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(56, 189, 248, 0.15)' if is_dark else 'rgba(37, 99, 235, 0.12)',
        name='Messages'
    ))
    fig.update_layout(
        title='Monthly Message Timeline',
        xaxis_title='Month',
        yaxis_title='Messages',
        template=template,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380
    )
    return fig


def daily_timeline(sel_user: str, df: pd.DataFrame):
    """Aggregates messages per single date."""
    filtered_df = filter_user(df, sel_user)
    clean_df = filtered_df[filtered_df['user'] != 'Group_notification']
    if clean_df.empty:
        return pd.DataFrame()

    daily = clean_df.groupby('only_date').size().reset_index(name='message_count')
    daily = daily.sort_values('only_date')
    return daily


def plot_daily_timeline(daily: pd.DataFrame, is_dark: bool = False):
    """Interactive daily message timeline chart."""
    if daily.empty:
        return None

    template = "plotly_dark" if is_dark else "plotly_white"
    color = '#10b981' if is_dark else '#059669'

    fig = px.line(
        daily,
        x='only_date',
        y='message_count',
        title='Daily Activity Timeline',
        labels={'only_date': 'Date', 'message_count': 'Messages'},
        template=template
    )
    fig.update_traces(line_color=color, line_width=1.8)
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380
    )
    return fig


def week_activity(sel_user: str, df: pd.DataFrame):
    """Returns activity aggregated across Monday through Sunday."""
    filtered_df = filter_user(df, sel_user)
    clean_df = filtered_df[filtered_df['user'] != 'Group_notification']
    if clean_df.empty:
        return pd.DataFrame()

    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    counts = clean_df['day_name'].value_counts()
    reindexed = counts.reindex(ordered_days, fill_value=0).reset_index()
    reindexed.columns = ['Day', 'Messages']
    return reindexed


def plot_week_activity(week_df: pd.DataFrame, is_dark: bool = False):
    """Plotly bar chart for day-of-week message counts."""
    if week_df.empty:
        return None

    template = "plotly_dark" if is_dark else "plotly_white"
    color = '#6366f1' if is_dark else '#4f46e5'

    fig = px.bar(
        week_df,
        x='Day',
        y='Messages',
        title='Activity by Day of Week',
        color='Messages',
        color_continuous_scale='Purples' if is_dark else 'Viridis',
        template=template
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=350
    )
    return fig


def activity_heatmap(sel_user: str, df: pd.DataFrame):
    """Builds a 7x24 pivot table matrix indexed Monday through Sunday."""
    filtered_df = filter_user(df, sel_user)
    clean_df = filtered_df[filtered_df['user'] != 'Group_notification']
    if clean_df.empty:
        return pd.DataFrame()

    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ordered_periods = [f"{h:02d}:00 - {(h + 1) % 24:02d}:00" for h in range(24)]

    pivot = clean_df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count',
        fill_value=0
    )

    pivot = pivot.reindex(index=ordered_days, columns=ordered_periods, fill_value=0)
    return pivot


def plot_activity_heatmap(pivot: pd.DataFrame, is_dark: bool = False):
    """Interactive weekly hourly heatmap."""
    if pivot.empty:
        return None

    template = "plotly_dark" if is_dark else "plotly_white"
    colorscale = 'Viridis' if is_dark else 'YlGnBu'

    fig = px.imshow(
        pivot,
        labels=dict(x="Time of Day", y="Day of Week", color="Messages"),
        x=pivot.columns,
        y=pivot.index,
        title="Weekly Hourly Heatmap",
        color_continuous_scale=colorscale,
        aspect="auto",
        template=template
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        xaxis=dict(tickangle=-45)
    )
    return fig


def create_wordcloud_image(sel_user: str, df: pd.DataFrame, is_dark: bool = False):
    """Generates WordCloud PIL image after filtering stopwords, links, and system notices."""
    filtered_df = filter_user(df, sel_user)
    clean_df = filtered_df[filtered_df['user'] != 'Group_notification']
    content_msgs = clean_df[~clean_df['is_media'] & ~clean_df['is_deleted']]

    if content_msgs.empty:
        return None

    stop_words = load_stopwords()

    cleaned_words = []
    for message in content_msgs['message']:
        # Remove URLs
        text_without_urls = re.sub(r'https?://\S+|www\.\S+', '', message)
        # Remove special characters and digits
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text_without_urls.lower())
        for w in words:
            if w not in stop_words:
                cleaned_words.append(w)

    if not cleaned_words:
        return None

    full_text = " ".join(cleaned_words)
    bg_color = "#0f172a" if is_dark else "#ffffff"
    colormap = "cool" if is_dark else "tab10"

    wc = WordCloud(
        width=800,
        height=450,
        min_font_size=10,
        background_color=bg_color,
        colormap=colormap,
        collocations=False
    )
    return wc.generate(full_text)


def most_common_words(sel_user: str, df: pd.DataFrame, top_n: int = 15):
    """Finds most frequent words excluding stopwords."""
    filtered_df = filter_user(df, sel_user)
    clean_df = filtered_df[filtered_df['user'] != 'Group_notification']
    content_msgs = clean_df[~clean_df['is_media'] & ~clean_df['is_deleted']]

    if content_msgs.empty:
        return pd.DataFrame(columns=['Word', 'Count'])

    stop_words = load_stopwords()
    words_list = []

    for message in content_msgs['message']:
        text_no_urls = re.sub(r'https?://\S+|www\.\S+', '', message)
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text_no_urls.lower())
        for token in tokens:
            if token not in stop_words:
                words_list.append(token)

    if not words_list:
        return pd.DataFrame(columns=['Word', 'Count'])

    counts = Counter(words_list).most_common(top_n)
    res_df = pd.DataFrame(counts, columns=['Word', 'Count'])
    return res_df


def plot_most_common_words(words_df: pd.DataFrame, is_dark: bool = False):
    """Interactive horizontal bar chart of top words."""
    if words_df.empty:
        return None

    template = "plotly_dark" if is_dark else "plotly_white"
    color = '#06b6d4' if is_dark else '#0891b2'

    fig = px.bar(
        words_df,
        x='Count',
        y='Word',
        orientation='h',
        title='Most Frequent Words',
        template=template
    )
    fig.update_traces(marker_color=color)
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=20, t=50, b=20),
        height=420
    )
    return fig


def emoji_analyser(sel_user: str, df: pd.DataFrame):
    """Extracts and counts emojis in chat messages."""
    filtered_df = filter_user(df, sel_user)
    clean_df = filtered_df[filtered_df['user'] != 'Group_notification']

    if clean_df.empty:
        return pd.DataFrame(columns=['Emoji', 'Count'])

    emojis = []
    for msg in clean_df['message']:
        emojis.extend([c for c in msg if emoji.is_emoji(c)])

    if not emojis:
        return pd.DataFrame(columns=['Emoji', 'Count'])

    counter = Counter(emojis)
    emoji_df = pd.DataFrame(counter.most_common(), columns=['Emoji', 'Count'])
    return emoji_df


def plot_emoji_distribution(emoji_df: pd.DataFrame, is_dark: bool = False, top_n: int = 8):
    """Creates top emoji horizontal bar chart."""
    if emoji_df.empty:
        return None

    sample = emoji_df.head(top_n)
    template = "plotly_dark" if is_dark else "plotly_white"

    fig = px.bar(
        sample,
        x='Count',
        y='Emoji',
        orientation='h',
        title=f'Top {top_n} Emojis Used',
        template=template,
        color='Count',
        color_continuous_scale='Sunset' if is_dark else 'Oranges'
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=20, t=50, b=20),
        height=380
    )
    return fig


def sentiment_analysis(sel_user: str, df: pd.DataFrame):
    """
    Computes sentiment polarity (Positive, Neutral, Negative) per message
    using VADER sentiment analysis.
    """
    if sia is None:
        return None, None

    filtered_df = filter_user(df, sel_user)
    clean_df = filtered_df[filtered_df['user'] != 'Group_notification'].copy()
    content_msgs = clean_df[~clean_df['is_media'] & ~clean_df['is_deleted']].copy()

    if content_msgs.empty:
        return None, None

    scores = []
    labels = []

    for msg in content_msgs['message']:
        polarity = sia.polarity_scores(msg)
        compound = polarity['compound']
        scores.append(compound)
        if compound >= 0.05:
            labels.append('Positive')
        elif compound <= -0.05:
            labels.append('Negative')
        else:
            labels.append('Neutral')

    content_msgs['sentiment_score'] = scores
    content_msgs['sentiment'] = labels

    summary = content_msgs['sentiment'].value_counts().reset_index()
    summary.columns = ['Sentiment', 'Count']
    summary['Percentage'] = round((summary['Count'] / summary['Count'].sum()) * 100, 1)

    return summary, content_msgs


def plot_sentiment_donut(summary_df: pd.DataFrame, is_dark: bool = False):
    """Interactive Donut chart for sentiment distribution."""
    if summary_df is None or summary_df.empty:
        return None

    template = "plotly_dark" if is_dark else "plotly_white"
    color_map = {
        'Positive': '#10b981',
        'Neutral': '#64748b',
        'Negative': '#ef4444'
    }

    colors = [color_map.get(s, '#94a3b8') for s in summary_df['Sentiment']]

    fig = go.Figure(data=[go.Pie(
        labels=summary_df['Sentiment'],
        values=summary_df['Count'],
        hole=.55,
        marker=dict(colors=colors),
        textinfo='label+percent',
        hoverinfo='label+value+percent'
    )])

    fig.update_layout(
        title='Sentiment Distribution',
        template=template,
        margin=dict(l=20, r=20, t=50, b=20),
        height=350,
        showlegend=True
    )
    return fig


def plot_3d_activity_surface(pivot: pd.DataFrame, is_dark: bool = False):
    """
    Renders an interactive 3D activity surface:
    X: Hours of Day (0 - 23)
    Y: Days of Week (Monday - Sunday)
    Z: Message Frequency Density
    """
    if pivot.empty:
        return None

    z_data = pivot.values
    x_hours = [f"{h:02d}:00" for h in range(24)]
    y_days = list(pivot.index)

    template = "plotly_dark" if is_dark else "plotly_white"
    colorscale = "Plasma" if is_dark else "Turbo"

    fig = go.Figure(data=[go.Surface(
        z=z_data,
        x=x_hours,
        y=y_days,
        colorscale=colorscale,
        contours_z=dict(
            show=True,
            usecolormap=True,
            highlightcolor="white" if is_dark else "black",
            project_z=True
        ),
        lighting=dict(ambient=0.6, diffuse=0.8, roughness=0.5, specular=0.2),
        hoverinfo='x+y+z'
    )])

    fig.update_layout(
        title="3D Conversational Activity Landscape (Day vs Hour vs Messages)",
        template=template,
        scene=dict(
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            zaxis_title="Message Count",
            camera=dict(
                eye=dict(x=-1.5, y=-1.5, z=1.2)
            ),
            xaxis=dict(tickangle=-30)
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=520
    )
    return fig


def plot_polar_hourly_activity(sel_user: str, df: pd.DataFrame, is_dark: bool = False):
    """
    Renders a 24-hour circular polar clock chart showing circadian conversation rhythms.
    """
    filtered_df = filter_user(df, sel_user)
    clean_df = filtered_df[filtered_df['user'] != 'Group_notification']
    if clean_df.empty:
        return None

    hourly_counts = clean_df['hour'].value_counts().reindex(range(24), fill_value=0)
    theta_labels = [f"{h:02d}:00" for h in range(24)]
    # Close the polar loop
    r_values = list(hourly_counts.values) + [hourly_counts.values[0]]
    theta_values = theta_labels + [theta_labels[0]]

    template = "plotly_dark" if is_dark else "plotly_white"
    line_color = '#38bdf8' if is_dark else '#2563eb'
    fill_color = 'rgba(56, 189, 248, 0.25)' if is_dark else 'rgba(37, 99, 235, 0.2)'

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r_values,
        theta=theta_values,
        fill='toself',
        fillcolor=fill_color,
        line=dict(color=line_color, width=2.5),
        marker=dict(size=5, color=line_color),
        name="Activity"
    ))

    fig.update_layout(
        title="Circadian 24-Hour Activity Clock",
        template=template,
        polar=dict(
            radialaxis=dict(visible=True, showline=False),
            angularaxis=dict(direction="clockwise", period=24)
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=420
    )
    return fig


def plot_participant_personas(df: pd.DataFrame, is_dark: bool = False, min_messages: int = 5):
    """
    Interactive Multi-Dimensional Bubble Scatter Plot:
    X: Total Messages Sent
    Y: Average Words per Message (Verbosity)
    Size: Media Items Shared
    Color: Active Days
    """
    clean_df = df[df['user'] != 'Group_notification']
    if clean_df.empty:
        return None

    # Aggregate per participant
    grouped = clean_df.groupby('user').agg(
        total_messages=('message', 'count'),
        total_words=('message', lambda s: sum(len(str(m).split()) for m in s)),
        media_count=('is_media', 'sum'),
        active_days=('only_date', 'nunique')
    ).reset_index()

    # Filter out users with very few messages for readability
    filtered = grouped[grouped['total_messages'] >= min_messages].copy()
    if filtered.empty:
        filtered = grouped.copy()

    filtered['avg_words'] = round(filtered['total_words'] / filtered['total_messages'], 1)
    # Scaled size for bubble visualization
    filtered['bubble_size'] = np.clip(filtered['media_count'] * 2 + 10, 10, 45)

    template = "plotly_dark" if is_dark else "plotly_white"

    fig = px.scatter(
        filtered,
        x='total_messages',
        y='avg_words',
        size='bubble_size',
        color='active_days',
        hover_name='user',
        hover_data={
            'total_messages': True,
            'avg_words': True,
            'media_count': True,
            'active_days': True,
            'bubble_size': False
        },
        labels={
            'total_messages': 'Total Messages Sent',
            'avg_words': 'Avg Words per Message (Verbosity)',
            'active_days': 'Active Days',
            'media_count': 'Media Shared'
        },
        title='Participant Persona Matrix (Activity vs Verbosity vs Media)',
        template=template,
        color_continuous_scale='Viridis' if is_dark else 'Plasma'
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=450
    )
    return fig


def plot_cumulative_growth(sel_user: str, df: pd.DataFrame, is_dark: bool = False):
    """
    Cumulative message growth curve over the lifetime of the conversation.
    """
    filtered_df = filter_user(df, sel_user)
    clean_df = filtered_df[filtered_df['user'] != 'Group_notification']
    if clean_df.empty:
        return None

    daily = clean_df.groupby('only_date').size().reset_index(name='daily_count')
    daily = daily.sort_values('only_date')
    daily['cumulative_messages'] = daily['daily_count'].cumsum()

    template = "plotly_dark" if is_dark else "plotly_white"
    color = '#f59e0b' if is_dark else '#d97706'

    fig = px.area(
        daily,
        x='only_date',
        y='cumulative_messages',
        title='Cumulative Message Growth Trajectory',
        labels={'only_date': 'Date', 'cumulative_messages': 'Cumulative Messages'},
        template=template
    )
    fig.update_traces(line_color=color, fillcolor='rgba(245, 158, 11, 0.15)')
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=380
    )
    return fig


def plot_sentiment_trend(scored_msgs: pd.DataFrame, is_dark: bool = False):
    """
    Monthly sentiment score trendline showing emotional evolution over time.
    """
    if scored_msgs is None or scored_msgs.empty:
        return None

    monthly_sentiment = scored_msgs.groupby(['year', 'month_num', 'month'])['sentiment_score'].mean().reset_index()
    monthly_sentiment = monthly_sentiment.sort_values(by=['year', 'month_num'])
    monthly_sentiment['time'] = monthly_sentiment['month'] + ' ' + monthly_sentiment['year'].astype(str)

    template = "plotly_dark" if is_dark else "plotly_white"
    line_color = '#10b981' if is_dark else '#059669'

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_sentiment['time'],
        y=monthly_sentiment['sentiment_score'],
        mode='lines+markers',
        line=dict(color=line_color, width=2.5),
        marker=dict(size=7, color=line_color),
        name="Avg Sentiment Polarity"
    ))

    # Add reference line at neutral (0.0)
    fig.add_hline(y=0.0, line_dash="dash", line_color="gray", annotation_text="Neutral Line")

    fig.update_layout(
        title="Monthly Sentiment Polarity Trend (-1.0 Negative to +1.0 Positive)",
        xaxis_title="Month",
        yaxis_title="Mean Sentiment Score",
        template=template,
        margin=dict(l=20, r=20, t=50, b=20),
        height=350,
        yaxis=dict(range=[-0.6, 0.8])
    )
    return fig

