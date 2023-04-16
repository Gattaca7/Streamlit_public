import streamlit as st
import pandas as pd
import altair as alt
import os
import requests

# Render app
st.set_page_config(page_title="Strava Activities", page_icon=":runner:", layout="centered")

url = "https://drive.google.com/uc?id=1plOBbcq6T6k-VPE0zMPzjyp9fzMoHv1Y" 
df = pd.read_csv(url)

## TOTAL ACTIVITIES PAGE ##
# Define function to show Total Activities page
def show_total_activities():
    # Create scatter plot for elevation gain and distance
    scatter1 = alt.Chart(df).mark_circle(size=60).encode(
        x=alt.X('total_elevation_gain', title='Total Elevation Gain (m)'),
        y=alt.Y('distance', title='Total Distance (km)'),
        color=alt.Color('group:N', title='Group'),
        tooltip=['name', 'distance', 'total_elevation_gain', 'type']
    )

    # Create scatter plot for time and distance
    scatter2 = alt.Chart(df).mark_circle(size=60).encode(
        x=alt.X('moving_time', title='Moving Time (seconds)'),
        y=alt.Y('distance', title='Total Distance (km)'),
        color=alt.Color('group:N', title='Group'),
        tooltip=[
            'name', 
            'distance', 
            'moving_time', 
            'type', 
            'athlete.firstname', 
            'group'
         ]
    )

    # Create column chart for total distance by discipline
    column1 = alt.Chart(df).mark_bar().encode(
        x=alt.X('group', title='Discipline'),
        y=alt.Y('sum(distance):Q', title='Total Distance (m)'),
        color=alt.Color('type:N', title='Discipline')
    )

    # Create column chart for total activities by discipline
    column2 = alt.Chart(df).mark_bar().encode(
        x=alt.X('group', title='Discipline'),
        y=alt.Y('count():Q', title='Total Activities'),
        color=alt.Color('type:N', title='Discipline')
    )

    # Add the scatter plots and column charts to the app
    st.altair_chart(scatter1, use_container_width=True)
    st.altair_chart(scatter2, use_container_width=True)
    st.altair_chart(column1, use_container_width=True)
    st.altair_chart(column2, use_container_width=True)

## MAP PAGE ##
# Define function to show Map page
def show_map():
    pass

## LEADERBOARD PAGE ##
# Define function to show Leaderboard page
def show_leaderboard():
    # Define three dataframes for the three tables
    most_runs = df.groupby(['athlete.firstname', 'athlete.lastname']).size().reset_index(name='count').sort_values('count', ascending=False).head(10)
    most_runs['athlete'] = most_runs['athlete.firstname'] + ' ' + most_runs['athlete.lastname']
    most_runs.drop(['athlete.firstname', 'athlete.lastname'], axis=1, inplace=True)
    most_runs = most_runs[['athlete', 'count']]
    most_runs = most_runs.rename(columns={'athlete': 'Athlete'})
    most_runs_no_index = most_runs.reset_index(drop=True)

    longest_run = df[['athlete.firstname', 'athlete.lastname', 'distance']]
    longest_run['athlete'] = longest_run['athlete.firstname'] + ' ' + longest_run['athlete.lastname']
    longest_run['distance'] = longest_run['distance'] / 1000
    longest_run = longest_run.sort_values('distance', ascending=False).drop_duplicates(subset=['athlete']).head(10)[['athlete', 'distance']]
    longest_run['distance'] = longest_run['distance'].apply(lambda x: f"{x:.2f}")
    longest_run = longest_run.rename(columns={'athlete': 'Athlete'})
    longest_run_no_index = longest_run.reset_index(drop=True)

    total_distance = df.groupby(['athlete.firstname', 'athlete.lastname'])['distance'].sum().reset_index(name='sum').sort_values('sum', ascending=False).head(10)
    total_distance['athlete'] = total_distance['athlete.firstname'] + ' ' + total_distance['athlete.lastname']
    total_distance.drop(['athlete.firstname', 'athlete.lastname'], axis=1, inplace=True)
    total_distance = total_distance.rename(columns={'athlete': 'Athlete'})
    total_distance_no_index = total_distance.reset_index(drop=True)

    # Display the tables
    st.subheader("Most Runs")
    st.table(most_runs_no_index)
    st.subheader("Longest Run (by distance)")
    st.table(longest_run_no_index)
    st.subheader("Most Total Distance")
    st.table(total_distance_no_index)

## ABOUT THE APP ##
def show_about_the_app():
    st.write("About the App:\n\nWelcome to Umpify - an app designed to visualize the activity of SANFL umpires. We collect data from the SANFL Umpires Group on Strava, including time, distance, and elevation, to provide an overview of umpire activity. At Umpify, we are committed to continuous improvement, and we plan to add the following 4 features to make the app even better:\n\n1. Round-by-round with slider page: This feature will allow users to see whether umpires are running more on average in Round 5 than Round 6, and so on.\n2. Map page: We want to create a map that shows each ground where the match day runs were held. This will help users track umpire activity at specific locations.\n3. General tidying: We are always looking to streamline the app and make it more user-friendly, so we'll be conducting general tidying and improvements to ensure the app runs smoothly.\n4. Login: We'll be adding a login feature to make it easier for users to access their data and ensure their privacy.\n\nThank you for checking out the Umpify app! If you have any suggestions or would like to help improve the app, please don't hesitate to contact us at umpify@gmail.com.")

## MATCH TRACKER PAGE ##
# filter out rows with null values in round column
def match_tracker():
    filtered_df = df[df["round"].notnull()]

# calculate the average distance for each round and group
    avg_distance = filtered_df.groupby(['round', 'group']).mean().reset_index()

# create scatter plot
    scatter_plot = (
        alt.Chart(avg_distance)
        .mark_point(filled=True, size=100)
        .encode(
            x=alt.X("round:O", axis=alt.Axis(title="Round")),
            y=alt.Y("distance:Q", axis=alt.Axis(title="Average Distance")),
            tooltip=["round", "group", "distance"],
            color=alt.Color("group:N", title="Discipline"),
        )
        .properties(title="Average Distance by Round and Discipline")
    )

# display scatter plot in Streamlit app
    st.altair_chart(scatter_plot, use_container_width=True)

# filter the DataFrame to keep only the desired columns and rows with non-null values in the 'round' column
    filtered_df2 = df.loc[df['round'].notnull(), ['distance', 'name', 'round']]
    filtered_df2['round'] = filtered_df2['round'].astype(int)

# Define the slider range and default value based on the unique values in the 'round' column
    min_round = filtered_df2['round'].min()
    max_round = filtered_df2['round'].max()
    default_round = (min_round, max_round)

# Add a slider to filter the DataFrame by the 'round' column
    round_filter = st.slider('Filter by Round', int(min_round), int(max_round), (int(default_round[0]), int(default_round[1])))
    filtered_df2 = filtered_df2.loc[(filtered_df2['round'].astype(int) >= round_filter[0]) & (filtered_df2['round'].astype(int) <= round_filter[1])]

# Display the filtered DataFrame in a table using Streamlit
    st.table(filtered_df2.set_index('name', drop=True))

## SIDEBAR ##
# Add a sidebar with page selection
st.sidebar.title("Settings")
page = st.sidebar.selectbox("Select a page", ["Total Activities", "Map", "Leaderboard", "Match Tracker", "About the App"])

# Show the selected page
if page == "Total Activities":
    st.title("Total Activities")
    show_total_activities()
elif page == "Map":
    st.title("Map")
    show_map()
elif page == "Match Tracker":
    st.title("Match Tracker")
    match_tracker()
elif page == "About the App":
    st.title("About the App")
    show_about_the_app()
elif page == "Leaderboard":
    st.title(f"Leaderboard: Last {len(df)} Activities")
    show_leaderboard()