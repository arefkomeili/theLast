
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# تنظیمات احراز هویت
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('json.json', scope)
client = gspread.authorize(credentials)

# لینک به گوگل شیت شما
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1L0DWEUq95L7U38dccF49a8kKC49JGdehDL-N0EOE6vc/edit?usp=sharing"

# باز کردن شیت
spreadsheet = client.open_by_url(spreadsheet_url)
worksheet = spreadsheet.sheet1

# تابع برای خواندن داده‌ها از گوگل شیت
def read_data():
    try:
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error reading data: {e}")
        return pd.DataFrame(columns=['Task', 'Date', 'Completed'])

# تابع برای افزودن وظیفه جدید به گوگل شیت
def add_task(task):
    try:
        df = read_data()
        new_task = pd.DataFrame([[task, '', 'pending']], columns=['Task', 'Date', 'Completed'])
        updated_df = pd.concat([df, new_task], ignore_index=True)
        worksheet.update([updated_df.columns.values.tolist()] + updated_df.values.tolist())
        st.success('Task added successfully!')
        st.session_state.new_task_input = ""  # Clear the input field
        st.experimental_rerun()  # Rerun the app to refresh all parts
    except Exception as e:
        st.error(f"Error adding task: {e}")

# تابع برای ویرایش عنوان وظیفه
def edit_task(index, new_title):
    try:
        worksheet.update_cell(index + 2, 1, new_title)  # ستون عنوان
        st.success('Task title updated successfully!')
        st.experimental_rerun()  # Rerun the app to refresh all parts
    except Exception as e:
        st.error(f"Error editing task title: {e}")

# تابع برای تکمیل وظیفه
def complete_task(index):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.update_cell(index + 2, 2, current_time)  # ستون تاریخ و زمان
        worksheet.update_cell(index + 2, 3, 'done')  # ستون وضعیت
        st.success('Task completed successfully!')
        st.experimental_rerun()  # Rerun the app to refresh all parts
    except Exception as e:
        st.error(f"Error completing task: {e}")

# تابع برای حذف وظیفه
def delete_task(index):
    try:
        worksheet.delete_rows(index + 2)  # +2 به دلیل اینکه گوگل شیت از ردیف 1 شروع می‌شود و ردیف هدر هم وجود دارد
        st.success('Task deleted successfully!')
        st.experimental_rerun()  # Rerun the app to refresh all parts
    except Exception as e:
        st.error(f"Error deleting task: {e}")

# نمایش داده‌ها
st.header("Task Management App")
data = read_data()

# Initialize session state
if 'new_task_input' not in st.session_state:
    st.session_state.new_task_input = ""

# فرم برای افزودن وظیفه جدید
with st.form(key='add_form'):
    new_task = st.text_input('New Task', value=st.session_state.new_task_input)
    submit_button = st.form_submit_button(label='Add Task')

    if submit_button:
        add_task(new_task)

# نمایش لیستی از وظایف
st.header("Tasks List")
if len(data) > 0:
    for index, row in data.iterrows():
        task_text = row['Task']
        task_date = row['Date']
        is_completed = row['Completed'] == 'done'

        col1, col2, col3, col4 = st.columns([4, 3, 2, 2])

        with col1:
            new_task_title = st.text_input('Edit Task Title', value=task_text, key=f"edit_{index}")
            if st.button("Update Title", key=f"update_{index}"):
                edit_task(index, new_task_title)

        with col2:
            checkbox = st.checkbox(f"{task_text} (Completed on: {task_date})", value=is_completed, key=f"task_{index}")
        with col3:
            if st.button("Delete", key=f"delete_{index}"):
                delete_task(index)

        if checkbox and not is_completed:
            complete_task(index)
else:
    st.write("No tasks found.")

# نمایش داده‌ها به صورت جدول
st.header("Tasks Data")
st.dataframe(data)