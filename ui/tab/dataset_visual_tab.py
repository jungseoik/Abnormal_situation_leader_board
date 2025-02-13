import gradio as gr
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import enviroments.config as config
from ui.visual.data_plot import create_category_pie_chart, create_bar_chart
from utils.bench_meta import process_videos_in_directory
## TODO 현재 임시 방편 하드코딩
DATA_PATH = "/home/piawsa6000/nas192/videos/huggingface_benchmarks_dataset/Leaderboard_bench"

def visual_tab():
    df = process_videos_in_directory(DATA_PATH)
    with gr.Tab("📊 Bench Info"):
        with gr.Row():
        #     benchmark_dropdown = gr.Dropdown(
        #         choices=sorted(df['benchmark'].unique().tolist()),
        #         value=sorted(df['benchmark'].unique().tolist())[0],
        #         label="Select Benchmark",
        #         interactive=True
        #     )
            
        #     category_multiselect = gr.CheckboxGroup(
        #         choices=sorted(df['category'].unique().tolist()),
        #         label="Select Categories (empty for all)",
        #         interactive=True
        #     )
        
        # pie_plot_output = gr.Plot(label="pie")
        
            benchmark_dropdown = gr.Dropdown(
            choices=sorted(df['benchmark'].unique().tolist()),
            value=sorted(df['benchmark'].unique().tolist())[0],
            label="Select Benchmark",
            interactive=True
              )
        
            # 카테고리 체크박스 그룹 (초기값은 첫 번째 벤치마크의 카테고리들)
            initial_benchmark = sorted(df['benchmark'].unique().tolist())[0]
            initial_categories = sorted(df[df['benchmark'] == initial_benchmark]['category'].unique().tolist())
            
            category_multiselect = gr.CheckboxGroup(
                choices=initial_categories,
                label="Select Categories (empty for all)",
                interactive=True
            )

        # 파이 차트 출력
        pie_plot_output = gr.Plot(label="pie")
        def update_categories(benchmark):
            categories = sorted(df[df['benchmark'] == benchmark]['category'].unique().tolist())
            return gr.CheckboxGroup(choices=categories, value=[])
        # 벤치마크 선택 시 카테고리 업데이트 이벤트 연결
        benchmark_dropdown.change(
            fn=update_categories,
            inputs=[benchmark_dropdown],
            outputs=[category_multiselect]
        )
        
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
    