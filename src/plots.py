import plotly.graph_objects as go
import numpy as np
import pandas as pd
from typing import Literal


def get_data(file):
    model_results = pd.read_pickle(file)
    for i in range(len(model_results)):
        if 'container tanks' not in model_results[i]:
            model_results[i]['container tanks'] = len(model_results[i]['size'])
            model_results[i]['number'] = len(model_results[i]['size'])

        if 'date' not in model_results[i]:
            model_results[i]['date'] = i
        if 'location' not in model_results[i]:
            model_results[i]['location'] = f"Location {i}"
    return model_results


def plot_one_feature_temporal(file: str, selected_feature: Literal["size", 'container tanks', "is_in_construction", "number"]):
    """
    Plots the evolution of a feature over time for a single location.
    
    Args:
        file (str): Path to the file containing the model results.
        selected_feature (str): The feature to plot.
    """
    file = "./flask_frontend/static/processed/time-series-USA-cushing.pkl"
    model_results = get_data(file)
    timestamps = [entry["date"] for entry in model_results]
    values = [entry[selected_feature] for entry in model_results]

    
    # Line plot with a single value per image
    if all(isinstance(v, (int, float)) for v in values):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timestamps, y=values, mode="lines+markers"))
        fig.update_layout(
            title=f"Evolution of {selected_feature} over time",
            xaxis_title="Time",
            yaxis_title=selected_feature,
            template="plotly_white",
        )
    
    # Line plot for boolean values (e.g., True or False predictions)
    elif all(v in [0, 1] for v in values[0]):
        # Plot the proportion of each class
        proportions = [np.mean(v) for v in values]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timestamps, y=proportions, fill="tozeroy", mode="lines+markers", fillcolor="Lavender"))
        fig.update_layout(
            title=f"Proportion of each class over time",
            xaxis_title="Time",
            yaxis_title="Proportion",
            template="plotly_white",
            shapes=[dict(type="rect", xref="paper", x0=0, x1=1, y0=0, y1=1, fillcolor="LightSkyBlue", layer="below", line_width=0)]
        )

    # Line plot with multiple values per image -> plot the mean and confidence interval 
    elif all(isinstance(v, list) for v in values):  
        mean_values = [np.mean(v) for v in values]
        std_values = [np.std(v) for v in values]
        lower_bound = [m - s for m, s in zip(mean_values, std_values)]
        upper_bound = [m + s for m, s in zip(mean_values, std_values)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps, y=mean_values, mode="lines+markers", name="Mean"
        ))
        fig.add_trace(go.Scatter(
            x=timestamps + timestamps[::-1],
            y=upper_bound + lower_bound[::-1],
            fill="toself",
            fillcolor="rgba(0,100,250,0.2)",
            line=dict(color="rgba(255,255,255,0)"),
            name="Confidence interval",
            showlegend=True
        ))
        fig.update_layout(
            title=f"Evolution of {selected_feature} with confidence interval",
            xaxis_title="Time",
            yaxis_title=selected_feature,
            template="plotly_white",
        )

    # Export the plot as an HTML file in 'flask_frontend/plots'
    fig.write_html("flask_frontend/static/plots/plot1.html")
    return 'All done! Check the plot below and interact with it.'


def plot_one_feature_distribution(file: str, selected_feature: Literal["size", "is_in_construction"]):
    """
    Plots the distribution of a feature for a single location at a given time.
    
    Args:
        file (str): Path to the file containing the model results.
        selected_feature (str): The feature to plot.
    """
    file = "./flask_frontend/static/processed/USA-cushing-2024_1.pkl"
    model_results = get_data(file)
    data = model_results[0].get(selected_feature, [])
    if isinstance(data, list):  # Distribution for features containing a list of values
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=data, nbinsx=10))
        fig.update_layout(
            title=f"Distribution of {selected_feature}",
            xaxis_title=selected_feature,
            yaxis_title="Frequency",
            template="plotly_white",
        )

    # Export the plot as an HTML file in 'flask_frontend/plots'
    fig.write_html("flask_frontend/static/plots/plot2.html")
    return 'All done! Check the plot below and interact with it.'


# def plot_correlation_two_features(file: str, selected_features: list[str]):
#     """
#     Plots the correlation between two features for a single location at a given time.
    
#     Args:
#         file (str): Path to the file containing the model results.
#         selected_features (list): The two features to plot.
#     """
#     model_results = get_data(file)
#     selected_features = ["size", "is_in_construction"]
#     feature1 = selected_features[0]
#     feature2 = selected_features[1]
#     values1 = [entry[feature1] for entry in model_results]
#     values2 = [entry[feature2] for entry in model_results]

#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=values1, y=values2, mode="markers"))
#     fig.update_layout(
#         title=f"Correlation between {feature1} and {feature2}",
#         xaxis_title=feature1,
#         yaxis_title=feature2,
#         template="plotly_white",
#     )

#     # Export the plot as an HTML file in 'flask_frontend/plots'
#     fig.write_html("flask_frontend/static/plots/plot.html")
#     return 'All done! Check the plot below and interact with it.'

def plot_temporal_comparison_multiple_locations(file: list, selected_feature: str):
    """
    Plots the comparison of a feature between two locations over time.

    Args:
        file (str): Path to the file containing the model results.
        selected_feature (str): The feature to plot.
    """
    file = ['./flask_frontend/static/processed/time-series-Netherlands-Rotterdam.pkl', 
            './flask_frontend/static/processed/time-series-UAE-Fujairah.pkl', 
            './flask_frontend/static/processed/time-series-USA-cushing.pkl']
    fig = go.Figure()
    model_results = []
    for f in file:
        model_results = get_data(f)
        timestamps = [entry["date"] for entry in model_results]
        values = [entry[selected_feature] for entry in model_results]

        # Line plot with a single value per image
        

        # Line plot with multiple values per image -> plot the mean and confidence interval
        if all(isinstance(v, list) for v in values):
            for i in range(len(values)):
                mean_values = [np.mean(v) for v in values[i]]
                std_values = [np.std(v) for v in values[i]]
                lower_bound = [m - s for m, s in zip(mean_values, std_values)]
                upper_bound = [m + s for m, s in zip(mean_values, std_values)]
                fig.add_trace(go.Scatter(x=timestamps, y=mean_values, mode="lines+markers", name=model_results[i]["location"]))
                fig.add_trace(go.Scatter(
                    x=timestamps + timestamps[::-1],
                    y=upper_bound + lower_bound[::-1],
                    fill="toself",
                    fillcolor="rgba(0,100,250,0.2)",
                    line=dict(color="rgba(255,255,255,0)"),
                    name=model_results[i]["location"]
                ))
            fig.update_layout(
                title=f"Comparison of {selected_feature} between multiple locations with confidence interval",
                xaxis_title="Time",
                yaxis_title=selected_feature,
                template="plotly_white",
            )
        elif all(isinstance(v, (int, float)) for v in values[0]):
            for i in range(len(values)):
                fig.add_trace(go.Scatter(x=timestamps, y=values[i], mode="lines+markers", name=model_results[i]["location"]))
            fig.update_layout(
                title=f"Comparison of {selected_feature} between multiple locations over time",
                xaxis_title="Time",
                yaxis_title=selected_feature,
                template="plotly_white",
            )

    # Export the plot as an HTML file in 'flask_frontend/plots'
    fig.write_html("flask_frontend/plots/plot3.html")
    return 'All done! Check the plot below and interact with it.'

def plot_comparison_two_locations(file: str, selected_feature: str):
    """
    Plots the comparison of a feature between two locations at a given time.

    Args:
        file (str): Path to the file containing the model results.
        selected_feature (str): The feature to plot.
    """
    model_results = get_data(file)
    values = [entry[selected_feature] for entry in model_results]

    fig = go.Figure()
    # Bar plot with multiple values per image -> plot the mean and confidence interval
    if all(isinstance(v, list) for v in values):
        for i in range(len(values)):
            mean_values = [np.mean(v) for v in values[i]]
            std_values = [np.std(v) for v in values[i]]
            lower_bound = [m - s for m, s in zip(mean_values, std_values)]
            upper_bound = [m + s for m, s in zip(mean_values, std_values)]
            fig.add_trace(go.Bar(x=["Mean"], y=[mean_values[0]], name=model_results[i]["location"]))
            fig.add_trace(go.Bar(x=["Confidence interval"], y=[upper_bound[0] - lower_bound[0]], name=model_results[i]["location"]))
        fig.update_layout(
            title=f"Comparison of {selected_feature} between multiple locations with confidence interval",
            xaxis_title="Location",
            yaxis_title=selected_feature,
            template="plotly_white",
        )

    # Bar plot with a single value per image
    elif all(isinstance(v, (int, float)) for v in values[0]):
        fig.add_trace(go.Bar(x=[model_results[i]["location"] for i in range(len(model_results))], y=[v[0] for v in values]))
        fig.update_layout(
            title=f"Comparison of {selected_feature} between multiple locations",
            xaxis_title="Location",
            yaxis_title=selected_feature,
            template="plotly_white"
        )

    # Export the plot as an HTML file in 'flask_frontend/plots'
    fig.write_html("flask_frontend/plots/plot4.html")
    return 'All done! Check the plot below and interact with it.'


