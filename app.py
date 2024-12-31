import gradio as gr
from gradio_leaderboard import Leaderboard, SelectColumns, ColumnFilter,SearchColumns
import config
from pathlib import Path
import pandas as pd
import random
from sheet_manager.sheet_loader.sheet2df import sheet2df
abs_path = Path(__file__).parent

main_df = sheet2df()

def on_select(evt: gr.SelectData):
    selected_value = evt.value  # 클릭된 셀의 값
    selected_index = evt.index  # 클릭된 셀의 (row, col)
        # 디버깅 로그 추가
    print(f"Selected value: {selected_value}")
    print(f"Selected index: {selected_index}")
    print(evt.__dict__)

    # 선택된 열 이름 확인
    col_name = main_df.columns[selected_index[1]]
    print(f"Column name: {col_name}")


with gr.Blocks() as demo:
    gr.Markdown("""
    # 🥇 PIA_leaderboard
    """)
    with gr.Tabs():
        with gr.Tab("Demo"):
            leaderboard = Leaderboard(
                value=main_df,
                select_columns=SelectColumns(
                    default_selection=config.ON_LOAD_COLUMNS,
                    cant_deselect=config.OFF_LOAD_COLUMNS,
                    label="Select Columns to Display:",
                    info="Check"
                ),

                search_columns=SearchColumns(
                    primary_column="Model name", 
                    secondary_columns=["TASK"],                 
                    placeholder="Search",
                    label="Search"
                ),
                hide_columns=["PIA_absit_F_V1 * 100"],
                filter_columns=[
                    "TASK",
                    ColumnFilter(
                        column="PIA_absit_F_V1 * 100",
                        type="slider",
                        min=0,  # 77
                        max=100,  # 92
                        # default=[min_val, max_val],
                        default = [77 ,92],
                        label="PIA_absit_F_V1"  # 실제 값의 100배로 표시됨,
                    )
                ],

                datatype=config.TYPES,
                # column_widths=["33%", "10%"],

            )

            # # 세부 정보를 표시할 데이터프레임
            detail_view = gr.Dataframe(label="Prompt Details")
            # # 클릭 이벤트 연결
            leaderboard.select(on_select, outputs=detail_view)
            
        with gr.Tab("Docs"):
            gr.Markdown((Path(__file__).parent / "docs.md").read_text())


if __name__ == "__main__":
    demo.launch()
