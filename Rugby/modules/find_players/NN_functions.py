from IPython.display import display, HTML, clear_output, Javascript
from ipywidgets import widgets, interact, Layout
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import warnings
warnings.filterwarnings("ignore")

from modules.utilities import (decode_unicode,
                               disable_cell_collapsing,
                               fuzzy_match_names)

DATA_PATH = '~/workspace/.Datasets/find_players/'

# ASI font and colours
FONT = "Proxima Nova"
COLOURS = {"dark": "#505966",
           "grey": "#889CB4",
           "blue": "#00AEF9"}

def setup():
    disable_cell_collapsing()
    total_stats, PCA_forwards, PCA_backs = load_finder_data()
    search_setup(total_stats, PCA_forwards, PCA_backs)
    return
    
    
def load_finder_data():
    '''Load the three datasets required for finder app
    
    Returns
    -------
    total_stats : pandas dataframe
    PCA_forwards : pandas dataframe
    PCA_backs : pandas dataframe
    '''
    DATA_DIR = os.path.expanduser(DATA_PATH)
    
    total_stats = pd.read_pickle(DATA_DIR + 'all_seasons_data_per_80_mins.pkl')
    total_stats = total_stats.set_index("Name")
    total_stats.index = decode_unicode(pd.Series(total_stats.index))
    
    PCA_forwards = pd.read_pickle(DATA_DIR + "PCA_forwards.pkl")
    PCA_forwards.index = decode_unicode(pd.Series(PCA_forwards.index))

    PCA_backs = pd.read_pickle(DATA_DIR + "PCA_backs.pkl")
    PCA_backs.index = decode_unicode(pd.Series(PCA_backs.index))
    
    return total_stats, PCA_forwards, PCA_backs


def search_setup(total_stats, PCA_forwards, PCA_backs):

    def begin_search(sender):
        clear_output()
        
        # Recognise player
        names = search_bar.value.split(",")
        names = [name.strip() for name in names]
        # can only search for one name. Take first name entered.
        name = names[0]
        if name == "":
            return
        # returns list, so take value
        player = fuzzy_match_names(total_stats.index, name)[0]
        
        # Find similar players
        report_df = player_KNN_PCA(player, 0,
                                   PCA_forwards, PCA_backs, total_stats)
        
        # Visualise results
        similarity = report_df['Similarity out of 100']
        similarity_hist(similarity[1:])
        display_report(report_df)
        
    search_bar = widgets.Text(width='50%', margin='2%')

    title = widgets.HTML(
        value='<font face="{font}" size="8" color="{colour}"><br/>'
              '<b>London Irish</b> player finder'
              '&nbsp</font>'.format(font=FONT, colour=COLOURS['dark']))

    description =  widgets.HTML(
        value='<font face="{font}" size="4" color="{colour}"><br />Enter player name and press enter to search.</font>'.format(font=FONT, colour=COLOURS['blue']))

    cb_container = widgets.HBox(layout=Layout(width='100%',
                                              height='100%',
                                              display='flex',
                                              flex_flow='column wrap',
                                              flex_direction='row',
                                              flex='align-self',
                                              align_items='flex-start',
                                              margin='margin: 100px 150px 100px 80px;'))

    all_children = [title] + [description] + [search_bar]

    cb_container.children=[i for i in all_children]

    display(cb_container)

    search_bar.on_submit(begin_search)

    
def player_KNN_PCA(player, k, PCA_forwards, PCA_backs, total_stats):
    '''Carries out a nearest neighbour search from 
    the principal component analysis of player stats.
    Output is a report about matching players.'''
    
    #-----------------------------------------------
    # Retrieve PCA of player stats
    #-----------------------------------------------
    
    # Retrieve PCA of stats for chosen player
    player_df = PCA_forwards[PCA_forwards.index.str.lower() == player.lower()]
    if player_df.empty:
        player_df = PCA_backs[PCA_backs.index.str.lower() == player.lower()]
    
    # Find out role of chosen player
    # and determine if Forward or Back
    player_position = player_df["Position"].iloc[0]
    forward_or_back = player_df["Forward"].iloc[0]
    
    # Retrieve PCA of stats for other players
    if(player_df["Forward"].iloc[0] == 1):
        players_data = PCA_forwards[PCA_forwards["Position"] == player_df["Position"].iloc[0]]
    elif (player_df["Back"].iloc[0] == 1):
        players_data = PCA_backs[PCA_backs["Position"] == player_df["Position"].iloc[0]]
    
    #-----------------------------------------------
    # Nearest neighbour search
    #-----------------------------------------------
        
    # Select numeric features
    categ_features = ['Forward', 'Back',
                      'Position', 'Mins', 'Capped']
    all_features = players_data.columns
    numer_features = [x for x in all_features
                      if x not in categ_features]
        
    # Select numeric data
    data = players_data[numer_features]
        
    # Train NN search
    NN = NearestNeighbors()
    NN.fit(data)
        
    # Apply NN search
    neighbours = NN.kneighbors(data.loc[player].reshape(1, -1),
                         len(data), return_distance=True)
    
    #-----------------------------------------------
    # Prepare report about matching players
    #-----------------------------------------------
    
    # Find player role
    player_df = total_stats[total_stats.index.str.lower() == player.lower()]
    player_position = player_df.iloc[0]["Position"]
    forward_or_back =  player_df.iloc[0]["Forward"]
    
    # Select player role
    report_df = total_stats[total_stats["Position"] == player_position]
        
    # Select display features
    disp_features = get_display_features(player_position,
                                         forward_or_back)
    report_df = report_df[["Position"] + disp_features]
        
    # Select neighbours only
    nn_names = list(data.ix[neighbours[1][0]].index)
    report_df = report_df.ix[nn_names].fillna("-")
        
    # Add new feature: similarity
    nn_distances = list(data.ix[neighbours[0][0]].index)
    maximum_d = np.max(nn_distances)
    normalised_d = np.divide(nn_distances, maximum_d)
    nn_similarity = 100. * (1 - normalised_d)
    report_df.insert(0, "Similarity out of 100",
                     pd.Series(data = nn_similarity, index = nn_names))
        
    # Remove spurious 'Name' row 
    # from displayed tables
    report_df.index.name = None
    
    return report_df

def display_report(report_df, num_shown=50):
    '''Display report about matching players'''
    
    # Rename features for display purposes
    lookup = {'Tackles +': 'Tackles plus',
              'Total metres/carry': 'Total metres per carry',
              '+ve kicks %': '+Ve kicks in %'}
    report_df.rename(columns=lookup, inplace=True)
    
    # Display data...
    with pd.option_context('display.precision', 2):
        
        # ...of selected player
        html('Selected player (values per 80 minutes)')
        selected = report_df[0:1]
        selected.drop('Similarity out of 100', axis=1, inplace=True)
        html(selected)
        
        # ...of other players
        html('Matching players (values per 80 minutes)')
        html(report_df[1:].head(num_shown))

def similarity_hist(similarity, num_bins=20):
    '''Display histogram of player similarity'''
    
    # Init figure
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Remove part of frame 
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    # No ticks left and bottom
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    
    # Major horizontal grid
    ax.xaxis.grid(True, color=COLOURS['grey'], linestyle='dashed')
    ax.set_axisbelow(True) 
    plt.grid()
    
    # Customise labels and bars
    label_style = {'family': FONT,
                   'size': 18}
    bars_style = {'edgecolor': COLOURS['dark'],
                  'color': COLOURS['blue'],
                  'bins': range(0, 105, 5)}# Left-aligned bins
    plt.tick_params(axis='both', which='major', labelsize=14)
    
    # Actual plot
    plt.hist(similarity[1:], **bars_style) # Player itself removed
    plt.xlabel("Similarity out of 100", **label_style)
    plt.ylabel("Number of players", **label_style)
    plt.title("Player-similarity distribution", **label_style)
    plt.xlim(100, 0) # Similar players are leftmost
    ax.tick_params(axis='both', pad=10) # Avoid clash of plot-ticks at origin
    plt.show()       

def html(input, font="Proxima Nova", size=6, colour="#505966"):
    '''Display input as html'''
    if isinstance(input, pd.DataFrame):
        output = input.to_html(index=True) # Display index too!
    else: 
        output = '<font face="{font}" size="{size}" color="{colour}"><br>{text}</font>'.format(
            font=font, size=size, colour=colour, text=input)
    display(HTML(output))    

def check_player_name(player,PCA_forwards,PCA_backs):
    
    player_df = PCA_forwards[PCA_forwards.index.str.lower() == player.lower()]
    players_df = PCA_forwards
    
    if(len(player_df) == 0):
        player_df = PCA_backs[PCA_backs.index.str.lower() == player.lower()]
        players_df = PCA_backs

    if (len(player_df) == 0):
                
        names = list(players_df.index.values)
        
        potential_names = process.extract(player, names, limit=4)
        html('No exact match for: ' + str(player).title(), colour=COLOURS['dark'])

        names, values = zip(*potential_names)
        
        names = list(names)
        values = list(values)
        
        html('Using: ' + str(names[0]), colour=COLOURS['dark'])    
        html('Other close matches were:', size=4, colour=COLOURS['grey'])
        for name in names[1:]:
            html(str(name), size=4, colour=COLOURS['grey'])


        return names[0]
    
    else:
        
        return str(player_df.index.format()[0])
    

def get_display_features(position,forward_or_back):
    
    if(forward_or_back == 1): #forward
        if(position == "Hooker"):
            features = ["Tackles completed",
                    "Tackles +","No. of breaks",
                    "Defenders beaten","Total metres/carry",
                    "Support carries","Completed passes",
                    "Penalties conceded","Lineouts won thrown",'Total carries']
        else:
            features = ["Tackles completed",
        "Tackles +","No. of breaks",
        "Defenders beaten","Total metres/carry",
        "Support carries","Completed passes",
        "Penalties conceded","Lineouts won caught",'Total carries']
            
    else:
        features = ["Tackles completed",
        "Tackles +","No. of breaks",
        "Defenders beaten","Total metres/carry",
        "Support carries","Completed passes",
        "Penalties conceded","+ve kicks %",'Total carries']
        
    return features