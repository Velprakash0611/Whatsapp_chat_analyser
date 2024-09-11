import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import preprocess , helper



st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file=st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data=bytes_data.decode("utf-8")
    #st.text(data)
    df=preprocess.preprocess(data)
   # st.dataframe(df)

# to fetch unique users from chat for sidebar
    user_list = df['user'].unique().tolist()
    user_list.remove('Group_notification')
    user_list.sort()
    user_list.insert(0,'All Chats')

    sel_user=st.sidebar.selectbox('Show Analysis for : ',user_list)

    if st.sidebar.button('Show Analysis'):
        
        num_messages , words , num_media_msg, links =helper.fetch_stats(sel_user,df)
        st.title("Top Statistics")

        col1,col2,col3,col4 = st.columns(4)
        

        with col1:  # to show total messages
            st.header("Total Message")
            st.title(num_messages)
            
        with col2:  # to show total words
            st.header("Total Words")
            st.title(words)

        with col3:  # to show total media messages
            st.header("Media Shared")
            st.title(num_media_msg)

        with col4:  # to show total links shared
            st.header("Links Shared")
            st.title(links)

        # monthly timeline analysis
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(sel_user,df)
        fig , ax = plt.subplots()
        ax.plot(timeline['time'],timeline['message'],color ='red')
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(sel_user,df)
        fig , ax = plt.subplots()
        ax.plot(daily_timeline['only_date'],daily_timeline['message'],color ='black')
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

        # activity map
        st.title("Activity Map")
        col1,col2=st.columns(2)

        with col1:
            st.header('Most busy day')
            busy_day = helper.week_activity(sel_user,df)
            fig,ax=plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='cyan')
            plt.xticks(rotation = 'vertical')
            st.pyplot(fig)

        with col2:
            st.header('Most busy Month')
            busy_month = helper.month_activity(sel_user,df)
            fig,ax=plt.subplots()
            ax.bar(busy_month.index,busy_month.values,color='cyan')
            plt.xticks(rotation = 'vertical')
            st.pyplot(fig)


        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(sel_user, df)
        fig,ax = plt.subplots()
        ax=sns.heatmap(user_heatmap)
        st.pyplot(fig)



        # find busiest user

        if sel_user == 'All Chats':
            st.title('Most Busiest User')
            x, df1=helper.most_busy_user(df)
            fig, ax = plt.subplots()
            
            col1,col2 = st.columns(2)

            with col1:
                ax.bar(x.index,x.values, color = 'green')
                plt.xticks(rotation = 'vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(df1)

        # wordcloud
        st.title('Wordcloud')
        df_wc= helper.create_wordcloud(sel_user,df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # most common words
        most_common_words = helper.most_common_words(sel_user,df)
        st.title("Most Common Words")
        fig, ax = plt.subplots()
        ax.bar(most_common_words[0],most_common_words[1], color ='green')
        plt.xticks(rotation ='vertical')
        st.pyplot(fig)
        #  st.dataframe(most_common_words)

        # emoji analysis
        emoji_df = helper.emoji_analyser(sel_user,df)
        st.title("Emoji Analysis")
        col1,col2 = st.columns(2)

        try:
            with col1:
                st.dataframe(emoji_df,height=400,width=1000)


            with col2:
                # Create a bar chart instead of a pie chart
                fig, ax = plt.subplots()
                # Assuming emoji_df[0] contains the labels and emoji_df[1] contains the counts
                ax.bar(emoji_df[0].head(5), emoji_df[1].head(5),width = 0.5,color='orange')  # Use ax.bar() for a bar chart
                # Add labels and title for clarity
                ax.set_xlabel('Emojis')
                ax.set_ylabel('Counts')
                ax.set_title('Emoji Frequency')
                st.pyplot(fig)

        except KeyError as e:
            st.warning(f"Emoji not found")


        st.markdown("<div style='text-align: center;'>End of Analysis</div>", unsafe_allow_html=True)

            

else:
    st.markdown("<div style='text-align: center;'>\n\n\n\n\nUpload the text file</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>\nClick \"Show Analysis\" for report</div>", unsafe_allow_html=True)


