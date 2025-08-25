import os
import pandas as pd
from flask import Flask, render_template, jsonify, request
import plotly.express as px
from flask_cors import CORS
import numpy as np
import base64
import io

# --- Flask App Setup ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app)

# The raw data string from your original prompt
data_string = """State,Organization,Center,Sl. No.,Cohort,Level,Gender,Candidate's Name,Category,Candidate Status (Joined/Completed/Resigned),Date of Joining,Technology,"Candidate Qualification
(B.Tech./B.E/M.S.c/M.C.A)",Passed Out Year/Pursuing 7th or 8th semester,Employment Status
Telangana,C-DAC,Hyderabad,1," Cohort 2- L1, 2023",Level-1,Male,Dipak V,ST,Completed,20-03-23,Web Technologies,B.Tech,2023,Unemployed
Telangana,C-DAC,Hyderabad,2," Cohort 2- L1, 2023",Level-1,Female,Devraj Bavan,SC,Completed,20-03-2023,AI/ML,B.Tech,2023,Unemployed
Telangana,C-DAC,Hyderabad,3," Cohort 2- L1, 2023",Level-1,Male,P.Deepthi,EWS,Resigned,21-04-2023,Software Technologies,B.Tech,2023,Employed
Telangana,C-DAC,Hyderabad,4," Cohort 2- L1, 2023",Level-1,Male,D Tejonath,EWS,Completed,21-04-2023,Web Development ,B. Tech,2023,Employed
Telangana,C-DAC,Hyderabad,5," Cohort 2- L1, 2023",Level-1,Male,P Ramyasri,SC,Completed,21-04-2023,Web Development,B. Tech,2023,Employed
Telangana,C-DAC,Hyderabad,6," Cohort 2- L1, 2023",Level-1,Male,P. Chandini,ST,Completed,22-04-2023,Web Development,B.Tech,2023,
Telangana,C-DAC,Hyderabad,7," Cohort 2- L1, 2023",Level-1,Female,Madala Aswanitejasri,ST,Completed,21-04-2023,Mobile Apps,B.Tech,2023,
Telangana,C-DAC,Hyderabad,8," Cohort 2- L1, 2023",Level-1,Female,Tanuja Chikkala,EWS,Resigned,21-04-2023,Cyber Security,B.Tech,2023,Employed
Telangana,C-DAC,Hyderabad,9," Cohort 2- L1, 2023",Level-1,Female,Y. Likhitha,Women,Completed,21-04-2023,Cyber Security,B.Tech,2023,Unemployed
Telangana,C-DAC,Hyderabad,10," Cohort 2- L1, 2023",Level-1,Female,K. Yamini,SC,Completed,22-04-2023,Web Development,B.Tech,2023,Unemployed
Telangana,C-DAC,Hyderabad,11," Cohort 2- L1, 2023",Level-1,Male,B. Satish,ST,Completed,21-04-2023,Web Development,B.Tech,2023,Employed
Telangana,C-DAC,Hyderabad,12," Cohort 2- L1, 2023",Level-1,Male,Yadla Ushasri,SC,Completed,21-4-2023,Mobile Apps,B. Tech,2023,Employed
Telangana,C-DAC,Hyderabad,13,"Cohort 3, L-2, 2023",Level-2,Female,Madala Aswanitejasri,ST,Completed,25/10/2023,Mobile App Development,B.Tech,2023,Employed
Telangana,C-DAC,Hyderabad,14,"Cohort 3, L-2, 2023",Level-2,Female,P. Chandini,ST,Resigned,,Software Technologies,B.Tech,2023,Employed
Telangana,C-DAC,Hyderabad,15,"Cohort 3, L-2, 2023",Level-2,Male,Dipak V,ST,Completed,09/25/2023,Web Technologies,B.Tech,2023,Unemployed
Telangana,C-DAC,Hyderabad,16,"Cohort 3, L-2, 2023",Level-2,Male,Devraj Bavan,SC,Completed,10/09/2023,Artificial Intelligence,B.Tech,2023,Unemployed
Telangana,C-DAC,Hyderabad,17,"Cohort 3, L-1, 2023",Level-1,Male,Mr. Swarajyam Deepak Raj,SC,Completed,10.10.2023,Cyber Security,B.Tech,2023,Pursuing Higher education
Telangana,C-DAC,Hyderabad,18,"Cohort 3, L-1, 2023",Level-1,Female,Ms. Anupama Hendry,SC,Completed,11.10.2023,Artificial Intelligence,B.Tech,Pursuing 7th sem,Ongoing
Telangana,C-DAC,Hyderabad,19,"Cohort 3, L-1, 2023",Level-1,Male,Mr. Eslavath Keerthi Bhushan Naik,ST,Completed,21.09.2023,Artificial Intelligence,B.Tech,2022,Status Pending
Telangana,C-DAC,Hyderabad,20,"Cohort 3, L-1, 2023",Level-1,Female,Ms. Thokachichu Tejaswini,Women,Completed,25.09.2023,Artificial Intelligence,B.Tech,Pursuing 7th sem,Employed
Telangana,C-DAC,Hyderabad,21,"Cohort 3, L-1, 2023",Level-1,Female,Ms. Shavva Sai Shraddha,Women,Completed,25.09.2023,Big Data Analytics,B.Tech,2023,Ongoing
Telangana,C-DAC,Hyderabad,22,"Cohort 3, L-1, 2023",Level-1,Male,Mr. Sandu Ankamma Rao,EWS,Resigned,25.09.2023,Software Technologies,B.Tech,2023,Employed
Telangana,C-DAC,Hyderabad,23,"Cohort 4, L-2, 2024",Level-2,Female,Ms. Shavva Sai Shraddha,Women,Completed,01.04.2024,Big Data Analytics,B.Tech,2023,Ongoing
Telangana,C-DAC,Hyderabad,24,"Cohort 4, L-2, 2024",Level-2,Female,Ms. Anupama Hendry,SC,Completed,22.04.2024,Artificial Intelligence,B.Tech,Pursuing 7th sem,Ongoing
Telangana,C-DAC,Hyderabad,25,"Cohort 4, L-1, 2024",Level-1,Female,Nuthalapati Pauline Angel,Women,Completed,06.03.2024,Cyber Security,B.Tech,Pursuing 8th semester,Employed
Telangana,C-DAC,Hyderabad,26,"Cohort 4, L-1, 2024",Level-1,Female,CHINNAKOTLA MADHAVI,Women,Completed,06.03.2024,Artificial Intelligence,B.Tech,Pursuing 8th semester,Ongoing
Telangana,C-DAC,Hyderabad,27,"Cohort 4, L-1, 2024",Level-1,Female,Mullangi Naga Sahitya,EWS,Completed,11.03.2024,Mobile App Development,B.Tech,Pursuing 8th semester,Employed
Telangana,C-DAC,Hyderabad,28,"Cohort 4, L-1, 2024",Level-1,Female,Sathuluri Keerthana,SC,Completed,06.03.2024,Artificial Intelligence,B.Tech,Pursuing 8th semester,Ongoing
Telangana,C-DAC,Hyderabad,29,"Cohort 4, L-1, 2024",Level-1,Female,Doppala Baby Shalini,SC,Completed,06.03.2024,Drones,B.Tech,Pursuing 8th semester,Ongoing
Telangana,C-DAC,Hyderabad,30,"Cohort 4, L-1, 2024",Level-1,Male,Akula Niranjan,ST,Resigned,06.03.2024,Drones,B.Tech,Pursuing 8th semester,Employed
Telangana,C-DAC,Hyderabad,31,"Cohort 4, L-1, 2024",Level-1,Male,DOKI VAMSI KRISHNA,EWS,Completed,06.03.2024,Artificial Intelligence,B.Tech,Pursuing 8th semester,Ongoing
Telangana,C-DAC,Hyderabad,32,"Cohort 4, L-1, 2024",Level-1,Male,Ven Leonin Kandlakunta,SC,Completed,06.03.2024,Mobile App Development,B.Tech,Pursuing 8th semester,Ongoing
Telangana,C-DAC,Hyderabad,33,"Cohort 4, L-1, 2024",Level-1,Male,Mohit Kumar Maloth,ST,Resigned,07.03.2024,Software Technologies,B.Tech,Pursuing 8th semester,Employed
Telangana,C-DAC,Hyderabad,34,"Cohort 4, L-1, 2024",Level-1,Female,Komma Swathi Reddy,Women,Completed,26.03.2024,Artificial Intelligence,B.Tech,Pursuing 8th semester,Employed
Telangana,C-DAC,Hyderabad,35,"Cohort 5, L-1, 2024",Level-1,Female,Gundluru Mamatha,SC,Joined,21.08.2024,Metaverse,B.Tech,Pursuing 7th semester,Ongoing
Telangana,C-DAC,Hyderabad,36,"Cohort 5, L-1, 2024",Level-1,Male,Ragimanu Sivamahendranath,SC,Joined,22.10.2024,Big Data Analytics,B.Tech,2024,Ongoing
Telangana,C-DAC,Hyderabad,37,"Cohort 5, L-1, 2024",Level-1,Male,Chandolu Joy Suhas,SC,Joined,22.10.2024,Cyber Security,B.Tech,Pursuing 7th semester,Ongoing
Telangana,C-DAC,Hyderabad,38,"Cohort 5, L-1, 2024",Level-1,Female,Meka Akanksha,SC,Joined,21.08.2024,Cyber Security,B.Tech,Pursuing 7th semester,Employed
Telangana,C-DAC,Hyderabad,39,"Cohort 5, L-1, 2024",Level-1,Female,Aparna Malineni,EWS,Joined,21.08.2024,Metaverse,B.Tech,2024,Ongoing
Telangana,C-DAC,Hyderabad,40,"Cohort 5, L-1, 2024",Level-1,Male,Durvasula Sai Srikanth,EWS,Joined,21.08.2024,Artificial Intelligence,B.Tech,2024,Employed
Telangana,C-DAC,Hyderabad,41,"Cohort 5, L-1, 2024",Level-1,Male,Syed Akif,EWS,Joined,21.08.2024,Cyber Security,B.Tech,2024,Ongoing
Telangana,C-DAC,Hyderabad,42,"Cohort 5, L-1, 2024",Level-1,Female,Komirisetti Bhavya Sri Satya Sai,Women,Joined,21.08.2024,Mobile App Development,B.Tech,Pursuing 7th semester,Employed
Telangana,C-DAC,Hyderabad,43,"Cohort 5, L-1, 2024",Level-1,Female,Perumandla Sushma,Women,Joined,21.08.2024,Cyber Security,B.Tech,2024,Ongoing
Telangana,C-DAC,Hyderabad,44,"Cohort 5, L-1, 2024",Level-1,Female,Swathi Verma,Women,Joined,21.08.2024,Cyber Security,B.Tech,2022,Employed
Telangana,C-DAC,Hyderabad,45,"Cohort 5, L-1, 2024",Level-1,Female,Chagallu Rekha,Women,Joined,21.08.2024,Big Data Analytics,B.Tech,2024,Ongoing
Telangana,C-DAC,Hyderabad,46,"Cohort 5, L-1, 2024",Level-1,Female,Banoth Sai Pallavi,ST,Joined,22.10.2024,Web Development,B.Tech,Pursuing 7th semester,Ongoing
Telangana,C-DAC,Hyderabad,47,"Cohort 5, L-1, 2024",Level-1,Male,Jarpula Tharun,ST,Joined,22.10.2024,Artificial Intelligence,B.Tech,Pursuing 7th semester,Ongoing
Telangana,C-DAC,Hyderabad,48,"Cohort 5, L-2, 2024",Level-2,Female,Mullangi Naga Sahitya,EWS,Resigned,20.09.2024,Mobile App Development,B.Tech,2024,
Telangana,C-DAC,Hyderabad,49,"Cohort 5, L-2, 2024",Level-2,Female,Nuthalapati Pauline Angel,Women,Resigned,20.09.2024,Cyber Security,B.Tech,2024,
Telangana,C-DAC,Hyderabad,50,"Cohort 6, L-1, 2025",Level-1,Female,Aruna Jyothi Boddu,SC,Joined,24.02.2025,Web Development,,,
Telangana,C-DAC,Hyderabad,51,"Cohort 6, L-1, 2025",Level-1,Male,Pavan Banoth,ST,Joined,24.02.2025,Artificial Intelligence,,,
Telangana,C-DAC,Hyderabad,52,"Cohort 6, L-1, 2025",Level-1,Male,Mohammed Mahroz Uddin Hamza,EWS,Joined,06.03.2025,Web Development,,,
Telangana,C-DAC,Hyderabad,53,"Cohort 6, L-1, 2025",Level-1,Female,Vangala Chandana ,EWS,Joined,24.02.2025,Cyber Security,,,
Telangana,C-DAC,Hyderabad,54,"Cohort 6, L-1, 2025",Level-1,Female,Ganga Sravani Neelapala,Women,Joined,24.02.2025,Artificial Intelligence,,,
Telangana,C-DAC,Hyderabad,55,"Cohort 6, L-1, 2025",Level-1,Female,Chitti Reddy Veda,Women,Joined,03.03.2025,Web Development,,,
Telangana,C-DAC,Hyderabad,56,"Cohort 6, L-1, 2025",Level-1,Female,Pithani Sowgandhika ,Women,Joined,05.03.2025,Artificial Intelligence,,,
Telangana,C-DAC,Hyderabad,57,"Cohort 6, L-1, 2025",Level-1,Female,Vallabhapurapu Blessy Rani,SC,Joined,10.03.2025,Cyber Security,,,
Telangana,C-DAC,Hyderabad,58,"Cohort 6, L-2, 2025",Level-2,Female,Ms. G Mamatha,SC,Joined,24.02.2025,Metaverse,,,
Telangana,C-DAC,Hyderabad,59,"Cohort 6, L-2, 2025",Level-2,Female,Ms. Meka Akanksha,SC,Joined,25.02.2025,Web Development,,,
Telangana,C-DAC,Hyderabad,60,"Cohort 6, L-2, 2025",Level-2,Female,Ms. Chagallu Rekha,Women,Joined,03.03.2025,Cyber Security,,,
Telangana,C-DAC,Hyderabad,61,"Cohort 6, L-2, 2025",Level-2,Female,Ms. Sushma Perumandla,Women,Joined,24.02.2025,Cyber Security,,,
Telangana,C-DAC,Hyderabad,62,"Cohort 6, L-2, 2025",Level-2,Female,Ms. Swathi Verma,Women,Joined,26.02.2025,Cyber Security,,,"""

df = pd.read_csv(io.StringIO(data_string))
df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('\r', '')
df['Technology'] = df['Technology'].str.strip()
df['Employment Status'] = df['Employment Status'].str.strip()
df['Cohort'] = df['Cohort'].str.strip()
df['Gender'] = df['Gender'].str.strip()
df['Category'] = df['Category'].str.strip()
df['Technology'] = df['Technology'].replace('Web Technologies', 'Web Development') # Normalize tech names
df['Technology'] = df['Technology'].replace('AI/ML', 'Artificial Intelligence') # Normalize tech names

# --- Helper Functions ---
def fig_to_serializable(fig_dict):
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

def get_total_participant_count(df_filtered):
    return len(df_filtered)

def create_employment_status_chart(df_filtered):
    employment_counts = df_filtered['Employment Status'].value_counts().reset_index()
    employment_counts.columns = ['status', 'count']
    return {
        'data': [{
            'labels': employment_counts['status'].tolist(),
            'values': employment_counts['count'].tolist(),
            'type': 'pie',
            'hole': .4
        }],
        'layout': {'title': 'Employment Status Distribution'}
    }

def create_technology_distribution_chart(df_filtered):
    tech_counts = df_filtered['Technology'].value_counts().reset_index()
    tech_counts.columns = ['technology', 'count']
    return {
        'data': [{
            'x': tech_counts['technology'].tolist(),
            'y': tech_counts['count'].tolist(),
            'type': 'bar'
        }],
        'layout': {'title': 'Technology Domain Analysis'}
    }

def create_gender_category_analysis(df_filtered):
    # Normalize 'Women' category to 'Female' in both Gender and Category columns
    df_filtered['Gender'] = df_filtered['Gender'].replace('Women', 'Female')
    df_filtered['Category'] = df_filtered['Category'].replace('Women', 'Female')

    male_df = df_filtered[df_filtered['Gender'] == 'Male']
    female_df = df_filtered[df_filtered['Gender'] == 'Female']

    male_counts = male_df['Category'].value_counts().reset_index()
    male_counts.columns = ['category', 'count']

    female_counts = female_df['Category'].value_counts().reset_index()
    female_counts.columns = ['category', 'count']

    # Add text labels for bar charts, show only the count once, and set contrasting colors
    # Professional color palette
    male_bar = {
        'x': male_counts['category'].tolist(),
        'y': male_counts['count'].tolist(),
        'type': 'bar',
        'text': male_counts['count'].tolist(),
        'textposition': 'outside',
        'textfont': {'size': 24, 'color': '#212121', 'family': 'Arial', 'weight': 'bold'},
        'marker': {'color': '#1976d2'},  # Professional blue
        'hoverlabel': {'font': {'color': 'white'}, 'bgcolor': '#1976d2'}
    }
    female_bar = {
        'x': female_counts['category'].tolist(),
        'y': female_counts['count'].tolist(),
        'type': 'bar',
        'text': female_counts['count'].tolist(),
        'textposition': 'outside',
        'textfont': {'size': 24, 'color': '#ad1457', 'family': 'Arial', 'weight': 'bold'},
        'marker': {'color': '#ad1457'},  # Professional magenta
        'hoverlabel': {'font': {'color': 'white'}, 'bgcolor': '#ad1457'}
    }

    return {
        'male': {
            'data': [male_bar],
            'layout': {
                'title': 'Male Category Analysis',
                'uniformtext': {'mode': 'show', 'minsize': 16},
                'yaxis': {'automargin': True},
                'margin': {'t': 60, 'b': 40, 'l': 40, 'r': 20}
            }
        },
        'female': {
            'data': [female_bar],
            'layout': {
                'title': 'Female Category Analysis',
                'uniformtext': {'mode': 'show', 'minsize': 16},
                'yaxis': {'automargin': True},
                'margin': {'t': 60, 'b': 40, 'l': 40, 'r': 20}
            }
        }
    }

def create_cohort_details_table(df_filtered):
    cohort_details = df_filtered.groupby(['Cohort', 'Level']).size().reset_index(name='Count')
    cohort_details['Year'] = cohort_details['Cohort'].str.extract(r'(\d{4})')
    cohort_details['Cohort'] = cohort_details['Cohort'].str.replace(r',?\s*\d{4}', '', regex=True)
    cohort_details['Cohort'] = cohort_details['Cohort'].str.replace(r'L-1|L-2|L1|L2', '', regex=True).str.strip(', ').str.strip()
    return cohort_details.to_dict('records')

@app.route('/')
def index():
        return render_template(
            'index.html',
            cohorts=['All'] + sorted(df['Cohort'].dropna().unique().tolist()),
            genders=['All'] + sorted(df['Gender'].dropna().unique().tolist()),
            categories=['All'] + sorted(df['Category'].dropna().unique().tolist()),
            technologies=['All'] + sorted(df['Technology'].dropna().unique().tolist()),
            employment_statuses=['All'] + sorted(df['Employment Status'].dropna().unique().tolist())
        )

@app.route('/api/initial_data', methods=['GET'])
def get_initial_data():
    cohorts = ['All'] + sorted(df['Cohort'].unique().tolist())
    genders = ['All'] + sorted(df['Gender'].unique().tolist())
    categories = ['All'] + sorted(df['Category'].unique().tolist())
    technologies = ['All'] + sorted(df['Technology'].unique().tolist())
    employment_statuses = ['All'] + sorted(df['Employment Status'].unique().tolist())
    
    return jsonify({
        'cohorts': cohorts,
        'genders': genders,
        'categories': categories,
        'technologies': technologies,
        'employment_statuses': employment_statuses
    })

@app.route('/api/data', methods=['GET'])
def get_filtered_data():
    # Correctly parse filter parameters
    cohort_filter = request.args.get('cohort')
    gender_filter = request.args.get('gender')
    category_filter = request.args.get('category')
    technology_filter = request.args.get('technology')
    employment_status_filter = request.args.get('employment_status')

    filtered_df = df.copy()
    
    if cohort_filter and cohort_filter != 'All':
        filtered_df = filtered_df[filtered_df['Cohort'].str.strip() == cohort_filter.strip()]
    if gender_filter and gender_filter != 'All':
        filtered_df = filtered_df[filtered_df['Gender'].str.strip() == gender_filter.strip()]
    if category_filter and category_filter != 'All':
        filtered_df = filtered_df[filtered_df['Category'].str.strip() == category_filter.strip()]
    if technology_filter and technology_filter != 'All':
        filtered_df = filtered_df[filtered_df['Technology'].str.strip() == technology_filter.strip()]
    if employment_status_filter and employment_status_filter != 'All':
        filtered_df = filtered_df[filtered_df['Employment Status'].str.strip() == employment_status_filter.strip()]

    response = {
        'total_participant_count': get_total_participant_count(filtered_df),
        'employment_chart_data': create_employment_status_chart(filtered_df),
        'technology_chart_data': create_technology_distribution_chart(filtered_df),
        'gender_category_chart_data': create_gender_category_analysis(filtered_df),
        'cohort_table_data': create_cohort_details_table(filtered_df)
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)