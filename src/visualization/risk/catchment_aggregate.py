from matplotlib.axes import Axes 
import matplotlib.dates as mdates
import pandas as pd 
import seaborn as sns

from ..utils import airport_colors

def plot_catchment_aggregate(ax : Axes, 
                             df : pd.DataFrame):
    
    catchment_aggregate = df.melt(
        id_vars='airport',
        var_name='timestamp',
        value_name='metric'
    )
    # Keep only airports with at least one non-zero observation
    catchment_aggregate = catchment_aggregate[
        catchment_aggregate.groupby('airport')['metric'].transform('max') > 0
    ]    

    sns.lineplot(
        data=catchment_aggregate[catchment_aggregate['airport'].isin(airport_colors.keys())],
        x='timestamp',
        y='metric',
        hue='airport',
        marker='o',
        palette = airport_colors,
        ax=ax
    )

    sns.lineplot(
        data=catchment_aggregate[~catchment_aggregate['airport'].isin(airport_colors.keys())],
        x='timestamp',
        y='metric',
        marker='o',
        c = 'grey',
        ax=ax
    )
    
    ax.set_xlabel(None)
    ax.set_xticks(list(catchment_aggregate['timestamp'].unique()))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=5, fancybox=True, shadow=True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
