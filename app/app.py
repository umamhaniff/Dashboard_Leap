import streamlit as st

# Ini cara masukin CSS custom
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .custom-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #ff4b4b;
    }
    </style>
    """, unsafe_allow_html=True)

# Ini cara manggil HTML-nya
st.markdown('<div class="custom-card"><h3>Halo Resti!</h3>Ini adalah card custom pake CSS.</div>', unsafe_allow_html=True)