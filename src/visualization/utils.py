airport_colors = {
    'FIH' : '#2a78d6',
    'GOM' : '#1b9e77',
    'FKI' : '#d95f02',
    'IRP' : '#4a3aa7',
    'BNC' : '#e7298a',
    'BUX' : '#008300',
    'FBM' : '#a6761d',
    'RUE' : "#4daba3",
    'EBB' : '#1b9e77',
    'JUB' : '#7570b3',
    'KXO' : '#e6ab02',
    'KHX' : '#66a61e'
}

import base64, io
import matplotlib.pyplot as plt
from IPython.display import HTML

def show_inline(fig, dpi=150):
    """Embed a matplotlib figure directly in the HTML (no image files)."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
    plt.close(fig)                                   # prevents a second copy being shown
    b64 = base64.b64encode(buf.getvalue()).decode()
    return HTML(f'<img src="data:image/png;base64,{b64}" style="width:100%">')