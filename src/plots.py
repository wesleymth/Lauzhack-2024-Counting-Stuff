import plotly.graph_objects as go
import numpy as np
import pandas as pd


def get_data(file):
    model_results = pd.read_pickle(file)
    for i in range(len(model_results)):
        if 'count' not in model_results[i]:
            model_results[i]['count'] = len(model_results[i]['size'])
    return model_results


def plot(file, selected_feature):
    """Crée un graphique interactif à partir des résultats du modèle et des paramètres de l'utilisateur.

    Args:
        model_results (list): Liste de dictionnaires contenant les résultats du modèle pour chaque image.
        selected_feature (str): Feature sélectionné par l'utilisateur.
    """
    model_results = get_data(file)

    if len(model_results) == 1:  # Une seule image analysée
        data = model_results[0].get(selected_feature, [])
        if isinstance(data, list):  # Distribution pour les features contenant une liste de valeurs
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=data, nbinsx=10))
            fig.update_layout(
                title=f"Distribution de {selected_feature}",
                xaxis_title=selected_feature,
                yaxis_title="Fréquence",
                template="plotly_white",
            )
        else:
            return ValueError("Type de plot non supporté pour ce feature."), 400 

    else:  # Plusieurs images analysées
        timestamps = [entry["date"] for entry in model_results]
        values = [entry[selected_feature] for entry in model_results]
        if all(isinstance(v, (int, float)) for v in values):  # Line plot pour une valeur par image
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=timestamps, y=values, mode="lines+markers"))
            fig.update_layout(
                title=f"Évolution de {selected_feature} dans le temps",
                xaxis_title="Temps",
                yaxis_title=selected_feature,
                template="plotly_white",
            )
        elif all(isinstance(v, list) for v in values):  # Line plot avec intervalle de confiance
            if all(v in [0, 1] for v in values[0]):
                # Plot la proportion de chaque classe
                proportions = [np.mean(v) for v in values]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=timestamps, y=proportions, fill="tozeroy", mode="lines+markers", fillcolor="Lavender"))
                fig.update_layout(
                    title=f"Proportion de chaque classe dans le temps",
                    xaxis_title="Temps",
                    yaxis_title="Proportion",
                    template="plotly_white",
                    shapes=[dict(type="rect", xref="paper", x0=0, x1=1, y0=0, y1=1, fillcolor="LightSkyBlue", layer="below", line_width=0)]
                )
            else:
                mean_values = [np.mean(v) for v in values]
                std_values = [np.std(v) for v in values]
                lower_bound = [m - s for m, s in zip(mean_values, std_values)]
                upper_bound = [m + s for m, s in zip(mean_values, std_values)]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=timestamps, y=mean_values, mode="lines+markers", name="Moyenne"
                ))
                fig.add_trace(go.Scatter(
                    x=timestamps + timestamps[::-1],
                    y=upper_bound + lower_bound[::-1],
                    fill="toself",
                    fillcolor="rgba(0,100,250,0.2)",
                    line=dict(color="rgba(255,255,255,0)"),
                    name="Intervalle de confiance",
                    showlegend=True
                ))
                fig.update_layout(
                    title=f"Évolution de {selected_feature} avec intervalle de confiance",
                    xaxis_title="Temps",
                    yaxis_title=selected_feature,
                    template="plotly_white",
                )
        else:
            return ValueError("Type de plot non supporté pour ce feature."), 400 

    # Exporte le graphique en HTML dans 'flask_frontend/plots'
    fig.write_html("flask_frontend/plots/plot.html")