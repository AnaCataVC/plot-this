import plotly.graph_objects as go

# Curated color palettes for a premium design look
PALETTES = {
    "PlotThis Brand (Claro)": {
        "bg": "#FFFFFF",
        "plot_bg": "#F8F9FC",
        "grid": "rgba(44, 77, 130, 0.06)",
        "text": "#2D3748",
        "colors": ["#8C7AE6", "#5FAEE3", "#E1759F", "#54C08D", "#414142"],
        "line": "#8C7AE6",
        "accent": "#E1759F"
    },
    "PlotThis Brand (Oscuro)": {
        "bg": "#0D1117",
        "plot_bg": "#161B22",
        "grid": "rgba(240, 246, 252, 0.06)",
        "text": "#C9D1D9",
        "colors": ["#A291EE", "#7FC0EC", "#E997B9", "#79D2A7", "#E9E9E9"],
        "line": "#A291EE",
        "accent": "#E997B9"
    },
    "Classic Navy": {
        "bg": "#FFFFFF",
        "plot_bg": "#F8F9FA",
        "grid": "rgba(33, 37, 41, 0.06)",
        "text": "#212529",
        "colors": ["#1A365D", "#2B6CB0", "#4299E1", "#ECC94B", "#ED8936", "#E53E3E"],
        "line": "#1A365D",
        "accent": "#DD6B20"
    },
    "Cyberpunk (Dark)": {
        "bg": "#0D1117",
        "plot_bg": "#161B22",
        "grid": "rgba(240, 246, 252, 0.06)",
        "text": "#C9D1D9",
        "colors": ["#FF007F", "#00F0FF", "#BD00FF", "#39FF14", "#FFEF00", "#FF5E00"],
        "line": "#FF007F",
        "accent": "#00F0FF"
    },
    "Warm Earth": {
        "bg": "#FCFBF7",
        "plot_bg": "#F5F2EB",
        "grid": "rgba(60, 50, 40, 0.05)",
        "text": "#2C2520",
        "colors": ["#8C6239", "#C69C6D", "#7E8C78", "#D99B82", "#A64D3F", "#593E30"],
        "line": "#8C6239",
        "accent": "#A64D3F"
    }
}

def apply_premium_style(fig, title: str, palette_name: str = "PlotThis Brand (Claro)"):
    """
    Modifies a Plotly figure to apply premium and clean visual styles:
    elegant typography, coordinated colors, subtle gridlines, and formatted tooltips.
    """
    # Load color palette
    palette = PALETTES.get(palette_name, PALETTES["PlotThis Brand (Claro)"])
    
    # Assign color sequences for traces depending on chart type
    if hasattr(fig, "update_traces"):
        # Update colors on all traces
        for idx, trace in enumerate(fig.data):
            color = palette["colors"][idx % len(palette["colors"])]
            
            # Custom scatter / line styling
            if isinstance(trace, go.Scatter):
                if trace.mode == "lines" or trace.mode == "lines+markers":
                    trace.line.update(color=color, width=2.5)
                elif trace.mode == "markers":
                    trace.marker.update(color=color, size=8, line=dict(width=1, color=palette["bg"]))
            # Custom bar styling
            elif isinstance(trace, go.Bar):
                trace.update(marker_color=color, marker_line=dict(width=0))
            # Custom histogram styling
            elif isinstance(trace, go.Histogram):
                trace.update(marker_color=color, marker_line=dict(width=0.5, color=palette["bg"]))
            # Custom boxplot styling
            elif isinstance(trace, go.Box):
                trace.update(marker_color=color, line=dict(width=1.5))
            # Custom pie chart styling
            elif isinstance(trace, go.Pie):
                trace.update(marker=dict(colors=palette["colors"], line=dict(width=1.5, color=palette["bg"])))
                
    # Update global layout parameters
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "y": 0.95,
            "x": 0.05,
            "xanchor": "left",
            "yanchor": "top",
            "font": {
                "family": "Outfit, Inter, sans-serif",
                "size": 18,
                "color": palette["text"]
            }
        },
        font={
            "family": "Inter, sans-serif",
            "size": 12,
            "color": palette["text"]
        },
        paper_bgcolor=palette["bg"],
        plot_bgcolor=palette["plot_bg"],
        margin=dict(l=60, r=40, t=80, b=60),
        legend={
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(0,0,0,0)",
            "font": {"size": 11, "color": palette["text"]},
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.2,
            "xanchor": "left",
            "x": 0.0
        },
        hoverlabel={
            "bgcolor": palette["plot_bg"],
            "bordercolor": palette["grid"],
            "font": {
                "family": "Inter, sans-serif",
                "size": 12,
                "color": palette["text"]
            }
        },
        # Enable responsive hover modes
        hovermode="closest",
        dragmode="zoom"
    )
    
    # Configure axes layout parameters
    fig.update_xaxes(
        automargin=True,
        showgrid=True,
        gridcolor=palette["grid"],
        gridwidth=0.5,
        linecolor=palette["grid"],
        linewidth=1,
        ticks="outside",
        tickcolor=palette["grid"],
        title_font={"family": "Inter, sans-serif", "size": 12, "color": palette["text"]},
        tickfont={"size": 10, "color": palette["text"]}
    )
    
    fig.update_yaxes(
        automargin=True,
        showgrid=True,
        gridcolor=palette["grid"],
        gridwidth=0.5,
        linecolor=palette["grid"],
        linewidth=1,
        ticks="outside",
        tickcolor=palette["grid"],
        title_font={"family": "Inter, sans-serif", "size": 12, "color": palette["text"]},
        tickfont={"size": 10, "color": palette["text"]}
    )
    
    return fig
