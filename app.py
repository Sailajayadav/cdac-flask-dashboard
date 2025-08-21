import os
import pandas as pd
from flask import Flask, render_template, jsonify, request
import plotly.express as px
from flask_cors import CORS
import numpy as np

# --- Flask App Setup ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_folder='static')
CORS(app)

# --- Load and Clean Data ---
xlsx_path = os.path.join(basedir, "WBL_CDAC_Hyd_August_19_2025.xlsx")
df = pd.read_excel(xlsx_path, engine="openpyxl")

relevant_columns = ['State', 'Employment Status', 'Cohort', 'Technology', 'Gender', 'Category']
for col in relevant_columns:
    if col in df.columns:
        df[col] = df[col].fillna('Unknown')
        df[col] = df[col].astype('category')

# --- Helper Functions ---
def fig_to_serializable(fig_dict):
    """Convert any NumPy arrays in a Plotly figure dict to lists."""
    def convert(obj):
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(i) for i in obj]
        elif isinstance(obj, (np.ndarray, pd.Series)):
            return obj.tolist()
        else:
            return obj
    return convert(fig_dict)

def create_state_wise_participants_chart(df_filtered):
    if df_filtered.empty:
        fig = px.bar(x=['No Data'], y=[0], title='State-wise Participant Count', template='plotly_white')
        return fig_to_serializable(fig.to_dict())

    state_counts = df_filtered['State'].value_counts().reset_index()
    state_counts.columns = ['State', 'Count']
    state_counts['Count'] = state_counts['Count'].astype(int).tolist()  # convert to list explicitly

    fig = px.bar(
        state_counts, x='State', y='Count',
        title='State-wise Participant Count',
        color='Count',
        color_continuous_scale='viridis',
        template='plotly_white'
    )
    fig.update_traces(marker=dict(line=dict(width=2, color='white')),
                      hoverinfo='y', width=0.6)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Poppins, sans-serif', size=16),
        margin=dict(t=60, b=40, l=40, r=40)
    )
    return fig_to_serializable(fig.to_dict())

def create_employment_status_chart(df_filtered):
    if df_filtered.empty:
        fig = px.pie(values=[1], names=['No Data'], title='Employment Status Distribution', template='plotly_white')
        return fig_to_serializable(fig.to_dict())

    employment_counts = df_filtered['Employment Status'].value_counts().reset_index()
    employment_counts.columns = ['Employment Status', 'Count']
    # ensure Count is plain Python list
    values_list = employment_counts['Count'].astype(int).tolist()
    names_list = employment_counts['Employment Status'].tolist()

    fig = px.pie(
        names=names_list,
        values=values_list,
        title='Employment Status Distribution',
        color_discrete_sequence=px.colors.sequential.RdPu,
        template='plotly_white'
    )
    fig.update_traces(textinfo='percent+label', pull=[0.05]*len(values_list),
                      marker=dict(line=dict(color='white', width=2)),
                      hoverinfo='label+percent', rotation=45)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Poppins, sans-serif', size=16),
        margin=dict(t=60, b=40, l=40, r=40)
    )
    return fig_to_serializable(fig.to_dict())

def create_technology_distribution_chart(df_filtered):
    if df_filtered.empty:
        fig = px.bar(x=['No Data'], y=[0], title='Technology Domain Distribution', template='plotly_white')
        return fig_to_serializable(fig.to_dict())

    tech_counts = df_filtered['Technology'].value_counts().reset_index()
    tech_counts.columns = ['Technology', 'Count']
    tech_counts['Count'] = tech_counts['Count'].astype(int).tolist()
    tech_counts['Technology'] = tech_counts['Technology'].tolist()

    fig = px.bar(
        x=tech_counts['Technology'],
        y=tech_counts['Count'],
        title='Technology Domain Distribution',
        color=tech_counts['Count'],
        color_continuous_scale='plasma',
        template='plotly_white'
    )
    fig.update_traces(marker=dict(line=dict(width=2, color='white')),
                      hoverinfo='y', width=0.6)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Poppins, sans-serif', size=16),
        margin=dict(t=60, b=40, l=40, r=40)
    )
    return fig_to_serializable(fig.to_dict())

def create_gender_category_analysis(df_filtered):
    if df_filtered.empty:
        fig = px.bar(x=['No Data'], y=[0], title='Gender and Category Analysis', template='plotly_white')
        return fig_to_serializable(fig.to_dict())

    gender_category_counts = df_filtered.groupby(['Gender', 'Category']).size().reset_index(name='Count')
    gender_category_counts['Count'] = gender_category_counts['Count'].astype(int).tolist()
    gender_category_counts['Gender'] = gender_category_counts['Gender'].tolist()
    gender_category_counts['Category'] = gender_category_counts['Category'].tolist()

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
        margin=dict(t=60, b=40, l=40, r=40)
    )
    return fig_to_serializable(fig.to_dict())

def create_cohort_details_table(df_filtered):
    if df_filtered.empty:
        return []
    cohort_summary = df_filtered.groupby('Cohort').size().reset_index(name='Participant Count')
    # convert any NumPy int64 to Python int
    cohort_summary['Participant Count'] = cohort_summary['Participant Count'].astype(int)
    return cohort_summary.to_dict('records')

# --- Routes ---
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

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
