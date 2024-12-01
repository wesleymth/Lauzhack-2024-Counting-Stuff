import plotly.graph_objects as go
import numpy as np
import pandas as pd


def get_data(file):
    model_results = pd.read_pickle(file)
    for i in range(len(model_results)):
        if 'count' not in model_results[i]:
            model_results[i]['count'] = len(model_results[i]['size'])
        if 'date' not in model_results[i]:
            model_results[i]['date'] = i
        if 'location' not in model_results[i]:
            model_results[i]['location'] = f"Location {i}"
    return model_results


def plot_one_feature_temporal(file: str, selected_feature: str):
    """
    Plots the evolution of a feature over time for a single location.
    
    Args:
        file (str): Path to the file containing the model results.
        selected_feature (str): The feature to plot.
    """
    model_results = get_data(file)
    timestamps = [entry["date"] for entry in model_results]
    values = [entry[selected_feature] for entry in model_results]

    # Line plot for boolean values (e.g., True or False predictions)
    if all(v in [0, 1] for v in values[0]):
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

    # Line plot with a single value per image
    elif all(isinstance(v, (int, float)) for v in values):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timestamps, y=values, mode="lines+markers"))
        fig.update_layout(
            title=f"Evolution of {selected_feature} over time",
            xaxis_title="Time",
            yaxis_title=selected_feature,
            template="plotly_white",
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
    fig.write_html("flask_frontend/plots/plot.html")
    return 'All done! Check the plot below and interact with it.'


def plot_one_feature_distribution(file: str, selected_feature: str):
    """
    Plots the distribution of a feature for a single location at a given time.
    
    Args:
        file (str): Path to the file containing the model results.
        selected_feature (str): The feature to plot.
    """
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
    fig.write_html("flask_frontend/plots/plot.html")
    return 'All done! Check the plot below and interact with it.'


def plot_correlation_two_features(file: str, selected_features: list):
    """
    Plots the correlation between two features for a single location at a given time.
    
    Args:
        file (str): Path to the file containing the model results.
        selected_features (list): The two features to plot.
    """
    model_results = get_data(file)
    feature1 = selected_features[0]
    feature2 = selected_features[1]
    values1 = [entry[feature1] for entry in model_results]
    values2 = [entry[feature2] for entry in model_results]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=values1, y=values2, mode="markers"))
    fig.update_layout(
        title=f"Correlation between {feature1} and {feature2}",
        xaxis_title=feature1,
        yaxis_title=feature2,
        template="plotly_white",
    )

    # Export the plot as an HTML file in 'flask_frontend/plots'
    fig.write_html("flask_frontend/plots/plot.html")
    return 'All done! Check the plot below and interact with it.'


def plot_temporal_comparison_two_locations(file: str, selected_feature: str):
    """
    Plots the comparison of a feature between two locations over time.
    
    Args:
        file (str): Path to the file containing the model results.
        selected_feature (str): The feature to plot.
    """
    model_results = get_data(file)
    timestamps = [entry["date"] for entry in model_results]
    values = [entry[selected_feature] for entry in model_results]

    fig = go.Figure()
    # Line plot with a single value per image
    if all(isinstance(v, (int, float)) for v in values[0]):
        fig.add_trace(go.Scatter(x=timestamps, y=values[0], mode="lines+markers", name=model_results[0]["location"]))
        fig.add_trace(go.Scatter(x=timestamps, y=values[1], mode="lines+markers", name=model_results[1]["location"]))
        fig.update_layout(
            title=f"Comparison of {selected_feature} between two locations over time",
            xaxis_title="Time",
            yaxis_title=selected_feature,
            template="plotly_white",
        )

    # Line plot with multiple values per image -> plot the mean and confidence interval
    elif all(isinstance(v, list) for v in values):
        mean_values1 = [np.mean(v) for v in values[0]]
        mean_values2 = [np.mean(v) for v in values[1]]
        std_values1 = [np.std(v) for v in values[0]]
        std_values2 = [np.std(v) for v in values[1]]
        lower_bound1 = [m - s for m, s in zip(mean_values1, std_values1)]
        upper_bound1 = [m + s for m, s in zip(mean_values1, std_values1)]
        lower_bound2 = [m - s for m, s in zip(mean_values2, std_values2)]
        upper_bound2 = [m + s for m, s in zip(mean_values2, std_values2)]

        fig.add_trace(go.Scatter(x=timestamps, y=mean_values1, mode="lines+markers", name=model_results[0]["location"]), showlegend=True)
        fig.add_trace(go.Scatter(x=timestamps, y=mean_values2, mode="lines+markers", name=model_results[1]["location"]), showlegend=True)
        fig.add_trace(go.Scatter(
            x=timestamps + timestamps[::-1],
            y=upper_bound1 + lower_bound1[::-1],
            fill="toself",
            fillcolor="rgba(0,100,250,0.2)",
            line=dict(color="rgba(255,255,255,0)")
            ))
        fig.add_trace(go.Scatter(
            x=timestamps + timestamps[::-1],
            y=upper_bound2 + lower_bound2[::-1],
            fill="toself",
            fillcolor="rgba(0,100,250,0.2)",
            line=dict(color="rgba(255,255,255,0)")
        ))
        fig.update_layout(
            title=f"Comparison of {selected_feature} between two locations with confidence interval",
            xaxis_title="Time",
            yaxis_title=selected_feature,
            template="plotly_white",
        )

    # Export the plot as an HTML file in 'flask_frontend/plots'
    fig.write_html("flask_frontend/plots/plot.html")
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
        mean_values1 = [np.mean(v) for v in values[0]]
        mean_values2 = [np.mean(v) for v in values[1]]
        std_values1 = [np.std(v) for v in values[0]]
        std_values2 = [np.std(v) for v in values[1]]
        lower_bound1 = [m - s for m, s in zip(mean_values1, std_values1)]
        upper_bound1 = [m + s for m, s in zip(mean_values1, std_values1)]
        lower_bound2 = [m - s for m, s in zip(mean_values2, std_values2)]
        upper_bound2 = [m + s for m, s in zip(mean_values2, std_values2)]

        fig.add_trace(go.Bar(x=["Mean"], y=[mean_values1[0]], name=model_results[0]["location"]))
        fig.add_trace(go.Bar(x=["Mean"], y=[mean_values2[0]], name=model_results[1]["location"]))
        fig.add_trace(go.Bar(x=["Confidence interval"], y=[upper_bound1[0] - lower_bound1[0]], name=model_results[0]["location"]))
        fig.add_trace(go.Bar(x=["Confidence interval"], y=[upper_bound2[0] - lower_bound2[0]], name=model_results[1]["location"]))
        fig.update_layout(
            title=f"Comparison of {selected_feature} between two locations with confidence interval",
            xaxis_title="Location",
            yaxis_title=selected_feature,
            template="plotly_white",
        )

    # Bar plot with a single value per image
    elif all(isinstance(v, (int, float)) for v in values[0]):
        fig.add_trace(go.Bar(x=[model_results[0]["location"], model_results[1]["location"]], y=[values[0][0], values[1][0]]))
        fig.update_layout(
            title=f"Comparison of {selected_feature} between two locations",
            xaxis_title="Location",
            yaxis_title=selected_feature,
            template="plotly_white"
        )

    # Export the plot as an HTML file in 'flask_frontend/plots'
    fig.write_html("flask_frontend/plots/plot.html")
    return 'All done! Check the plot below and interact with it.'


