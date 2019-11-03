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
    margin=dict(l=30, r=30, b=0, t=40),
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
)

df = pd.read_csv(
    "world_cities_full_info.csv",
    names=["name", "lattitude", "longitude", "elevation"],
    header=None,
)

df2 = pd.read_csv("worldcities too full version without altitude.csv")
df3 = df.merge(df2, left_on="name", right_on="city_ascii", how="left").dropna(
    subset=["name"]
)
print(df3.head(10))
df = df3
df.population = df.population.fillna(1)

df.astype({"elevation": int})


app.layout = html.Div(
    className="container",
    children=[
        Header("Noah's Ark", app),
        html.Div(
            id="main_row",
            children=[
                html.Div(
                    id="controls",
                    className="card",
                    children=[
                        html.P(
                            id="rate_text",
                            className="control_label",
                            children="Rate of sea level rise",
                        ),
                        dcc.Slider(
                            id="rate_slider",
                            min=0.001,
                            max=5,
                            step=0.001,
                            marks={i: str(i) for i in range(1, 6)},
                            value=0.063,
                        ),
                        dcc.Markdown(id="city_info", children="City:"),
                        dcc.Markdown(
                            id="affected_text", children="**Population affected**"
                        ),
                    ],
                ),
                html.Div(
                    id="main_card",
                    className="card",
                    children=[
                        dcc.Slider(
                            id="sea_level",
                            min=2019,
                            max=3019,
                            step=1,
                            value=2019,
                            marks={
                                2019: "2019",
                                2250: "2250",
                                2500: "2500",
                                2750: "2750",
                                3019: "3019",
                            },
                        ),
                        dcc.Graph(id="map"),
                    ],
                ),
            ],
        ),
        html.Div(
            className="card",
            children=[
                dcc.Markdown("**Topographic map of rising sea levels**"),
                html.Video(id="video", src="/static/Earth_Flooding.mp4", controls=True),
            ],
        ),
    ],
)


@app.callback(
    Output("map", "figure"),
    [Input("sea_level", "value"), Input("rate_slider", "value")],
)
def update_map(year, rate):

    figure = go.Figure()
    sea_level = (int(year) - 2019) * float(rate)
    dff = df[df.elevation >= sea_level]
    figure.add_trace(
        go.Scattermapbox(
            name="Above sea level",
            lat=dff.lattitude,
            lon=dff.longitude,
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=dff.population // 200000, color="rgb(160,82,45)", opacity=0.6
            ),
            text=dff.name,
            hoverinfo="text",
            customdata=dff.elevation,
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
                size=dff.population // 200000, color="rgb(123, 199, 255)", opacity=0.6
            ),
            text=dff.name,
            hoverinfo="text",
            customdata=dff.elevation,
        )
    )
    layout["title"] = "Satellite Overview : Year {} (sea level: {:.2f}m)".format(
        year, sea_level
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


@app.callback(
    Output("city_info", "children"),
    [
        Input("sea_level", "value"),
        Input("map", "clickData"),
        Input("rate_slider", "value"),
    ],
)
def update_city_info(year, clickData, rate):
    data = clickData["points"][0]
    sea_level = (int(year) - 2019) * int(rate)
    text = """**City: {}** \n
    Longitude: {:4f} \n
    Latitude: {:4f} \n
    Status in {}: {}
    """.format(
        data["text"],
        data["lat"],
        data["lon"],
        year,
        "Submerged" if data["customdata"] < sea_level else "Safe",
    )
    return text


@app.callback(Output("rate_text", "children"), [Input("rate_slider", "value")])
def update_rate_text(rate):
    return "Rate of sea level rise: {} m/y".format(rate)


# @app.callback(Output("rate_text", "children"), [Input("rate_slider", "value")])
# def update_rate_text(rate):
#     return "Rate of sea level rise: {} m/y".format(rate)


@server.route("/static/<path:path>")
def serve_static(path):
    root_dir = os.getcwd()
    return flask.send_from_directory(os.path.join(root_dir, "static"), path)


if __name__ == "__main__":
    app.run_server(debug=True)
