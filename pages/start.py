import streamlit as st
import sys
sys.path.append("src")
from ui import render_sidebar

st.title("Financial Visualiazer")

ticker_selected = render_sidebar()