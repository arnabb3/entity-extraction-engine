import streamlit as st
import pandas as pd
import os

# Set page theme and title
st.set_page_config(
    page_title="E3: Entity Extraction Engine",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "E3 is a Streamlit-based web app that lets users upload text datasets and explore entity-level sentiment or rating trends. Whether you're analyzing food reviews, music comments, or news headlines, E3 helps visualize how entities are mentioned, perceived, and rated.",
    }
)

st.markdown("<h1 style='text-align: center;'>🔍 E3: Entity Extraction Engine</h1>", unsafe_allow_html=True)

## Page 1
# source
st.header("Choose Your Dataset", divider="blue")

data_option = st.radio("How would you like to load data?", ("Use default (Indian Reviews)", "Upload your own"))

if data_option == "Use default (Indian Reviews)":
    df = pd.read_csv("data/indian_reviews.csv")
    st.success("Loaded default dataset: indian_reviews.csv")
else:
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("Custom dataset uploaded successfully.")
    else:
        st.stop()

st.subheader("Preview of Data")
st.dataframe(df.head())

# dropdowns
st.header("Column Selection", divider="blue")
text_col = st.selectbox("[Required] Which column contains text to be analyzed?", df.columns, index=df.columns.get_loc("text") if "text" in df.columns else 0)
rating_col = st.selectbox("[Required] Which column should be used for sentiment/ratings?", df.columns, index=df.columns.get_loc("stars") if "stars" in df.columns else 0)
# secondary_col = st.selectbox("[Recommended] Which column contains the secondary entity to be analyzed?", df.columns, index=df.columns.get_loc("business") if "business" in df.columns else 0, 
#                              help="For instance, if analyzing different dishes in reviews, a secondary column could be 'business' to analyze performance over different restaurants.")
# meta_cols = st.multiselect("[Optional] Select any additional metadata columns to use for filtering:", df.columns, default=[col for col in ["city", "state"] if col in df.columns],
#                            help="These columns can be used to filter or segment the data during analysis (e.g. city, state).")

# submit
nav_col1, nav_col2, nav_col3 = st.columns([2, 1, 2])
with nav_col3:
    if st.button("Extract and Analyze!", icon="🚀", type="primary"):
        st.session_state["df"] = df
        st.session_state["text_col"] = text_col
        st.session_state["rating_col"] = rating_col
        # st.session_state["secondary_col"] = secondary_col
        # st.session_state["meta_cols"] = meta_cols
        st.switch_page("pages/analysis.py")
