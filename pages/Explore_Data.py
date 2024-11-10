import streamlit as st
import plotly.express as px
import pandas as pd

from helpers import read_json

st.title("Insights from Polis")

# json_data = read_json(r'data/topic_visualization.json')
# df = pd.DataFrame(json_data['points'])
# df = df[~(df['topic']==-1)]

# fig = px.scatter(df, x='x', y='y', color='topic_label', hover_data=['document'])

# st.plotly_chart(fig)

st.markdown(
    """
    <iframe src="http://127.0.0.1:8050/" width="700" height="500"></iframe>
    """,
    unsafe_allow_html=True
)

