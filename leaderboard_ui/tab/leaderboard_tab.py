import gradio as gr
from gradio_leaderboard import Leaderboard, SelectColumns, ColumnFilter,SearchColumns
import enviroments.config as config
from sheet_manager.sheet_loader.sheet2df import sheet2df

def leaderboard_tab():
    with gr.Tab("🏆Leaderboard"):
                leaderboard = Leaderboard(
                    value=sheet2df(),
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
                    hide_columns=config.HIDE_COLUMNS,
                    filter_columns=[
                        ColumnFilter(
                            column= "TASK",
                        ),
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
                refresh_button = gr.Button("🔄 Refresh Leaderboard")

                def refresh_leaderboard():
                    return sheet2df()

                refresh_button.click(
                    refresh_leaderboard,  
                    inputs=[],            
                    outputs=leaderboard,  
                )

