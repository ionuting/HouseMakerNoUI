import pandas as pd
import plotly.graph_objects as go
import json
import matplotlib.pyplot as plt
import numpy as np

def read_volumes_from_json(filename):
    """Read volume data from a JSON file."""
    try:
        with open(filename, 'r') as json_file:
            volumes = json.load(json_file)
        return volumes
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file '{filename}'.")
        return {}

def create_plotly_chart(volumes):
    """Create an interactive pie chart using Plotly."""
    volumes_df = pd.DataFrame(list(volumes.items()), columns=['Object', 'Volume'])
    volumes_df['Volume'] = pd.to_numeric(volumes_df['Volume'], errors='coerce')
    volumes_df = volumes_df.dropna()
    
    labels_with_volumes = [
        f"{obj} (Volume: {vol:.2f})" 
        for obj, vol in zip(volumes_df['Object'], volumes_df['Volume'])
    ]

    fig = go.Figure(data=[go.Pie(
        labels=labels_with_volumes,
        values=volumes_df['Volume'],
        hoverinfo='label+percent',
        textinfo='label+value',
        marker=dict(
            colors=['#636EFA', '#EF553B', '#00CC96', '#AB63FA'],
            line=dict(color='#FFFFFF', width=2)
        )
    )])
    
    fig.update_layout(
        title=dict(
            text="Volume Distribution of 3D Objects (Plotly)",
            font=dict(size=24, family="Arial"),
            x=0.5
        ),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
            font=dict(size=12)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=50, b=50, t=50, pad=4)
    )
    
    fig.update_traces(
        pull=[0.05, 0, 0.05, 0],
        rotation=90,
        hole=0.3,
        opacity=0.9
    )
    
    return fig

def create_matplotlib_charts(volumes):
    """Create both pie and bar charts using Matplotlib."""
    # Convert volumes to DataFrame
    volumes_df = pd.DataFrame(list(volumes.items()), columns=['Object', 'Volume'])
    volumes_df['Volume'] = pd.to_numeric(volumes_df['Volume'], errors='coerce')
    volumes_df = volumes_df.dropna()
    
    # Create a figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    # Culori atractive pentru pie chart
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', '#99CCFF', '#FFB366', '#99FF99']
    
    # Explode effect pentru pie chart (toate feliile sunt ușor separate)
    explode = [0.05] * len(volumes_df)
    
    # Create pie chart (subplot 1)
    wedges, texts, autotexts = ax1.pie(volumes_df['Volume'], 
                                      explode=explode,
                                      labels=volumes_df['Object'],
                                      colors=colors,
                                      autopct='%1.1f%%',
                                      pctdistance=0.85,
                                      shadow=True)
    
    # Add a circle at the center to create a donut chart effect
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    ax1.add_artist(centre_circle)
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax1.axis('equal')
    ax1.set_title('Volume Distribution (Pie Chart)', pad=20)
    
    # Customize text properties
    plt.setp(autotexts, size=8, weight="bold")
    plt.setp(texts, size=8)
    
    # Create bar chart (subplot 2)
    bars = ax2.bar(volumes_df['Object'], volumes_df['Volume'], color=colors)
    
    # Customize bar chart
    ax2.set_title('Volume Distribution (Bar Chart)', pad=20)
    ax2.set_xlabel('Object')
    ax2.set_ylabel('Volume')
    
    # Rotate x-axis labels
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom')
    
    # Add legend to pie chart
    ax1.legend(wedges, volumes_df['Object'],
              title="Objects",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Adjust layout
    plt.tight_layout()
    
    return fig, (ax1, ax2)
''''
def main():
    filename = 'volumes.json'
    volumes = read_volumes_from_json(filename)
    
    if volumes:
        # Create and display Plotly chart
        plotly_fig = create_plotly_chart(volumes)
        plotly_fig.show()
        
        # Create and display Matplotlib charts
        fig, axes = create_matplotlib_charts(volumes)
        plt.show()

if __name__ == "__main__":
    main()
'''