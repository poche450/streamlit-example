import streamlit as st
import pandas as pd
import sqlite3
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Compensation Tool", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
# 1. as sidebar menu
with st.sidebar:
    selected = option_menu("Compensation Tool Menu", ["Pharmacy Compensation Benchmarking Tool", 'Model Calibration'], 
        icons=['heart-pulse', 'cash-coin', 'cart4', 'calculator-fill', 'graph-up-arrow'], menu_icon="bar-chart-steps", default_index=0)

if selected == "Pharmacy Compensation Benchmarking Tool":
    # Database fetch function
    def fetch_data(query):
        conn = sqlite3.connect('PharmDB4.db')
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    # UI
    st.title("Pharmacy Pay Rates Tool")
    with st.expander("**:warning: Instruction and Methodology :information_source:**"):
            
            st.info("The **OBJECTIVE** of this tool is to assist you in the salaly positioning process for Pharmacy Manager and Pharmacist.")
            st.info("The **OUTCOME** of this tool is to support people Leader who utilize the salary positioning Excel spreadsheet in determining the appropriate pay for all Pharmacy Managers and Pharmacist roles, ensureing  pay equity and competitiveness at an affordable cost.")
            st.warning("Familiarize yourself with the three demensional approach to targeting ideal pay positioning; **1) Market**, **2) Pharmacy complexity** & **3) Individual competency**")
            tabMarket, tabComplexity, tabCompetency = st.tabs(["**Market**","**Pharmacy Complexity**", "**Individual Competency**"])
            with tabMarket:
                st.write("""The salary range for each position considers the regional market or location of the pharmacy in which the Staff Pharmacists and Pharmacy Managers are assigned to.Each pharmacy location is ranked based on the market specific to the province and the type of labor market in which it is located:""")
                st.write("""**Zone 1** – cities with market rates higher than the provincial average where rates are driven by demand with less supply of pharmacists""")
                st.write("""**Zone 2** – cities with stable market rates on par with the provincial average""")
                st.write("""**Zone 3** – cities with less market pressures and stable rates, generally in urban centers with surplus of pharmacist and rates are lower than the national average – ie. GTA, Cities with Pharmacy Programs")""")
            with tabComplexity:
                st.write("Each Pharmacy location is ranked based on their store’s complexity.")
                st.write("RX Count was considered when ranking these pharmacies . (**High:** above 1,600; **Medium-High:** 1,200 to 15,999, **Medium:** 800 to 1,200 and **Low:** less than 800).")
            with tabCompetency:
                st.write("Individual skills, competency level is used to determine each employees ranking (**New/Minimal, Competent, Embracing Full Scope, Star/Expert**) in order to establish appropriate pay positioning in their relevant market. Distributions by rating are also included below as a directional guage.")
                st.write("**(5%) New/ Minimal** - Pharmacist with less than one year service or is continuing to build upon the core competencies of the job")
                st.write("**(50%) - Competent** - A proficient & seasoned Pharmacist that may or may not be acquiring additional certifications")
                st.write("**(30%) Embracing Full Scope** - Has achieved advanced clinical proficiency. May have attained several additional certifications and continues to excel in Professional Services, in addition to core dispensing duties")
                st.write("**(15%) Star/Expert** - A subject matter expert with a wider strategic focus. May be called upon to provide authoritative advice to Leadership team. A strong people leader. Possibly on succession plans and ready to move into the next level (if desired)")
                
    colPharm1, colPharm2 = st.columns(2)
    with colPharm1:
        st.header(':hospital: Pharmacy Selection')
        
        
        
        colProv, colLoc = st.columns(2)
        with colProv:
            province = st.selectbox("Select a Province", fetch_data("SELECT DISTINCT Province FROM locations")['Province'].tolist())
        with colLoc:
            location = st.selectbox("Select a Location", fetch_data(f"SELECT DISTINCT Location FROM locations WHERE Province='{province}'")['Location'].tolist())

        # Fetch and display data about selected location
        location_data = fetch_data(f"SELECT * FROM locations WHERE Location='{location}'")
        st.subheader(':bookmark_tabs: Pharmacy Information')
        colPharminfo1, colPharmInfo2, colPharmInfo3 = st.columns(3)
        with colPharminfo1:
            st.write(f"**City: {location_data['City'].values[0]}**")
            
        with colPharmInfo2:
            st.write(f"**Zone: {location_data['Zone'].values[0]}**")
        with colPharmInfo3:
            st.write(f"**Complexity: {location_data['Complexity'].values[0]}**")
    with colPharm2:
        st.header(':bar_chart: Job Benchmark')
        colJob, colTitle = st.columns(2)
        with colJob:
            role_type = st.selectbox("Select Role Type", fetch_data("SELECT DISTINCT `Role Type` FROM marketRates")['Role Type'].tolist())
            scope = st.selectbox("Select Scope", fetch_data("SELECT DISTINCT Scope FROM `Compa-Ratio`")['Scope'].tolist())
        with colTitle:
                position_name = st.text_input("Enter Position Name")
                current_pay_rate = st.number_input("Enter Current Pay Rate", min_value=0.0, format="%.2f", step=0.01, help="Please Enter the Current or Expected Hourly Rate of Pay")
        

        # Fetch data based on selections
        provLoc = location_data['Province'].values[0]
        locZone = location_data['Zone'].values[0]
        locComp = location_data['Complexity'].values[0]
    market_rates_data = fetch_data(f"SELECT * FROM marketRates WHERE `Role Type`='{role_type}' AND Province='{provLoc}' AND Zone='{locZone}'")
    compa_ratio_data = fetch_data(f"SELECT * FROM `Compa-Ratio` WHERE Complexity='{locComp}' AND Scope='{scope}'")
  
    # Calculate hiring rate, salary range and compa-ratio

    if market_rates_data.empty or compa_ratio_data.empty:
        st.write("No data available for the selected options.")
    else:
        
        min_salary_range = market_rates_data['Low'].values[0]
        max_salary_range = market_rates_data['High'].values[0]
        compa_ratio = compa_ratio_data['Ratio'].values[0]
        hiring_rate = market_rates_data['Mid'].values[0] * compa_ratio_data['Ratio'].values[0]
        
    

        st.subheader(':heavy_dollar_sign: Compensation Details')
       
        
        col1, col2, col3, col4=st.columns(4)
        
        with col1:
            st.subheader('Compa-Ratio')
            st.metric('label1', f"{compa_ratio*100:.2f}%", label_visibility= "hidden")
        with col2:
            st.subheader('Hiring Rate')
            st.metric('label2', f"${hiring_rate:.2f}", label_visibility= "hidden")
        with col3:
            st.subheader('Salary Range')
            st.metric('label3', f"${min_salary_range:.2f} - ${max_salary_range:.2f}", label_visibility= "hidden")
        
        if current_pay_rate != 0:
            with col4:
                salary_increase = max(0,hiring_rate-current_pay_rate)
                salary_increase_perc = salary_increase/current_pay_rate
                st.subheader('Salary Increase')
                st.metric('label4', f"${salary_increase:.2f} - {salary_increase_perc*100:.2f}%", label_visibility= "hidden")
