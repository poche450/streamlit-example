import streamlit as st
import pandas as pd
import sqlite3
from streamlit_option_menu import option_menu


st.set_page_config(page_title="Compensation Tool", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
# 1. as sidebar menu
with st.sidebar:
    selected = option_menu("Compensation Tool Menu", ["Pharmacy Compensation Tool", 'Pay Equity Tool', 'Retail Compensation Tool', 'Wage Scale Costing Tool', 'Planning & Forecasting'], 
        icons=['heart-pulse', 'cash-coin', 'cart4', 'calculator-fill', 'graph-up-arrow'], menu_icon="bar-chart-steps", default_index=1)

if selected == "Pharmacy Compensation Tool":
    # Database fetch function
    def fetch_data(query):
        conn = sqlite3.connect('pharmacy_data.db')
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    # UI
    st.title("Pharmacy Pay Rates Tool")
    st.info('Info message')

    st.header('Pharmacy Selection')
    province = st.selectbox("Select a Province", fetch_data("SELECT DISTINCT province FROM pay_rates")['province'].tolist())
    location = st.selectbox("Select a Location", fetch_data(f"SELECT DISTINCT location FROM pay_rates WHERE province='{province}'")['location'].tolist())
    st.header('Job Benchmark')
    role_type = st.selectbox("Select Role Type", fetch_data("SELECT DISTINCT role_type FROM pay_rates")['role_type'].tolist())
    competency_level = st.selectbox("Select Competency Level", fetch_data("SELECT DISTINCT competency_level FROM pay_rates")['competency_level'].tolist())

    st.warning('Warning message')


    # Fetch and display data
    df = fetch_data(f"SELECT * FROM pay_rates WHERE province='{province}' AND location='{location}' AND role_type='{role_type}' AND competency_level='{competency_level}'")
    dfProvOnly = fetch_data(f"SELECT * FROM pay_rates WHERE province='{province}' AND role_type='{role_type}' AND competency_level='{competency_level}'")
   
    if df.empty:
        st.write("No data available for the selected options.")
    else:
        # calculate hiring rate, salary range and compa-ratio
        df['hiring_rate'] = df['pay_rate']*0.9
        df['min_salary_range'] = df['pay_rate']*0.8
        df['max_salary_range'] = df['pay_rate']*1.2
        df['compa_ratio'] = df['pay_rate']/df['max_salary_range']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader('Compa-Ratio')
            st.metric('label1',f"{df['compa_ratio'].mean()*100:.2f}%", -2,label_visibility= "hidden")
        with col2:    
            
            st.subheader('Hiring Rate')
            st.metric('label2',f"${df['hiring_rate'].mean():.2f}", (df['hiring_rate'].mean()-dfProvOnly['pay_rate'].mean())/dfProvOnly['pay_rate'].mean(),label_visibility = "hidden")
        with col3:    
            
            st.subheader('Salary Range')
            st.metric('label3',f"${df['min_salary_range'].mean():.2f} - ${df['max_salary_range'].mean():.2f}", -2,label_visibility = "hidden")
if selected == "Pay Equity Tool":
        # Database fetch function
    def fetch_data(query):
        conn = sqlite3.connect('questionnaire_datac.db')
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    # Database update function
    def update_data(query, data):
        conn = sqlite3.connect('questionnaire_datac.db')
        c = conn.cursor()
        c.execute(query, data)
        conn.commit()
        conn.close()
    # Initialize the session state variables if they don't exist
    if 'job_counter' not in st.session_state:
        st.session_state['job_counter'] = 0
    if 'jobs_df' not in st.session_state:
        st.session_state['jobs_df'] = pd.DataFrame()

    # UI
    
    st.title("Job Evaluation Questionnaire Builder")
    tab1, tab2 = st.columns(2)
    with tab1:
        # Create Questionnaire
        with st.form("Create Questionnaire"):
            st.text("Enter Questionnaire Details")
            questionnaire_name = st.text_input("Questionnaire Name")

            if st.form_submit_button("Create Questionnaire"):
                update_data("INSERT INTO Questionnaires (name) VALUES (?)", (questionnaire_name,))

        # Create Factors and Subfactors
        with st.form("Create Factors and Subfactors"):
            st.text("Enter Factor and Subfactor Details")
            questionnaire_id = st.selectbox("Select Questionnaire", options=fetch_data("SELECT * FROM Questionnaires")['id'].tolist())
            factor_name = st.text_input("Factor Name")
            subfactor_name = st.text_input("Subfactor Name")
            level = st.number_input("Level")
            points = st.number_input("Points")

            if st.form_submit_button("Create Factor and Subfactor"):
                update_data("INSERT INTO Factors (name, questionnaire_id) VALUES (?, ?)", (factor_name, questionnaire_id,))
                factor_id = fetch_data(f"SELECT id FROM Factors WHERE name='{factor_name}' AND questionnaire_id={questionnaire_id}")['id'].tolist()[0]
                update_data("INSERT INTO Subfactors (name, factor_id) VALUES (?, ?)", (subfactor_name, factor_id,))
                subfactor_id = fetch_data(f"SELECT id FROM Subfactors WHERE name='{subfactor_name}' AND factor_id={factor_id}")['id'].tolist()[0]
                update_data("INSERT INTO Levels (level, points, subfactor_id) VALUES (?, ?, ?)", (level, points, subfactor_id,))
    with tab2:
        # Create Job and Evaluate
        with st.form("Evaluate Jobs"):
            st.text("Upload Jobs for Evaluation")
            questionnaire_id = st.selectbox("Select Questionnaire for Evaluation", options=fetch_data("SELECT * FROM Questionnaires")['id'].tolist())

            if st.session_state.jobs_df.empty:
                jobs_file = st.file_uploader("Upload jobs file (CSV format)")
                

                
                if jobs_file is not None:
                    st.session_state.jobs_df = pd.read_csv(jobs_file)
                    

            
            if not st.session_state.jobs_df.empty and st.session_state.job_counter < len(st.session_state.jobs_df):
                job_name = st.session_state.jobs_df.iloc[st.session_state.job_counter]['job_name']  # Assumes 'job_name' is the column containing the job names
                st.subheader(f"Evaluating job: {job_name}")
                total_points = int(0)

                # Fetch Factors and Subfactors for selected Questionnaire
                factors = fetch_data(f"SELECT * FROM Factors WHERE questionnaire_id={questionnaire_id}")
                for _, factor in factors.iterrows():
                    st.text(f"Factor: {factor['name']}")
                    subfactors = fetch_data(f"SELECT * FROM Subfactors WHERE factor_id={factor['id']}")
                    for _, subfactor in subfactors.iterrows():
                        st.text(f"Subfactor: {subfactor['name']}")
                        levels = fetch_data(f"SELECT * FROM Levels WHERE subfactor_id={subfactor['id']}")
                        level = st.select_slider(f"Choose level for {subfactor['name']}", options=levels['level'].tolist(), format_func=int)
                        points = levels[levels['level'] == level]['points'].values[0]
                        total_points += points
                    

                
                if st.form_submit_button(f"Save Evaluation for {job_name}"):
                    st.success(f"{job_name} evaluated successfully!")
                    # Create Job
                    
                    update_data("INSERT INTO Jobs (name, questionnaire_id, total_points) VALUES (?, ?, ?)", (job_name, questionnaire_id, int(total_points),))
                    st.session_state.job_counter += 1

            elif not st.session_state.jobs_df.empty and st.session_state.job_counter >= len(st.session_state.jobs_df):
                st.success("All jobs evaluated successfully!")
            if st.session_state.jobs_df.empty and st.form_submit_button(f"Load"): pass
            if st.form_submit_button(f"Complete",disabled=True):    pass
if selected == "Wage Scale Costing Tool":
        def get_next_level_pay_rate(ps_group, psub_area, current_rate):
            # Fetch corresponding wage scale
            wage_scale = wage_data.loc[(wage_data['ps_group'] == ps_group) &
                                        (wage_data['province'] == psub_area)]
            
            # Sort wage scale by pay rate
            wage_scale = wage_scale.sort_values('payRate')

            # Find the current rate and get the next level pay rate
            current_level_index = wage_scale[wage_scale['payRate'] == current_rate].index[0]
            
            try:
                next_level_pay_rate = wage_scale.loc[current_level_index + 1, 'payRate']
                return next_level_pay_rate
            except IndexError:
                # Return None if there is no next level
                return None
        def fetch_wage_data(query, conn):
            df = pd.read_sql_query(query, conn)
            return df

        def calculate_costs(wage_df, ee_df):

            # Fetch wage scale and employee data from database
            wage_scale_df = wage_df
            employee_df = ee_df

            # Initialize total cost variables
            total_cost_min_wage = 0
            total_cost_structure = 0
            total_cost_top_rate = 0
            total_cost_progression = 0

            # Define parameters
            minimum_wage = 10.5  # specify minimum wage value
            structure_increase_percentage = 0.02  # specify structure increase percentage
            new_top_rate = 15  # specify new top rate
            work_weeks_per_year = 52  # assumed work weeks in a year

            # Iterate over employees
            for idx, row in employee_df.iterrows():

                # Fetch employee info
                current_rate = row['Pay Rate']
                weekly_hours = row['Weekly Hours']
                
                # Calculate cost increase due to minimum wage
                if current_rate < minimum_wage:
                    cost_increase_min_wage = (minimum_wage - current_rate) * weekly_hours * work_weeks_per_year
                else:
                    cost_increase_min_wage = 0
                total_cost_min_wage += cost_increase_min_wage

                # Calculate cost increase due to structure increase
                cost_increase_structure = current_rate * structure_increase_percentage * weekly_hours * work_weeks_per_year
                total_cost_structure += cost_increase_structure

                # Calculate cost increase due to top rate increase
                max_rate = wage_data.loc[(wage_data['ps_group'] == row['ps_group']) &
                                            (employee_data['province'] == row['province']), 'payRate'].max()
                if current_rate == max_rate:
                    cost_increase_top_rate = (new_top_rate - current_rate) * weekly_hours * work_weeks_per_year
                else:
                    cost_increase_top_rate = 0
                total_cost_top_rate += cost_increase_top_rate

                # Estimate cost increase due to progression
                next_level_pay_rate = get_next_level_pay_rate(row['ps_group'], row['province'], current_rate)
                if next_level_pay_rate is not None:
                    cost_increase_progression = (next_level_pay_rate - current_rate) * weekly_hours * work_weeks_per_year
                else:
                    cost_increase_progression = 0
                total_cost_progression += cost_increase_progression

            # Return cost summaries
            return {
                'total_cost_min_wage': total_cost_min_wage,
                'total_cost_structure': total_cost_structure,
                'total_cost_top_rate': total_cost_top_rate,
                'total_cost_progression': total_cost_progression
            }


        # Part 1: Upload Wage Scale data
        st.title("Wage Scale Costing Software")
        # Part 1: Upload or Select Wage Scale data
        st.header("Part 1: Wage Scale Data")

        # Connect to the database
        conn = sqlite3.connect('salary_data.db')

        # Fetch existing wage scales
        existing_scales = fetch_wage_data("SELECT DISTINCT `ps_group` FROM wage_scales", conn)['ps_group'].tolist()

        # Show add wage scale button
        uploaded_file = st.file_uploader("Add a new Wage Scale CSV file", type="csv")
        if uploaded_file is not None:
            wage_data = pd.read_csv(uploaded_file)
            wage_data.to_sql('wage_scales', conn, if_exists='append', index=False)
            st.write("Wage Scale Data Uploaded Successfully")

        # If any wage scales exist, allow the user to select one
        if existing_scales:
            selected_scale = st.selectbox("Select a Wage Scale", existing_scales)
            if selected_scale:
                df_scale = fetch_wage_data(f"SELECT * FROM wage_scales WHERE `ps_group`='{selected_scale}'", conn)
                st.write(df_scale)
                
                # Show remove button
                if st.button('Remove Wage Scale'):
                    conn.execute(f"DELETE FROM wage_scales WHERE `ps_group`='{selected_scale}'")
                    conn.commit()
                    st.write("Wage Scale Removed Successfully")
                
                # Show modify button
                if st.button('Modify Wage Scale'):
                    # Here you might want to add a form for the user to edit the wage scale data
                    st.write("Modify functionality not yet implemented")

        conn.close()

        # Part 2: Upload Employee Data
        st.header("Part 2: Employee Data")
        uploaded_file = st.file_uploader("Choose an Employee CSV file", type="csv")
        if uploaded_file is not None:
            employee_data = pd.read_csv(uploaded_file)
            conn = sqlite3.connect('salary_data.db')
            employee_data.to_sql('employees', conn, if_exists='replace', index=False)
            conn.close()
            st.write("Employee Data Uploaded Successfully")

        # Part 3: Calculate and Display Costs
        st.header("Part 3: Cost Calculation")
        conn = sqlite3.connect('salary_data.db')
        wage_data = fetch_wage_data("SELECT * FROM wage_scales", conn)
        employee_data = fetch_wage_data("SELECT * FROM employees", conn)
        conn.close()
        print(wage_data)
        print(employee_data)
        if not wage_data.empty and not employee_data.empty:
            st.subheader('Cost Calculation Summary')
            st.write(calculate_costs(wage_data, employee_data))
        else:
            st.write("Please upload both Wage Scale and Employee data to calculate costs.")

