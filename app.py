import dash
import plotly.express as px
import pandas as pd
from dash import html, dcc, Input, Output
from data_loader import load_preprocess_data
from config import (
    AGGREGATED_DATA_FILE,
    BASE_INDICATOR_OPTIONS_MAP,
    AVAILABLE_LAYERS, DEFAULT_LAYERS,
    DEFAULT_INDICATOR,
    color_SCALE, ROOT_color,
    HIGHLIGHT_COLOR, LINE_color, LINE_WIDTH)

#setup
df_full = load_preprocess_data(AGGREGATED_DATA_FILE)
app    = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server


#overall Rellative Impact
dynamic_indicator_map = BASE_INDICATOR_OPTIONS_MAP.copy()
if "relative_overall" in df_full.columns:
    dynamic_indicator_map["overall"] = "Overall Relative Impact"
indicator_options = [{"label": lbl, "value": val} for val, lbl in dynamic_indicator_map.items()]


#layout
app.layout = html.Div([

    html.H3("Environmental Impact by Diet Group"),
    html.Div([
        html.Label("Values shown are relative to high meat-eaters"),html.Br(),
        html.Label("Box size represents number of participants."),html.Br(), html.Br(),
        html.Span("Light blue sections highlight subgroups whose specific impact is higher than the overall weighted average for its diet type", style={'backgroundColor': HIGHLIGHT_COLOR, 'padding':'2px','borderRadius':'3px'})]),
    html.Div([
        html.Div([
            html.Label("Select Layers"),
            dcc.Checklist(id="layer-selector", options=[{"label":l.replace("_"," ").title(),"value":l} for l in AVAILABLE_LAYERS], value=DEFAULT_LAYERS, labelStyle={'display':'inline-block','marginRight':'10px'})], style={"display":"flex","flexDirection":"column","marginRight":"20px"}),
        html.Div([
            html.Label("Select Environmental Category"),
            dcc.Dropdown(id="indicator-dropdown", options=indicator_options, value=DEFAULT_INDICATOR, clearable=False, style={"width":"220px"})], style={"display":"flex","flexDirection":"column","marginRight":"20px"}),
        html.Div([
            dcc.Checklist(id='highlight-toggle', options=[{'label':'Unique feature','value':'ENABLE_HIGHLIGHT'}], value=['ENABLE_HIGHLIGHT'], labelStyle={'display':'inline-block'})], style={"marginLeft":"auto","alignSelf":"center"})], style={"display":"flex","justifyContent":"space-between", "alignItems":"flex-start","marginTop":"20px","paddingBottom":"10px"}),
    dcc.Graph(id="treemap-graph", style={"width":"100%","height":"75vh"})])


#filter per group
def filter_data(df, layers):
    g_all = df["gender"]    == "All"
    a_all = df["age_group"] == "All"
    if "gender" in layers and "age_group" in layers:
        cond = (~g_all)&(~a_all)
    elif "gender" in layers:
        cond = (~g_all)& a_all
    elif "age_group" in layers:
        cond =  g_all &(~a_all)
    else:
        cond =  g_all & a_all
    return df[cond & (df["participants"] > 0)]


#select details
def get_plot_details(indicator, cols):
    rel = f"relative_{indicator.lower()}"
    med = f"{indicator.lower()}_median"
    if indicator == "overall" and "relative_overall" in cols:
        col, is_rel = "relative_overall", True
    elif rel in cols:
        col, is_rel = rel, True
    elif med in cols:
        col, is_rel = med, False
    else:
        col, is_rel = "participants", False
    lbl = "Participants" if col=="participants" else dynamic_indicator_map[indicator]
    return col, is_rel, lbl


#color range
def calc_color_range(series, is_rel):
    if series.isnull().all():
        return None, None, None
    mi, ma = series.min(), series.max()
    if pd.isna(mi) or pd.isna(ma):
        return None, None, None
    if is_rel:
        lo, hi, mid = 0, max(110, ma)*1.05, 100
    else:
        lo, hi, mid = min(0, mi), max(abs(mi), ma)*1.1 or 1, None
    if lo >= hi:
        d = abs(mi*.1) or .1
        return mi-d, mi+d, mid
    return lo, hi, mid


#unique feature
def calc_diet_avg(df, col):
    base = df[(df["gender"]=="All") & (df["age_group"]=="All")]
    return base.set_index("diet")[col].dropna().to_dict()
def apply_highlight(fig, cond):
    enable, is_rel, detailed, diet_avgs = cond
    if not(enable and is_rel and detailed and diet_avgs and fig.data):
        return
    tr   = fig.data[0]
    orig = list(tr.marker.colors)
    new  = []
    for i, bid in enumerate(tr.ids):
        val, diet = tr.customdata[i][:2]
        above = len(bid.split("/"))>2 and val>diet_avgs.get(diet,0)
        new.append(HIGHLIGHT_COLOR if above else orig[i])
    fig.data[0].marker.colors = new


#update treemap
@app.callback(
    Output("treemap-graph","figure"),
    [
        Input("layer-selector","value"),
        Input("indicator-dropdown","value"),
        Input("highlight-toggle","value")])
def update_treemap(selected_layers, indicator, highlight_toggle):
    layers = selected_layers or []
    data   = filter_data(df_full, layers)
    plot_col, is_rel, lbl = get_plot_details(indicator, data.columns)
    r_min, r_max, mid     = calc_color_range(data[plot_col], is_rel)

    fig = px.treemap(
        data_frame=data,
        path=[px.Constant("All Participants")] + layers,
        values="participants",
        color=plot_col,
        color_continuous_scale=color_SCALE,
        range_color=[r_min, r_max],
        color_continuous_midpoint=mid,
        maxdepth=len(layers)+1,
        custom_data=[plot_col,"diet"])

    enable   = 'ENABLE_HIGHLIGHT' in (highlight_toggle or [])
    detailed = any(l in layers for l in ["gender","age_group"])
    avgs     = calc_diet_avg(df_full,plot_col) if (enable and is_rel and detailed) else {}
    apply_highlight(fig,(enable,is_rel,detailed,avgs))
    unit = "%" if is_rel else ""


#hover details
    hover = (
        "<b>%{label}</b><br><br>"
        "Participants: %{value:,}<br>"
        f"{lbl}: %{{customdata[0]:.1f}}{unit}"
        "<extra></extra>")
    text = f"%{{label}}<br>%{{customdata[0]:.1f}}{unit}"
    fig.update_traces(
        hovertemplate=hover,
        texttemplate=text,
        insidetextfont=dict(size=12,color='black'),
        branchvalues="total",
        marker=dict(depthfade=False,line=dict(color=LINE_color,width=LINE_WIDTH)),
        root_color=ROOT_color,
        pathbar_visible=True,
        textposition='middle center')
    fig.update_layout(
        margin=dict(t=30,l=10,r=10,b=10),
        coloraxis_colorbar=dict(title="Relative impact (%)"),
        font=dict(family="Arial, sans-serif",size=12,color="black"))


#side bar
    if is_rel:
        fig.update_layout(
            coloraxis_colorbar=dict(
                tickmode="array",
                tickvals=[0,100],
                ticktext=["0%","100%"]))
    return fig

if __name__=="__main__":
    app.run(debug=True,dev_tools_ui=False)
