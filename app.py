import streamlit as st
st.set_page_config(page_title="Financial Visualiazer", page_icon="📊", layout="centered")

pg = st.navigation([
    st.Page("pages/start.py", title="Financial Visualiazer", default=True),
])

pg.run()