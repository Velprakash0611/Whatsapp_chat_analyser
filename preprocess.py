import re
import pandas as pd

def preprocess(data: str) -> pd.DataFrame:
    """
    Parses WhatsApp exported chat data into a structured pandas DataFrame.
    Supports:
      - 24-hour format: '12/31/22, 23:59 - '
      - 12-hour format: '12/31/22, 11:59 pm - ' or '12/31/2022, 11:59 AM - '
      - iOS format: '[12/31/22, 11:59:59 PM] ' or '[31/12/2022, 23:59:59] '
    """
    if not data or not data.strip():
        return pd.DataFrame()

    # Normalize unicode non-breaking spaces (e.g. \u202f, \xa0) often present before AM/PM
    normalized_data = data.replace('\u202f', ' ').replace('\xa0', ' ')

    # List of candidate regex patterns for timestamp delimiters in WhatsApp exports
    # We test which pattern matches best
    patterns = [
        # Android 24-hour and 12-hour: '12/31/22, 19:49 - ' or '31/12/2021, 09:08 am - '
        r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?\s-\s)',
        # iOS format: '[12/31/22, 7:49:00 PM] ' or '[31/12/2021, 19:49:00] '
        r'(\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?\]\s)',
        # Alternate hyphen date: '2021-10-21, 19:49 - '
        r'(\d{4}-\d{1,2}-\d{1,2},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?\s-\s)',
        # Alternate dot date: '21.10.21, 19:49 - '
        r'(\d{1,2}\.\d{1,2}\.\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?(?:\s?[apAP][mM])?\s-\s)'
    ]

    matched_pattern = None
    max_matches = 0

    for pat in patterns:
        count = len(re.findall(pat, normalized_data))
        if count > max_matches:
            max_matches = count
            matched_pattern = pat

    if not matched_pattern or max_matches == 0:
        # Fallback to general timestamp pattern
        matched_pattern = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\s?[apAP][mM])?\s-\s)'

    raw_splits = re.split(matched_pattern, normalized_data)
    date_times = re.findall(matched_pattern, normalized_data)

    # In re.split with capture group, raw_splits contains: [preamble, date1, msg1, date2, msg2, ...]
    # If not capturing group or standard split:
    if len(raw_splits) == len(date_times) * 2 + 1:
        messages = raw_splits[2::2]
        dates = raw_splits[1::2]
    else:
        # Fallback split without capture group
        messages = re.split(matched_pattern, normalized_data)[1:]
        dates = date_times

    if not dates or not messages:
        return pd.DataFrame()

    # Align lengths safely
    min_len = min(len(dates), len(messages))
    dates = dates[:min_len]
    messages = messages[:min_len]

    # Clean date strings (remove trailing ' - ' or enclosing brackets)
    cleaned_dates = [re.sub(r'^[\[\s]+|[\]\s\-]+$', '', d).strip() for d in dates]

    df = pd.DataFrame({'raw_date': cleaned_dates, 'user_message': messages})

    # Vectorized date parsing with flexible fallbacks
    try:
        df['date'] = pd.to_datetime(df['raw_date'], format='mixed', errors='coerce')
    except Exception:
        df['date'] = pd.to_datetime(df['raw_date'], errors='coerce')
    
    # If coerce resulted in many NaTs, try dayfirst=True
    if df['date'].isna().mean() > 0.3:
        try:
            df['date'] = pd.to_datetime(df['raw_date'], dayfirst=True, format='mixed', errors='coerce')
        except Exception:
            df['date'] = pd.to_datetime(df['raw_date'], dayfirst=True, errors='coerce')

    # Forward fill or drop remaining invalid dates
    df = df.dropna(subset=['date']).reset_index(drop=True)

    users = []
    cleaned_messages = []

    # Regex for user: message separation
    # WhatsApp standard format: "User Name: Message text"
    user_pattern = re.compile(r'^([^:\n]+?):\s(.*)$', re.DOTALL)

    for msg in df['user_message']:
        match = user_pattern.match(msg)
        if match:
            users.append(match.group(1).strip())
            cleaned_messages.append(match.group(2).strip())
        else:
            # System notification (e.g. Group creator created group, You were added, Security code changed)
            users.append('Group_notification')
            cleaned_messages.append(msg.strip())

    df['user'] = users
    df['message'] = cleaned_messages
    df.drop(columns=['user_message', 'raw_date'], inplace=True, errors='ignore')

    # Temporal feature engineering
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['only_date'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Format period uniformly as '00:00 - 01:00', '01:00 - 02:00', ..., '23:00 - 00:00'
    df['period'] = df['hour'].apply(lambda h: f"{h:02d}:00 - {(h + 1) % 24:02d}:00")

    # Media detection
    media_patterns = [
        '<media omitted>',
        '<attached:',
        'image omitted',
        'video omitted',
        'audio omitted',
        'sticker omitted',
        'document omitted',
        'contact card omitted'
    ]
    df['is_media'] = df['message'].str.lower().apply(
        lambda m: any(p in m for p in media_patterns)
    )

    # Deleted message detection
    deleted_patterns = [
        'this message was deleted',
        'you deleted this message'
    ]
    df['is_deleted'] = df['message'].str.lower().apply(
        lambda m: any(p in m for p in deleted_patterns)
    )

    return df
