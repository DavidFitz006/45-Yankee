import streamlit as st
import pandas as pd
import webbrowser

# URL of the Google Sheets CSV export link
sheet_url = "https://docs.google.com/spreadsheets/d/1JZsnrbtk2y4hUrdEFkS9-zhlkiFzOKGjcju0QbYd3Hw/export?format=csv&gid=1607918864"

# Load the Google Sheet data into a pandas DataFrame
@st.cache_data(ttl=3600)
def load_data(url):
    return pd.read_csv(url)

df = load_data(sheet_url)

# Streamlit App Title
st.title("45 Yankee Attendance Report")

# Initialize attendance_summary to None
attendance_summary = None
operations_count = None

# Checking if required columns exist
if 'Attendance:' in df.columns and 'Operation or training:' in df.columns:
    # Create a list to store attendance data
    attendance_data = []

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Ensure the Attendance: column has a value before processing
        if pd.notna(row['Attendance:']):
            # Split names separated by commas, remove any leading/trailing spaces
            names = row['Attendance:'].split(',')
            names = [name.strip() for name in names]  # Clean up whitespace
            
            # Pair each name with its attendance type
            for name in names:
                attendance_data.append({'Name': name, 'Type': row['Operation or training:']})
    
    # Create a DataFrame to track attendance
    attendance_df = pd.DataFrame(attendance_data)
    
    # Count occurrences for each name in both categories
    total_attendance = attendance_df.groupby('Name').size().reset_index(name='Total Attendance')
    operation_attendance = attendance_df[attendance_df['Type'].str.contains("Operation", case=False, na=False)].groupby('Name').size().reset_index(name='Operation Attendance')
    training_attendance = attendance_df[attendance_df['Type'].str.contains("Training", case=False, na=False)].groupby('Name').size().reset_index(name='Training Attendance')
    
    # Merge the attendance counts into a single DataFrame
    attendance_summary = total_attendance.merge(operation_attendance, on='Name', how='left').merge(training_attendance, on='Name', how='left').fillna(0)
    
    # Calculate percentages
    attendance_summary['Operation Attendance'] = attendance_summary['Operation Attendance'].astype(int)
    attendance_summary['Training Attendance'] = attendance_summary['Training Attendance'].astype(int)
    
    attendance_summary['Operation %'] = ((attendance_summary['Operation Attendance'] / attendance_summary['Total Attendance']) * 100).round(0)
    attendance_summary['Training %'] = ((attendance_summary['Training Attendance'] / attendance_summary['Total Attendance']) * 100).round(0)

    # Convert the percentages to integers
    attendance_summary['Operation %'] = attendance_summary['Operation %'].astype(int)
    attendance_summary['Training %'] = attendance_summary['Training %'].astype(int)

    # Remove the Total Attendance column
    attendance_summary = attendance_summary[['Name', 'Operation %', 'Training %']]

    # Create a second table for operations/training comparison
    operation_count = df['Operation or training:'].nunique()  # Count of unique operations/trainings
    name_counts = df['Attendance:'].str.split(',').explode().str.strip().value_counts()  # Count attendance for each name
    
    operations_count = pd.DataFrame(name_counts).reset_index()
    operations_count.columns = ['Name', 'Attendance Count']
    
    # Calculate the percentage attendece
    operations_count['Operations/Training %'] = (operations_count['Attendance Count'] / operation_count * 100).round(0)

    # Convert percentages to integers
    operations_count['Operations/Training %'] = operations_count['Operations/Training %'].astype(int)

    # Display the Operations/Training comparison table
    st.subheader("Total Attendance Percentage")
    st.table(operations_count)

    # Display the attendance percentage table
    st.subheader("Operation to training ratio")
    st.table(attendance_summary)

else:
    st.error("The required columns are not found in the data.")

# Button to open Google Form
if st.button("Fill out the Attendance Form"):
    # Open the Google Form in a new tab
    webbrowser.open_new_tab("https://docs.google.com/forms/d/e/1FAIpQLScdtQchZhAaH_Y6wDvgHCw2O_GTsOgfC97YK_Dn4i5cBGrTpg/viewform")
