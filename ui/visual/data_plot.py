import plotly.express as px
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