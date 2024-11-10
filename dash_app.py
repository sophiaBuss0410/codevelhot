from dash import Dash, dcc, html, Output, Input
import plotly.express as px
import pandas as pd

from helpers import read_json

json_data = read_json(r'data/topic_visualization.json')
df = pd.DataFrame(json_data['points'])
df = df[~(df['topic']==-1)]
df['id'] = df.index

df_com = pd.read_csv(r'data/global_topic_google_labeled.csv')
df_com['id'] = df_com.index

fig = px.scatter(df, x='x', y='y', color='topic_label', hover_data=['document', 'topic_label'])
#################################
# Accessing the issues
comms = read_json(r'data/comment_issue_map.json')
recoms = read_json(r'data/recommendation_issue_map.json')
issues = read_json(r'data/all_issues.json')

#################################
app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(
        id='scatter-plot',
        figure=fig
    ),
    html.Div(id='click-output')  # クリックしたデータを表示するためのDiv
])

@app.callback(
    Output('click-output', 'children'),
    Input('scatter-plot', 'clickData')
)
def display_click_data(clickData):
    if clickData is None:
        return "Info on the clicked point"

    # クリックしたデータポイントの情報を抽出
    point_info = clickData['points'][0]
    x_value = point_info['x']
    y_value = point_info['y']
    document = point_info['customdata'][0]  # 'document' の情報が含まれている
    topic_label = point_info['customdata'][1]  # 'topic_label' の情報

    id = df_com[df_com['Document'] == document]['id'].values[0]
    
    result = topic_label.split(": ")
    topic = result[1]

    # try:
    issue_id = comms[str(id)]
    issues_list = []
    recoms_list = []
    for i in issue_id:
        issues_list.append(issues[i])
        recoms_list.append(recoms[i])

    return f"Issues identified by AI: {issues_list}. Recommended actions advised by AI: {recoms_list}"
    # except:
    #     return "Not applicable comment."
    # return topic_label
    # return f"Clicked point - x: {x_value}, y: {y_value}, topic-label: {topic_label}, document: {document}"
    # want to return the issues!!

# Dashサーバーの起動
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

# Dash is running on http://127.0.0.1:8050/