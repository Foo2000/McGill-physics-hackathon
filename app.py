import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd

from components import Column, Header, Row

app = dash.Dash(__name__)

server = app.server  # Expose the server variable for deployments
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"
mapbox_layout = dict(
    accesstoken=mapbox_access_token,
    style="light",
    center=dict(lon=-73.58781, lat=45.50884),
)
layout = dict(
    autosize=True,
    hovermode="closest",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=mapbox_layout,
    margin=dict(l=30, r=30, b=20, t=40),
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
)

df = pd.read_csv(
    "world_cities_full_info.csv",
    names=["name", "lattitude", "longitude", "elevation"],
    header=None,
)
df.astype({"elevation": int})
print(df.head())

# Standard Dash app code below
app.layout = html.Div(
    className="container",
    children=[
        Header("Walk On Water", app),
        html.Div(
            className="grid",
            children=[
                html.Div(
                    className="card",
                    children=dcc.Slider(
                        id="sea_level", min=0, max=1000, step=1, value=0
                    ),
                ),
                html.Div(className="card", children=dcc.Graph(id="map")),
            ],
        ),
    ],
)


@app.callback(Output("map", "figure"), [Input("sea_level", "value")])
def update_map(sea_level):
    figure = go.Figure()
    dff = df[df.elevation >= int(sea_level)]
    figure.add_trace(
        go.Scattermapbox(
            name="Above sea level",
            lat=dff.lattitude,
            lon=dff.longitude,
            mode="markers",
            marker=go.scattermapbox.Marker(size=5, color="rgb(160,82,45)", opacity=0.6),
            text=dff.name,
            hoverinfo="text",
        )
    )

    dff = df[df.elevation < int(sea_level)]
    figure.add_trace(
        go.Scattermapbox(
            name="Submerged",
            lat=dff.lattitude,
            lon=dff.longitude,
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=5, color="rgb(123, 199, 255)", opacity=0.6
            ),
            text=dff.name,
            hoverinfo="text",
        )
    )
    # figure = go.Figure(
    #     go.Scattermapbox(
    #         lat=df.lattitude,
    #         lon=df.longitude,
    #         mode="markers",
    #         marker=go.scattermapbox.Marker(size=4),
    #         text=df.name,
    #     )
    # )
    figure.update_layout(layout)
    return figure


if __name__ == "__main__":
    app.run_server(debug=True)
