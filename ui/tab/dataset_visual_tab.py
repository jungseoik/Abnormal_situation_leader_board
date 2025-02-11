import gradio as gr
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.bench_meta import process_videos_in_directory
import enviroments.config as config
## TODO 현재 임시 방편 하드코딩

df = pd.read_csv("sample.csv")
print("DataFrame shape:", df.shape)
print("DataFrame columns:", df.columns)
print("DataFrame head:\n", df.head())
def create_category_pie_chart(df, selected_benchmark, selected_categories=None):
    filtered_df = df[df['benchmark'] == selected_benchmark]
    
    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
    
    category_counts = filtered_df['category'].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title=f'{selected_benchmark} - Video Distribution by Category',
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig
 
###TODO 스트링일경우 어케 처리
def create_bar_chart(df, selected_benchmark, selected_categories, selected_column):
    # Filter by benchmark and categories
    filtered_df = df[df['benchmark'] == selected_benchmark]
    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
    
    # Create bar chart for selected column
    fig = px.bar(
        filtered_df,
        x=selected_column,
        y='video_name',
        color='category',  # Color by category
        title=f'{selected_benchmark} - Video {selected_column}',
        orientation='h',  # Horizontal bar chart
        color_discrete_sequence=px.colors.qualitative.Set3  # Color palette
    )
    
    # Adjust layout
    fig.update_layout(
        height=max(400, len(filtered_df) * 30),  # Adjust height based on data
        yaxis={'categoryorder': 'total ascending'},  # Sort by value
        margin=dict(l=200),  # Margin for long video names
        showlegend=True,  # Show legend
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=1.02,  # Place legend above graph
            xanchor="right",
            x=1
        )
    )
    
    return fig

def visual_tab():
    with gr.Tab("📊 Bench Info"):
        with gr.Row():
            benchmark_dropdown = gr.Dropdown(
                choices=sorted(df['benchmark'].unique().tolist()),
                value=sorted(df['benchmark'].unique().tolist())[0],
                label="Select Benchmark",
                interactive=True
            )
            
            category_multiselect = gr.CheckboxGroup(
                choices=sorted(df['category'].unique().tolist()),
                label="Select Categories (empty for all)",
                interactive=True
            )
        
        pie_plot_output = gr.Plot(label="pie")
        
        column_options = config.DATA_OPTIONS
        column_dropdown = gr.Dropdown(
            choices=column_options,
            value=column_options[0],
            label="Select Data to Compare",
            interactive=True
        )
        
        bar_plot_output = gr.Plot(label="video")
        
        def update_plots(benchmark, categories, selected_column):
            pie_chart = create_category_pie_chart(df, benchmark, categories)
            bar_chart = create_bar_chart(df, benchmark, categories, selected_column)
            return pie_chart, bar_chart
        
        benchmark_dropdown.change(
            fn=update_plots,
            inputs=[benchmark_dropdown, category_multiselect, column_dropdown],
            outputs=[pie_plot_output, bar_plot_output]
        )
        category_multiselect.change(
            fn=update_plots,
            inputs=[benchmark_dropdown, category_multiselect, column_dropdown],
            outputs=[pie_plot_output, bar_plot_output]
        )
        column_dropdown.change(
            fn=update_plots,
            inputs=[benchmark_dropdown, category_multiselect, column_dropdown],
            outputs=[pie_plot_output, bar_plot_output]
        )
    