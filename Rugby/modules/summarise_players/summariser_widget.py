from IPython.display import display, clear_output
from ipywidgets import widgets, interact, Layout

from summariser_functions import search_controller


FONT = "Proxima Nova"
COLOURS = {"dark": "#505966",
           "grey": "#889CB4",
           "blue": "#00AEF9"}
FEATURE_OPTIONS = ["All seasons",
                   "Carries", 
                   "Breaks", 
                   "Tackles", 
                   "Passing", 
                   "Offloads", 
                   "Kicking", 
                   "Goal kicking", 
                   "Lineouts caught",
                   "Lineouts thrown",
                   "Collection",
                   "Discipline"]

    
def setup_summariser(aggregated_data, season_by_season_data):
    '''Launches summariser widget for querying data'''

    def button_is_on(b):
        '''Returns true if button is clicked'''
        reset_check = False
        for c in checkboxes:
            if (c.value == False):
                reset_check = True
            if reset_check:
                for c in checkboxes:
                    c.value = True
            else:
                for c in checkboxes:
                    c.value = False

    def search(sender):
        clear_output()
        checks = []
        for c in checkboxes:
            checks.append(c.value) 
        search_controller(aggregated_data,
                          season_by_season_data,
                          search_bar.value,
                          checks)

    cb_container = widgets.HBox(layout=Layout(width='100%',
                                              display='flex',
                                              flex_flow='row wrap',
                                              flex_direction='row',
                                              flex='align-self',
                                              align_items='flex-start',
                                              margin='margin: 100px 150px 100px 80px;'))  
    title = widgets.HTML(
        value='<font face="{font}" size="{size}" color="{colour}"><br>'
              '<b>London Irish</b> player summariser</font>'.format(font=FONT,
                                                                size=7,
                                                                colour=COLOURS["dark"]))
    description =  widgets.HTML(
        value='<font face="{font}" size="{size}" color="{colour}"><br>'
              'Enter a player\'s name, or mulitple names seperated by commas, '
              'and press enter to see their match statistics.</font>'.format(font=FONT,
                                                                             size=4,
                                                                             colour=COLOURS["blue"]))
    search_bar = widgets.Text(description="Search:",
                              width='80%', margin='2%')
    checkboxes = [widgets.Checkbox(description=feature_name,
                                   value=True, width='20%', margin='1%')
                  for feature_name in FEATURE_OPTIONS]
    button = widgets.Button(description="Reset check boxes",
                            width='20%',
                            button_style='info',
                            margin='2%')

    all_children = [title] + [description] + [search_bar] + checkboxes + [button]
    cb_container.children = [child for child in all_children]
    display(cb_container)

    search_bar.on_submit(search)
    button.on_click(button_is_on)