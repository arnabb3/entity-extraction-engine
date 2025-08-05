import streamlit as st
import pandas as pd
import plotly.express as px
import re
from math import ceil
import time

from utils import optimize_entity_stats

# Set page theme and title
st.set_page_config(
    page_title="E3: Entity Extraction Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "E3 is a Streamlit-based web app that lets users upload text datasets and explore entity-level sentiment or rating trends. Whether you're analyzing food reviews, music comments, or news headlines, E3 helps visualize how entities are mentioned, perceived, and rated.",
    }
)

st.markdown("<h1 style='text-align: center;'>🔍 E3: Entity Extraction Engine</h1>", unsafe_allow_html=True)

if "df" not in st.session_state:
    st.error("No dataset found. Please return to the data input page.")
    if st.button("⬅️ Back to Data Input", type="primary"):
        st.switch_page("input.py")
    st.stop()

df = st.session_state["df"]
text_col = st.session_state["text_col"]
rating_col = st.session_state["rating_col"]
# secondary_col = st.session_state["secondary_col"]
# meta_cols = st.session_state["meta_cols"]

# Entity Input
st.header("Add Entities to Track", divider="blue")
if "entities" not in st.session_state:
    st.session_state.entities = []
if "highlighted_entities" not in st.session_state:
    st.session_state.highlighted_entities = []


# Manual entry
with st.form("entity_form", clear_on_submit=True):
    new_entity = st.text_input("Enter an entity:", help="This could be a product, person, or any term you want to track. Only entities with >5 mentions will be added.",
                               placeholder="e.g., for dish names, chicken tikka masala")
    submitted = st.form_submit_button("➕ Add to List")
    if submitted and new_entity:
        if new_entity.lower() not in [e.lower() for e in st.session_state.entities]:
            # Check count of new entity - if less than 5, do not add.
            if df[text_col].str.contains(re.escape(new_entity), case=False).sum() < 5:
                st.warning("This entity is mentioned less than 5 times in the dataset. Consider adding a more common entity.")
            else:
                st.session_state.entities.append(new_entity.strip().lower())
                st.success(f"✅ Added entity: {new_entity.strip()}")
            
        else:
            st.warning("That entity is already in the list.")

# Batch entry
uploaded_file = st.file_uploader(
    "Upload your .txt file",
    type=["txt"],
    help="Each line should contain one entity (e.g., dish name)."
)

if "batch_entities_uploaded" not in st.session_state:
    st.session_state.batch_entities_uploaded = False

if uploaded_file and not st.session_state.batch_entities_uploaded:
    try:
        content = uploaded_file.read().decode("utf-8")
        entities_list = [e.strip().lower() for e in content.splitlines() if e.strip()]
        total = len(entities_list)
        added = 0

        progress_bar = st.progress(0, text="Parsing uploaded entities...")

        for i, entity in enumerate(entities_list):
            entity = entity.strip().lower()
            time.sleep(0.01)
            progress_bar.progress((i + 1) / total, text=f"Adding: {entity[:30]}...")
            if entity not in st.session_state.entities:
                # Check count of new entity - if less than 5, do not add.
                if df[text_col].str.contains(re.escape(entity), case=False).sum() < 5:
                    continue
                else:
                    st.session_state.entities.append(entity)
                    added += 1

        progress_bar.empty()
        st.session_state.batch_entities_uploaded = True

        if added:
            st.success(f"✅ {added} new entities added from file.")
            st.session_state.uploaded_file = None
        else:
            st.info("No new entities added — all were duplicates.")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")


# Clear button logic
for key in ["clear_entities_confirm", "clear_entities_result"]:
    if key not in st.session_state:
        st.session_state[key] = False

# Show initial "Clear All" button
if not st.session_state.clear_entities_confirm:
    if st.button("🗑️ Clear All Entities (Double-Click)", type="primary"):
        if st.session_state.entities:
            st.session_state.clear_entities_confirm = True
        else:
            st.info("No entities to clear.")
else:
    st.warning("Are you sure you want to clear all entities? This action cannot be undone.")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes, clear all entities", key="yes_clear"):
            st.session_state.entities.clear()
            st.session_state.highlighted_entities = []
            st.session_state.clear_entities_confirm = False
            st.session_state.clear_entities_result = "success"
            st.session_state.batch_entities_uploaded = False
            st.rerun()

    with col2:
        if st.button("❌ Cancel", key="cancel_clear"):
            st.session_state.clear_entities_confirm = False
            st.session_state.clear_entities_result = "cancelled"
            st.rerun()

# Show result message temporarily
if st.session_state.clear_entities_result:
    if st.session_state.clear_entities_result == "success":
        st.success("✅ All entities cleared.")
    elif st.session_state.clear_entities_result == "cancelled":
        st.info("Action cancelled — entities were not cleared.")
    time.sleep(3)
    st.session_state.clear_entities_result = False
    st.rerun()



            

# Frequency and Sentiment Analysis
st.header("Mentions and Ratings", divider="blue")
all_entities = st.session_state.entities
highlighted = st.session_state.get("highlighted_entities", [])

if not all_entities:
    st.info("No entities added yet.")
else:
    entities_to_plot = highlighted if highlighted else all_entities
    stats_df = optimize_entity_stats(df, text_col, rating_col, entities_to_plot)

    if stats_df.empty:
        st.warning("No matching data to plot for the selected entities.")
    else:
        fig = px.bar(
            stats_df.sort_values("Mentions", ascending=False),
            x="Entity",
            y="Mentions",
            color="Average Rating",
            color_continuous_scale="purples",
            hover_data=["Average Rating"],
            title="Entity Mentions and Average Rating",
            text_auto=True
        )

        fig.update_layout(
            xaxis_title="Entity",
            yaxis_title="Mentions",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#F1F5F9",
            title_font_size=20
        )

    with st.expander("🛠️ Manage Tracked Entities", expanded=False):
        entities = sorted(st.session_state.entities, key=str.lower)

        if st.session_state.highlighted_entities:
            if st.button("🔄 Unhighlight All", help="Clear all highlighted entities", type="secondary"):
                st.session_state.highlighted_entities = []
                st.rerun()

        num_cols = 6
        rows = ceil(len(entities) / num_cols)

        if not entities:
            st.info("No entities to manage.")
        else:
            for row in range(rows):
                cols = st.columns(num_cols)
                for i in range(num_cols):
                    idx = row * num_cols + i
                    if idx < len(entities):
                        entity = entities[idx]
                        with cols[i]:
                            highlight = entity in st.session_state.get("highlighted_entities", [])
                            container = st.container()
                            with container:
                                col1, col2, col3 = st.columns([1, 15, 45])
                                with col1:
                                    # Vertical divider between columns
                                    st.markdown("<div style='border-left: 1px solid #444; height: 20px;'></div>", unsafe_allow_html=True)
                                with col2:
                                    icon_col1, icon_col2 = st.columns(2)
                                    with icon_col1:
                                        is_highlighted = entity in st.session_state.get("highlighted_entities", [])
                                        if st.button(
                                            "⭐" if not is_highlighted else "🌟",
                                            key=f"highlight_{entity}",
                                            help="Highlight/Unhighlight",
                                            type="tertiary"
                                        ):
                                            if is_highlighted:
                                                st.session_state["highlighted_entities"].remove(entity)
                                            else:
                                                st.session_state["highlighted_entities"].append(entity)
                                            st.rerun()
                                    with icon_col2:
                                        if st.button("❌", key=f"remove_{entity}", help="Remove", type="tertiary"):
                                            st.session_state["entities"].remove(entity)
                                            if entity in st.session_state.get("highlighted_entities", []):
                                                st.session_state["highlighted_entities"].remove(entity)
                                            st.rerun()
                                with col3:
                                    style = "font-size:1em; font-weight: 400;"
                                    if highlight:
                                        style += " color: #FFD700; background-color: #333333; border-radius: 4px; padding: 2px 6px;"
                                    st.markdown(
                                        f"<span style='{style}'>{entity}</span>",
                                        unsafe_allow_html=True
                                    )
                # Add horizontal line between rows
                if row < rows - 1:
                    st.markdown("<hr style='margin-top: 0.5em; margin-bottom: 0.5em; border-color: #444;'>", unsafe_allow_html=True)






    st.plotly_chart(fig, use_container_width=True)


# Back Button
if st.button("⬅️ Back to Data Input", type="primary"):
    st.switch_page("input.py")
