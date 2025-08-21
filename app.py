import os
import pandas as pd
from flask import Flask, render_template, jsonify, request
import plotly.express as px

# Define the base directory for the Flask app
basedir = os.path.abspath(os.path.dirname(__file__))

# Create the Flask application instance
app = Flask(__name__, static_folder='static')

# --- Data Loading and Cleaning ---
basedir = os.path.abspath(os.path.dirname(__file__))
xlsx_path = os.path.join(basedir, "WBL_CDAC_Hyd_August_19_2025.xlsx")  # change filename

# read all sheets as dict of DataFrames
df = pd.read_excel(xlsx_path, engine="openpyxl")

relevant_columns = ['State', 'Employment Status', 'Cohort', 'Technology', 'Gender', 'Category']
for col in relevant_columns:
    if col in df.columns:
        df[col] = df[col].fillna('Unknown')
        df[col] = df[col].astype('category')

# --- Helper Functions for Visualizations ---
def create_state_wise_participants_chart(df_filtered):
    state_counts = df_filtered['State'].value_counts().reset_index()
    state_counts.columns = ['State', 'Count']
    fig = px.bar(
        state_counts,
        x='State',
        y='Count',
        title='State-wise Participant Count',
        color='Count',
        color_continuous_scale='viridis',
        template='plotly_white'
    )
    fig.update_traces(marker=dict(line=dict(width=2, color='white'),
                                  colorbar=dict(thickness=20)),
                      marker_line_width=2,
                      marker_line_color='rgba(0,0,0,0.1)',
                      hoverinfo='y',
                      width=0.6)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Poppins, sans-serif', size=16),
        margin=dict(t=60, b=40, l=40, r=40),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(200,200,255,0.2)'),
        transition={'duration': 500, 'easing': 'cubic-in-out'}
    )
    return fig.to_json()

def create_employment_status_chart(df_filtered):
    employment_counts = df_filtered['Employment Status'].value_counts().reset_index()
    employment_counts.columns = ['Employment Status', 'Count']
    fig = px.pie(
        employment_counts,
        values='Count',
        names='Employment Status',
        title='Employment Status Distribution',
        color_discrete_sequence=px.colors.sequential.RdPu,
        template='plotly_white'
    )
    fig.update_traces(textinfo='percent+label', pull=[0.05]*len(employment_counts),
                      marker=dict(line=dict(color='white', width=2)),
                      hoverinfo='label+percent',
                      rotation=45)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Poppins, sans-serif', size=16),
        margin=dict(t=60, b=40, l=40, r=40),
        transition={'duration': 500, 'easing': 'cubic-in-out'}
    )
    return fig.to_json()

def create_technology_distribution_chart(df_filtered):
    technology_counts = df_filtered['Technology'].value_counts().reset_index()
    technology_counts.columns = ['Technology', 'Count']
    fig = px.bar(
        technology_counts,
        x='Technology',
        y='Count',
        title='Technology Domain Distribution',
        color='Count',
        color_continuous_scale='plasma',
        template='plotly_white'
    )
    fig.update_traces(marker=dict(line=dict(width=2, color='white'),
                                  colorbar=dict(thickness=20)),
                      marker_line_width=2,
                      marker_line_color='rgba(0,0,0,0.1)',
                      hoverinfo='y',
                      width=0.6)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Poppins, sans-serif', size=16),
        margin=dict(t=60, b=40, l=40, r=40),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(200,200,255,0.2)'),
        transition={'duration': 500, 'easing': 'cubic-in-out'}
    )
    return fig.to_json()

def create_gender_category_analysis(df_filtered):
    gender_category_counts = df_filtered.groupby(['Gender', 'Category']).size().reset_index(name='Count')
    fig = px.bar(
        gender_category_counts,
        x='Gender',
        y='Count',
        color='Category',
        barmode='group',
        title='Gender and Category Analysis',
        template='plotly_white'
    )
    fig.update_traces(marker_line_width=2, marker_line_color='white', width=0.6)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Poppins, sans-serif', size=16),
        margin=dict(t=60, b=40, l=40, r=40),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(200,200,255,0.2)'),
        transition={'duration': 500, 'easing': 'cubic-in-out'}
    )
    return fig.to_json()

def create_cohort_details_table(df_filtered):
    cohort_summary = df_filtered.groupby('Cohort').size().reset_index(name='Participant Count')
    return cohort_summary.to_dict('records')

# --- Routes and Views ---

@app.route("/excel")
def excel_view():

    return df.to_html(classes="table table-striped", index=False)

@app.route('/')
def index():
    states = ['All'] + sorted(df['State'].unique().tolist())
    cohorts = ['All'] + sorted(df['Cohort'].unique().tolist())
    genders = ['All'] + sorted(df['Gender'].unique().tolist())
    technologies = ['All'] + sorted(df['Technology'].unique().tolist())
    employment_statuses = ['All'] + sorted(df['Employment Status'].unique().tolist())

    return render_template('index.html',
                           states=states,
                           cohorts=cohorts,
                           genders=genders,
                           technologies=technologies,
                           employment_statuses=employment_statuses)

@app.route('/api/data')
def get_data():
    selected_state = request.args.get('state', 'All')
    selected_cohort = request.args.get('cohort', 'All')
    selected_gender = request.args.get('gender', 'All')
    selected_technology = request.args.get('technology', 'All')
    selected_employment_status = request.args.get('employment_status', 'All')

    filtered_df = df.copy()
    if selected_state != 'All':
        filtered_df = filtered_df[filtered_df['State'] == selected_state]
    if selected_cohort != 'All':
        filtered_df = filtered_df[filtered_df['Cohort'] == selected_cohort]
    if selected_gender != 'All':
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    if selected_technology != 'All':
        filtered_df = filtered_df[filtered_df['Technology'] == selected_technology]
    if selected_employment_status != 'All':
        filtered_df = filtered_df[filtered_df['Employment Status'] == selected_employment_status]

    response = {
        'state_chart_data': create_state_wise_participants_chart(filtered_df),
        'employment_chart_data': create_employment_status_chart(filtered_df),
        'technology_chart_data': create_technology_distribution_chart(filtered_df),
        'gender_category_chart_data': create_gender_category_analysis(filtered_df),
        'cohort_table_data': create_cohort_details_table(filtered_df)
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
