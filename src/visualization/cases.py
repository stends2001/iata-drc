import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import pandas as pd
import seaborn as sns
import matplotlib.dates as mdates

def plot_national_cases(axes : list[Axes], casedata : pd.DataFrame):

    cases_national = casedata.groupby(['date']).agg({'cases_new' : 'sum', 
                                                        'cases_cumulative_corrected' : 'sum'}).reset_index(drop = False)

    sns.lineplot(cases_national, x = 'date', y = 'cases_cumulative_corrected', marker = 'o', ax = axes[0])
    axes[0].set_title('Cumulative cases: Transribed from INSP', loc = 'left')
    axes[0].set_ylabel("Cases")

    sns.lineplot(cases_national, x = 'date', y = 'cases_new', marker = 'o', ax = axes[1])
    axes[1].set_title('New cases: Derived from cumulative cases', loc = 'left')
    axes[1].set_ylabel("Cases")

    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)