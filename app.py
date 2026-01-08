import streamlit as st
import smtplib
import os
import pandas as pd
import plotly.express as px
import openai

# For gdp by region page
image_gdp_region=r"C:\Users\hp\Desktop\GDP and productivity of Indian cities\GDP_of_Indian_states.png"

# For sectoral productivity page
data = {
    'Year': [2019, 2020, 2021, 2022, 2023],
    'Agriculture': [13.35666667, 12.34666667, 11.84, 11.98666667, 12.55],
    'Manufacturing': [18.0, 18.5, 19.0, 19.3, 19.5],
    'ICT': [17.76666667, 14.63333333, 15.95666667, 15.06666667, 14.94666667],
    'Tourism': [7.54, 6.796666667, 6.686666667, 7.246666667, 6.726666667],
    'Employment': [26.44, 28.63, 24.92666667, 29.21666667, 25.92666667]
}
df_sector = pd.DataFrame(data)

#  For employment rates page
# Year-wise employment data
employment_data = {
    'Year': [2019, 2020, 2021, 2022, 2023],
    'Employment Rate': [26.44, 28.63, 24.92666667, 29.21666667, 25.92666667]
}
df_employment = pd.DataFrame(employment_data)

# Open AI key used for chat bot
openai.api_key = 'YOUR OPEN AI KEY'

# In-memory storage for users 
if "users" not in st.session_state:
    st.session_state.users = {"user1": "password123"}

# Track login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# Functions for login, sign-up, and sending feedback
def login(username, password):
    # Check if the username exists
    if username not in st.session_state.users:
        st.warning("Username doesn't exist. Please sign up.")
    elif st.session_state.users[username] != password:
        # If the password is incorrect
        st.warning("Incorrect password. Please try again.")
    else:
        # If login is successful
        st.session_state.logged_in = True
        st.session_state.current_user = username
        st.success("Logged in successfully!")

def signup(username, password):
    if username in st.session_state.users:
        st.warning("Username already exists. Please choose a different username.")
    else:
        st.session_state.users[username] = password
        st.success("Account created successfully! You can now log in.")

def send_feedback(subject, message, sender_email, receiver_email, smtp_server, smtp_port, smtp_user, smtp_pass):
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            email_body = f"Subject: {subject}\n\n{message}"
            server.sendmail(sender_email, receiver_email, email_body)
        st.success("Feedback sent successfully!")
    except Exception as e:
        st.error(f"Failed to send feedback: {e}")

# Function to generate GPT-3 responses
def get_gpt_response(query, context):
    prompt = f"""
    Below is the dataset:
    {context}

    Answer the question based on the dataset:
    {query}
    """
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        # max_tokens=150,
        temperature=0.7
    )

    answer = response.choices[0].message.content.strip()

    return answer
    
# Handles login/signup process and show dashboard only when logged in
if not st.session_state.logged_in:
    # Login and Signup page
    st.title("Welcome to the GDP and Productivity Dashboard")

    auth_option = st.selectbox("Choose an option", ["Login", "Sign Up"])

    if auth_option == "Login":
        st.header("Login Page")
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            login(username_input, password_input)

    elif auth_option == "Sign Up":
        st.header("Sign Up Page")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        signup_button = st.button("Sign Up")

        if signup_button:
            signup(new_username, new_password)

else:
    # Once logged in, show the dashboard
    st.sidebar.success(f"Welcome, {st.session_state.current_user}!")

    # Custom CSS for sidebar and wider content area
    sidebar_width = 300  
    content_width = "100%"  

    # Custom CSS for layout
    st.markdown(f"""
        <style>
        /* Increase the sidebar width */
        .css-1d391kg {{
            width: {sidebar_width}px;
        }}
        /* Increase the content area width */
        .css-1outpf8 {{
            width: {content_width};
            margin-left: {sidebar_width}px; /* Make space for the sidebar */
        }}
        /* Optional: Style sidebar header */
        .css-1fzr9py {{
            font-size: 20px;
            font-weight: bold;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Sidebar for navigation
    nav_buttons = ["Overview", "GDP by Region", "Sectoral Productivity", "Employment Rates", "Economic Indicators", "Forecasts and Trends", "Feedback"]
    nav_button = st.sidebar.radio("Navigation", nav_buttons)

    st.title("GDP and Productivity Dashboard")

    df = pd.read_csv(r'C:\Users\hp\Desktop\GDP and productivity of Indian cities\Economy_Productivity_SD_India_Final.csv')
    
    if nav_button == "Overview":
        st.header("Overview of GDP and Productivity")
        st.write("""
            **Gross Domestic Product (GDP)** is the total value of all goods and services produced in a country during a specific period. 
            It is a primary indicator used to gauge the economic health of a nation and measure its productivity. 
            
            **Productivity** refers to the efficiency of production, measured as the ratio of output (goods/services) to input (labor, capital, etc.). 
            A higher productivity level typically correlates with economic growth, higher wages, and improved standards of living.
            
            In this dashboard, you will explore how different sectors contribute to the GDP of various regions in India, 
            along with how productivity is measured and tracked across industries like agriculture, ICT, and manufacturing.
        """)
        # Power bi Dashboard
        dashboard_url = "Power BI dashboard URL"
        st.markdown(f"""
            <iframe src="{dashboard_url}" width="100%" height="450px" frameborder="0" allowFullScreen="true"></iframe>
        """, unsafe_allow_html=True)
        
        # Chatbot section 
        st.subheader("Ask the Chatbot Anything About the Data")
        
        user_input = st.text_input("Ask a question about the GDP or productivity data:")

        if user_input:
            with st.spinner("Processing your request..."):
                # Use the first 100 rows of the dataframe as context
                context = df.head(100).to_string(index=False)
                answer = get_gpt_response(user_input, context)
                st.write("### Answer:")
                st.write(answer)

    elif nav_button == "GDP by Region":
        st.header("GDP by Region")
        st.write("""
            India has a diverse economic landscape, with each region contributing differently to the nation's GDP. 
            The primary regions for economic activity in India are North, South, East, and West. These regions have distinct economic strengths, 
            which influence their contribution to the national GDP.
            
            - **North**: Includes states like Uttar Pradesh, Punjab, and Delhi, which have a strong presence in agriculture, services, and manufacturing.
            - **South**: Includes states like Tamil Nadu, Karnataka, and Andhra Pradesh, known for their high productivity in sectors like IT, agriculture, and services.
            - **East**: Includes states like West Bengal, Odisha, and Bihar, with a focus on manufacturing, mining, and agriculture.
            - **West**: Includes Maharashtra, Gujarat, and Rajasthan, which have thriving industries in manufacturing, services, and trade.
            
            The analysis here highlights how each region's economic activities contribute to overall GDP growth.
            
        """)
        if os.path.exists(image_gdp_region):
            st.image(image_gdp_region, caption="Metropolitan Areas GDP", use_container_width=True)
        else:
            st.warning("Image not found. Please provide the correct path.")
        
        st.write(""" 
            - **Metropolitan areas**: The search results do not provide a comprehensive list of Indian cities by GDP. However, one snippet mentions that Mumbai had a gross domestic product (GDP) of $310 billion in 2023, making it the highest among other major cities in India. 
            - **State-wise GDP**: The search results provide lists of Indian states and union territories by their nominal gross state domestic product (GSDP) at current prices in millions or trillions of Indian rupees. The lists cover various years, including 2011-12 to 2022-23 and 2001-02 to 2010-11. 
            - **City-wise GDP**: The search results do not provide a direct list of Indian cities by GDP. However, one snippet mentions the top 10 richest cities in India based on GDP in 2024, but the ranking and figures are not provided. 
            - **Regional GDP**: The search results do not provide a breakdown of GDP by region (e.g., north, south, east, west) of Indian cities. However, some snippets mention the population and GDP of major cities in India, such as Delhi, Mumbai, Kolkata, Bangalore, and Hyderabad.
        """)

    elif nav_button == "Sectoral Productivity":
        st.header("Sectoral Productivity")
        st.write("""
            Productivity can be analyzed at the sectoral level to understand how efficiently different industries contribute to GDP. 
            Major sectors that influence productivity in India include:
            
            - **Agriculture**: Despite a large portion of the population being employed in agriculture, it contributes a smaller share to GDP.
            - **Manufacturing**: Key to India's industrial growth, including automotive, textiles, and heavy industries.
            - **ICT (Information and Communication Technology)**: The IT sector has experienced rapid growth, contributing significantly to GDP and employment.
            - **Services**: This sector, including finance, education, healthcare, and hospitality, is the largest contributor to India's GDP.
            
            Understanding sectoral productivity allows policymakers to target areas of growth and development.
        """)
        # Sector selection
        sector = st.selectbox("Select a sector to view its productivity trends", ["Agriculture", "Manufacturing", "ICT", "Tourism", "Employment"])

        # Show line chart of sectoral productivity
        fig = px.line(df_sector, x='Year', y=sector, title=f"{sector} Productivity Over Years", labels={'value': f'{sector} Productivity (%)'})
        st.plotly_chart(fig)

        # Additional insights based on selected sector
        if sector == "Agriculture":
            st.write("""
                Agriculture remains one of the largest employers in India, but its contribution to GDP has been declining 
                due to factors like urbanization, reduced arable land, and modern technology.
            """)
        elif sector == "Manufacturing":
            st.write("""
                Manufacturing plays a crucial role in driving industrial growth in India. Sectors such as automotive, textiles, and heavy machinery 
                continue to grow, though challenges like labor costs and automation are changing the landscape.
            """)
        elif sector == "ICT":
            st.write("""
                The ICT sector has experienced rapid growth, contributing significantly to India's GDP. The rise of digital technologies 
                and software services have made India a global hub for IT outsourcing.
            """)
        elif sector == "Tourism":
            st.write("""
                Tourism is a growing sector in India, with its contribution to the economy being driven by both domestic and international tourism. 
                The rise of travel and hospitality services has led to an increase in employment and economic activity in tourism-related regions.
            """)
        elif sector == "Employment":
            st.write("""
                Employment trends in India show variation across sectors. While the services and ICT sectors are seeing growth, 
                agriculture and manufacturing face challenges due to changing market dynamics and technology adoption.
            """)

        # bar chart for comparing sectoral contribution over the years
        st.write("Sectoral Contribution to GDP (by Year):")
        fig2 = px.bar(df_sector, x='Year', y=['Agriculture', 'Manufacturing', 'ICT', 'Tourism', 'Employment'], barmode='group', title="Sectoral Contribution to GDP and Employment")
        st.plotly_chart(fig2)
        
        st.write("""
                Understanding sectoral productivity helps policymakers focus on areas of potential growth and improvement. 
                For example, the ICT sector's rise has been driven by increasing internet penetration and tech innovations, 
                while the decline in agriculture’s share of GDP signals the need for innovation in farming practices.
        """)

    elif nav_button == "Employment Rates":
        st.header("Employment Rates and Unemployment")
        st.write("""
            Employment rates are crucial indicators of economic health. This section covers various employment metrics, including:
            
            - **Youth Unemployment**: Youth unemployment remains a major challenge in India, with many young people struggling to find stable employment.
            - **SME Employment**: Small and medium-sized enterprises (SMEs) are significant employers, particularly in rural and semi-urban areas.
            - **Tourism Sector Employment**: The tourism sector is a major employer, providing jobs in hospitality, transportation, and entertainment.
            - **ICT Sector Employment**: The IT sector continues to be one of the largest employers, providing skilled jobs in technology and services.
            
            Tracking employment rates across these sectors is vital for understanding economic inclusivity and areas requiring intervention.
        """)
        # bar chart for employment rate
        fig = px.bar(df_employment, x='Year', y='Employment Rate', 
                    title="Year-wise Employment Rate (2019-2023)", 
                    labels={'Employment Rate': 'Employment Rate (%)'})

        st.plotly_chart(fig)
        
        st.write("""
            ## Urban Areas (2023) - Unemployment Rates
            - **Himachal Pradesh**: 14.1% (highest unemployment rate in urban India)
            - **Andaman & Nicobar Islands**: 12.9%
            - **Punjab**: 12.4%
            - **Uttar Pradesh**: 11.9%
            - **Maharashtra**: 11.5%
            - **Delhi**: 10.9%
            - **Tamil Nadu**: 10.5%
            - **Karnataka**: 10.2%
            - **Andhra Pradesh**: 9.8%
            - **Telangana**: 9.5%
            ---
            ## Regional Variations
            Youth unemployment rates vary significantly across states and Union Territories (UTs). For example:
            - **Kerala** has one of the highest youth unemployment rates at **23.1%**.
            - **Madhya Pradesh** has one of the lowest at **6.4%**.
            Urban women generally experience a higher unemployment rate than rural women in India.
            ---
            
            ## Policy Implications
            The varying employment rates across cities and regions highlight the need for targeted policy measures to address economic challenges and promote sustainable growth.
            - **Diversifying economic activities** and creating more **employment opportunities** are crucial to bolstering India’s financial resilience.
        """)

    elif nav_button == "Economic Indicators":
        st.header("Key Economic Indicators")
        st.write("""
            Economic indicators provide insights into a country's economic performance. In this section, we examine:
            
            - **GDP Growth Rate**: Measures the increase in the value of goods and services produced by an economy.
            - **Inflation Rate**: Indicates the rate at which the general level of prices for goods and services is rising, leading to a decrease in purchasing power.
            - **Fiscal Deficit**: The difference between the government's total expenditure and total revenue.
            - **Exchange Rates**: The value of the Indian Rupee in comparison to other global currencies, affecting trade and foreign investments.
            
            These indicators are critical for decision-making by policymakers, investors, and businesses.
        """)
        st.image(r"C:\Users\hp\Desktop\GDP and productivity of Indian cities\economic_indicator.jpg", caption="India's Economic Growth", use_container_width=True)

        st.write("""
            ## Additional Insights

            - **GDP Growth Rates**: GDP growth rates can indicate economic expansion or contraction, while changes in GDP composition can reveal shifts in economic activity.
            - **Earnings Reports**: Earnings reports can signal business confidence and investment opportunities.
            - **Economic Indices**: Indices can identify inflationary pressures and potential economic imbalances.
            - **Government Budgets**: Central government budgets can influence fiscal policy and economic stability.
            - **International Trade Data**: International trade data can reveal trade patterns and potential vulnerabilities.

            ---

            ## Timeliness and Frequency

            - GDP is typically released quarterly, while earnings reports and indices are published more frequently, often monthly or weekly.
            - Central government budgets and international trade data may be released less frequently, often annually or quarterly.

            ---

            ## Interpretation and Analysis

            Economic indicators should be analyzed in conjunction with each other and considered within the context of broader economic trends and policies. This enables a more comprehensive understanding of an economy’s performance and potential future directions.
        """)

    elif nav_button == "Forecasts and Trends":
        st.header("GDP and Productivity Forecasts")
        st.write("""
            Future projections play a critical role in shaping economic policies and business strategies. 
            In this section, we will analyze:
            
            - **GDP Forecast**: Projected GDP growth based on current trends, government policies, and global economic conditions.
            - **Productivity Trends**: How sectors like IT, agriculture, and manufacturing are expected to perform in the coming years.
            - **Sectoral Shifts**: Shifts in economic activity, such as the rise of the digital economy, green energy, and automation.
            
            These forecasts help stakeholders plan for challenges and opportunities that lie ahead.
        """)
        st.write("""
            ## India GDP and Productivity Forecasts

            - The World Bank expects India’s medium-term outlook to remain positive, with growth forecast to reach **7 percent** in FY24/25 and remain strong in FY25/26 and FY26/27.
            - Treasury projections indicate an average annual growth rate of around **6 percent** over the next two decades, driven primarily by improved productivity.
            - India’s GDP growth is expected to be driven by robust revenue growth and further fiscal consolidation, leading to a decline in the debt-to-GDP ratio from **83.9 percent** in FY23/24 to **82 percent** by FY26/27.

            ---

            ## Productivity Trends in India

            - According to the McKinsey Global Institute, India needs to boost its rate of employment growth and create **90 million non-farm jobs** between 2023 to 2030 to increase productivity and economic growth.
            - To achieve **8-8.5% GDP growth** between 2023 to 2030, the net employment rate needs to grow by **1.5%** per annum.

            ---

            ## Export and Import Trends

            - India’s exports, goods and services, are expected to grow at a slower pace, with a forecast of **2.6%** in FY23/24 and **7.2%** in FY24/25.
            - Imports, goods and services, are expected to decline slightly, with a forecast of **10.9%** in FY23/24 and **4.1%** in FY24/25.
        """)

    elif nav_button == "Feedback":
        st.header("Feedback Form")
        st.write("""
        We value your feedback! Please let us know your thoughts on the dashboard, its content, and any improvements you'd like to see.
        """)
        subject = st.text_input("Subject")
        message = st.text_area("Message")
        if st.button("Submit Feedback"):
            
            smtp_server = "SERVER_MAIL_ID"
            smtp_port = "PORT_NO"
            smtp_user = "USER_ID"
            smtp_pass = "YOUR_SMTP_PASS"
            sender_email = "your_sender_email"
            receiver_email = "your_receiver_email"

            if not subject or not message:
                st.warning("Please fill in both subject and message.")
            else:
                send_feedback(subject, message, sender_email, receiver_email, smtp_server, smtp_port, smtp_user, smtp_pass)

    # Logout button
    if st.sidebar.button("Logout"):
        # Reset session states
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.sidebar.success("You have been logged out.")
