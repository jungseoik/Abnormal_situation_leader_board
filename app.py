import gradio as gr
from pathlib import Path
from leaderboard_ui.tab.submit_tab import submit_tab
from leaderboard_ui.tab.leaderboard_tab import leaderboard_tab
abs_path = Path(__file__).parent

with gr.Blocks() as demo:
    gr.Markdown("""
    # 🥇 PIA_leaderboard
    """)
    with gr.Tabs():
        leaderboard_tab()
        submit_tab()

if __name__ == "__main__":
    demo.launch()
