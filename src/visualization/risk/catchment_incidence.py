from matplotlib.axes import Axes 
import matplotlib.dates as mdates
import pandas as pd 
import seaborn as sns

from ..utils import airport_colors

def plot_catchment_incidence(ax : Axes, 
                             incidence : pd.DataFrame):
    
    catchment_incidence = incidence.melt(
        id_vars='airport',
        var_name='timestamp',
        value_name='incidence'
    )
    # Keep only airports with at least one non-zero observation
    catchment_incidence = catchment_incidence[
        catchment_incidence.groupby('airport')['incidence'].transform('max') > 0
    ]    

    sns.lineplot(
        data=catchment_incidence[catchment_incidence['airport'].isin(airport_colors.keys())],
        x='timestamp',
        y='incidence',
        hue='airport',
        marker='o',
        palette = airport_colors,
        ax=ax
    )

    sns.lineplot(
        data=catchment_incidence[~catchment_incidence['airport'].isin(airport_colors.keys())],
        x='timestamp',
        y='incidence',
        marker='o',
        c = 'grey',
        ax=ax
    )
    
    ax.set_xlabel(None)
    ax.set_xticks(list(catchment_incidence['timestamp'].unique()))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=5, fancybox=True, shadow=True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title('Catchment incidence', loc = 'left')