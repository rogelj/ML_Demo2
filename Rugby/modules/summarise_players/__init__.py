import warnings
warnings.filterwarnings("ignore")

from summariser_functions import load_data, set_matplotlib_params
from summariser_widget import setup_summariser
from modules.utilities import ASI_COLOUR, disable_cell_collapsing


def summarise():    
    set_matplotlib_params([
            ('patch.facecolor', ASI_COLOUR['blue']),
            ('patch.edgecolor', ASI_COLOUR['grey']),
            
            # text
            ('font.family', 'Proxima Nova'),
            ('font.size', 14),
            ('legend.fontsize', 12),
            ('ytick.labelsize', 12),
            ('xtick.labelsize', 10),
            ('text.color', ASI_COLOUR['grey']),
            ('axes.labelcolor', ASI_COLOUR['grey']),
            # tick label colour
            ('ytick.color', ASI_COLOUR['dark_grey']), 
            ('xtick.color', ASI_COLOUR['dark_grey']),

            ('axes.edgecolor', ASI_COLOUR['grey']),
            ('axes.grid ', True),
            ('axes.spines.top', False),
            ('axes.spines.right', False),
            ('xtick.major.size', 5),
            ('ytick.major.size', 0),
            
            # line, markers, etc. 
            ('lines.markersize', 10),
            ('axes.color_cycle', [ASI_COLOUR['green'],
                                  ASI_COLOUR['pink'],
                                  ASI_COLOUR['yellow'],
                                  ASI_COLOUR['dark_grey']
                                 ]),
        ])
    disable_cell_collapsing()    
    aggregated, seasons = load_data()
    setup_summariser(aggregated, seasons)
