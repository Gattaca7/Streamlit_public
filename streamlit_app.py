import streamlit as st
import pandas as pd
import altair as alt
import os
import requests

# Render app
st.set_page_config(page_title="Strava Activities", page_icon=":runner:", layout="centered")

#upload File
#uploaded_file = st.file_uploader("data.csv", type="csv")
#if uploaded_file is not None:
url = "https://drive.google.com/uc?id=18KyU3ledRA2kU7ZF4_B7xfFacqaZGehx"
df = pd.read_csv(url)

# Enable dark theme
alt.themes.enable('dark')

## ABOUT THE APP ##
def show_about_the_app():
    st.write("Welcome to the Umpify app, designed to visualize the activity of SANFL umpires. This app collects data from the SANFL Umpires Group on Strava, including run name, time, distance, and elevation, to provide an overview of umpire activity. At Umpify, we're committed to continuous improvement. Here are the next few features we're planning to add to make the app even better: Round by round with slider page: This feature will allow users to see whether umpires are running more on average in Round 5 than Round 6, and so on. Map page: Using the titles of the runs, we can figure out which ground the match day runs were at. We want to have a map that shows each ground, making it easier to track umpire activity at specific locations. General tidying: We're always looking to streamline the app and make it more user-friendly, so we'll be conducting general tidying and improvements to ensure the app runs smoothly. Login: We'll be adding a login feature to make it easier for users to access their data and ensure their privacy. Thank you for checking out the Umpify app! If you have any suggestions or would like to help improve the app, please don't hesitate to contact us at umpify@gmail.com.")

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

    longest_run = df[['athlete.firstname', 'athlete.lastname', 'distance']]
    longest_run['athlete'] = longest_run['athlete.firstname'] + ' ' + longest_run['athlete.lastname']
    longest_run['distance'] = longest_run['distance'] / 1000
    longest_run = longest_run.sort_values('distance', ascending=False).drop_duplicates(subset=['athlete']).head(10)[['athlete', 'distance']]
    longest_run['distance'] = longest_run['distance'].apply(lambda x: f"{x:.2f}")

    total_distance = df.groupby('athlete.firstname')['distance'].sum().reset_index(name='sum').sort_values('sum', ascending=False).head(10)

    # Display the tables
    st.subheader("Most Runs")
    st.table(most_runs)
    st.subheader("Longest Run (by distance)")
    st.table(longest_run)
    st.subheader("Most Total Distance")
    st.table(total_distance)

# Add a sidebar with page selection and dark mode toggle button
st.sidebar.title("Settings")
dark_mode = st.sidebar.checkbox("Dark Mode")
page = st.sidebar.selectbox("Select a page", ["Total Activities", "Map", "Leaderboard"])

if dark_mode:
    st.markdown("""<style>body {background-color: #2B2B2B;color: white;}</style>""",unsafe_allow_html=True)
else:
    st.markdown("""<style>body {background-color: white;color: black;}</style>""",unsafe_allow_html=True)

# Show the selected page
if page == "Total Activities":
    st.title("Total Activities")
    show_total_activities()
elif page == "Map":
    st.title("Map")
    show_map()
elif page == "About the App":
    st.title("About the App")
    show_about_the_app()
elif page == "Leaderboard":
    st.title(f"Leaderboard: Last {len(df)} Activities")
    show_leaderboard()