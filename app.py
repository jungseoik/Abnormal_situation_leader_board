import gradio as gr
from pathlib import Path
from ui.tab.submit_tab import submit_tab
from ui.tab.leaderboard_tab import leaderboard_tab
from ui.tab.dataset_visual_tab import visual_tab
from ui.tab.metric_visaul_tab import metric_visual_tab
abs_path = Path(__file__).parent

with gr.Blocks() as demo:
    gr.Markdown("""
    # 🥇 PIA_leaderboard
    """)
    with gr.Tabs():
        leaderboard_tab()
        submit_tab()
        visual_tab()
        metric_visual_tab()

if __name__ == "__main__":
    demo.launch()
