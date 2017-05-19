from IPython.display import display, HTML, Javascript
from fuzzywuzzy import process
import pandas as pd
from unidecode import unidecode


ASI_COLOUR = {'green': '#3AD4BD',
              'pink': '#E44161',
              'blue': '#00AEF9',
              'yellow': '#EEB856',
              'dark': '#22333E',
              'dark_grey': '#505966',
              'grey': '#889CB4',
              'light_grey': '#C7CDD6'}


def disable_cell_collapsing():
    '''Removes ability to collapse output of notebook cells'''
    display(Javascript(
            """IPython.OutputArea.prototype._should_scroll = function(lines) {
            return false;
            }"""))
    
    
def fuzzy_match_names(true_names, entered_names):
    """Find best matching name in all_names 
    for each name in names_to_find.
    
    Parameters:
    -----------
    all_names : array
        True names to match against.
    names_to_find : array
        Names to find a match for.
    
    Returns:
    --------
    liat
        Best match for each name in names_to_find."""
    found = []
    true_names = decode_unicode(pd.Series(true_names))
    entered_names = decode_unicode(pd.Series(entered_names))
    for name in entered_names.values:
        is_name = true_names.str.lower() == name.lower()
        if not any(is_name):
            potential_names = process.extract(name, true_names.values, limit=4)
            found_names, values = zip(*potential_names)
            name_found = found_names[0]
            
            html("No exact match for: {}".format(name.title()), size=5)
            html("Using: {}".format(name_found), size=5)
            close_matches = ", ".join(found_names[1:])
            html("Other close matches were: {}".format(close_matches),
                 size=3)
        else:
            name_found = true_names[is_name].item()
        found.append(name_found)
    return found

def decode_unicode(series):
    '''Convert series from unicode to string
    
    Parameters
    ----------
    series : pandas series 
    '''
    try:
        series = series.astype(str)
    except:
        series = series.apply(unidecode)
    return series


def html(input, font="Proxima Nova", size=5, colour=ASI_COLOUR['dark'], df_index=False):
    '''Display input as html'''
    if isinstance(input, pd.DataFrame):
        output = input.to_html(index=df_index)
    else: 
        output = ('<font face="{font}" size="{size}" color="{colour}">'
                 '<br>{text}</font>'.format(font=font,
                                            size=size,
                                            colour=colour,
                                            text=input))
    display(HTML(output))
