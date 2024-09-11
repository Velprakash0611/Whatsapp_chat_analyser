import re
import pandas as pd
#from dateutil import parser

def preprocess(data):
    pattern="\d{1,2}/\d{1,2}/\d{2}, \d{2}:\d{2} - "

    messages=re.split(pattern, data)[1:]
    date_time = re.findall(pattern, data)

    #create dataframe from text file
    df = pd.DataFrame({ 'user_message':messages,'date':date_time})
    #df['date']= pd.to_datetime(df['date'],format='%m/%d/%y, %H:%M - ')



# Function to parse dates with different formats
    def parse_date(date_string):
        try:
        # Try the MM/DD/YY format first
            return pd.to_datetime(date_string, format='%m/%d/%y, %H:%M - ')
        except ValueError:
            try:
            # If that fails, try DD/MM/YY format
                return pd.to_datetime(date_string, format='%d/%m/%y, %H:%M - ')
            except ValueError:
            # Fallback to automatic date parsing
                return pd.to_datetime(date_string)

# Apply the parse_date function to the 'date' column
    df['date'] = df['date'].apply(parse_date)


    #separate user and message

    users=[]
    messages=[]
    for message in df['user_message']:
        entry=re.split('([\w\W]+?):\s',message)
        if entry[1:]: #user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('Group_notification')
            messages.append(entry[0])
        
    df['user']=users
    df['message']=messages
    df.drop(columns=['user_message'],inplace=True)

    df['year']=df['date'].dt.year
    df['month_num']=df['date'].dt.month
    df['only_date']=df['date'].dt.date
    df['day_name']=df['date'].dt.day_name()
    df['month']=df['date'].dt.month_name()
    df['day']=df['date'].dt.day
    df['hour']=df['date'].dt.hour
    df['minute']=df['date'].dt.minute


    period=[]
    for hour in df[['day_name','hour']]['hour']:
        if hour ==23:
            period.append(str(hour)+'-'+str('00'))
        elif hour ==0:
            period.append(str(00)+'-'+str(hour+1))
        else:
            period.append(str(hour)+'-'+str(hour+1))

    df['period']=period

    return df
