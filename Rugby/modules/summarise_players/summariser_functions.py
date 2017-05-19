from fuzzywuzzy import process
from IPython.display import display
import matplotlib.pyplot as plt
import os
import pandas as pd

from modules.utilities import (ASI_COLOUR,
                               decode_unicode,
                               fuzzy_match_names,
                               html)

DATA_PATH = '~/workspace/.Datasets/summarise_players'

FEATURES = {'basic': ["Apps",
                      "Mins"],
            'carries': ["Total carries",
                        "Total metres",
                        "Total metres/carry",
                        "Support carries"],
            'breaks': ["No. of breaks",
                       "Defenders beaten"],
            'tackles': ["Tackles attempted",
                        "Tackles completed %",
                        "Tackles missed"],
            'passing': ["Attempted passes",
                        "Completed passes",
                        "Pass completion %"],
            'off_loads': ["Off loads"],
            'kicking': ["Total kicks in play",
                        "Penalty kicks",
                        "Total kicks",
                        "Successful kicks in to touch",
                        "+ve kicks %",
                        "-ve kicks %"],
            'goal_kicking': ["Penalty goals attempted",
                             "Penalty goals scored %",
                             "Conversions attempted",
                             "Conversions scored %",
                             "Drop goals attempted",
                             "Drop goals scored %"],
            'lineouts_caught': ["Lineouts won caught",
                                "Lineout steals"],
            'lineouts_thrown': ["Lineouts won thrown",
                                "Lineouts lost thrown",
                                "Lineouts won thrown %"],
            'collections': ["Attempted collections",
                            "Collection completion %"],
            'discipline': ["Penalties conceded",
                           "Yellow cards",
                           "Red cards"]
           }


def search_controller(aggregate_data, seasons_data, names_string, checkboxes):
    """Display player statistics based on string input
    specifying one or more players by name."""
    names = names_string.split(",")
    names = [name.strip() for name in names]
    if names[0] == "":
        return
    
    players = fuzzy_match_names(aggregate_data["Name"], names)
    show_all_seasons = checkboxes[0]
    if len(players) == 1 and not show_all_seasons: 
        display_career_stats(aggregate_data, players[0], checkboxes)
        return
    else:
        display_season_by_season_stats(aggregate_data,
                                       seasons_data,
                                       players,
                                       checkboxes) 
        return
    

def load_data():
    '''Returns aggregated data in a pandas DataFrame
    and a dictionary of season-by-season data.'''
    DATA_DIR = os.path.expanduser(DATA_PATH)
    aggregated = pd.read_pickle(os.path.join(
            DATA_DIR, "all_seasons_data.pkl"))
    aggregated["Name"] = decode_unicode(aggregated["Name"])
    seasons = {}
    for i in xrange(7):
        seasons[i] = pd.read_pickle(os.path.join(
                DATA_DIR, "club_season_{}_data.pkl".format(i)))
        seasons[i]["Name"] = decode_unicode(seasons[i]["Name"])
    for i in xrange(7, 11):
        seasons[i] = pd.read_pickle(os.path.join(
                DATA_DIR, "U20_6N_{}_data.pkl".format(i-7)))
        seasons[i]["Name"] = decode_unicode(seasons[i]["Name"])
    return aggregated, seasons


def set_matplotlib_params(parameters):
    """Sets matplotlib.pyplot parameters.

    Parameters
    ----------
    parameters : list of pairs
        List of tuples, each of which is a key-value pair for
        matplotlib.pyplot.rcParams

    Raises
    ------
    KeyError : if invalid parameter.
    """
    for parameter in parameters:
        try:
            plt.rcParams[parameter[0]] = parameter[1]
        except KeyError:
            pass


def tidy(df, unstack='Season', fillna='-'):
    '''Tidy df for display.
    
    Parameters
    ---------- 
    df : pandas dataframe
    unstack : str
        index level to unstack.
    fillna : str
    '''
    df = df.unstack(unstack)
    df.index.name = None
    return df.fillna('-')


def insert_additional_features(player_stats):
        '''Insert pre-determined additional features
        
        Parameters
        ----------
        player_stats : pandas dataframe
            statistics of player(s)
            
        Returns
        -------
        player_stats : pandas dataframe
            input with additional columns
        '''
        player_stats["Tackled dominant %"] = 100 * (player_stats["Tackled dominant"] / 
                                                    player_stats["Total carries"])
        player_stats["Tackled neutral %"] = 100 * (player_stats["Tackled neutral"] / 
                                                   player_stats["Total carries"])
        player_stats["Tackled ineffective %"] = 100 * (player_stats["Tackled ineffective"] / 
                                                       player_stats["Total carries"])
        player_stats["Tackles completed %"] = 100 * (player_stats["Tackles completed"] / 
                                                     player_stats["Tackles attempted"])
        player_stats["Tackles + %"] = 100 * (player_stats["Tackles +"] / 
                                             player_stats["Tackles completed"])
        player_stats["Tackles ineffective %"] = 100 * (player_stats["Tackles ineffective"] / 
                                                       player_stats["Tackles completed"])
        player_stats["Pass completion %"] = 100 * (player_stats["Completed passes"] / 
                                                   player_stats["Attempted passes"])
        player_stats["Collection completion %"] = 100 * (player_stats["Successful collections"] / 
                                                         player_stats["Attempted collections"])
        player_stats["Lineouts won thrown %"] = 100 * (player_stats["Lineouts won thrown"] / 
                                                       (player_stats["Lineouts won thrown"]
                                                        + player_stats["Lineouts lost thrown"]))
        player_stats["Penalty goals scored %"] = 100 * (player_stats["Penalty goal scored"] / 
                                                        player_stats["Penalty goals attempted"])
        player_stats["Conversions scored %"] = 100 * (player_stats["Conversion scored"] / 
                                                      player_stats["Conversions attempted"])
        player_stats["Drop goals scored %"] = 100 * (player_stats["Drop goal scored"] / 
                                                     player_stats["Drop goals attempted"])
        return player_stats


def display_career_stats(aggregate_data, name, checkboxes):
    
    # Select player's data
    player_stats = aggregate_data[aggregate_data["Name"].str.lower() == name.lower()] 
    
    if player_stats.empty:
        html("Player not found: " + str(name))
        return
    
    player_stats = insert_additional_features(player_stats)
    player_stats = player_stats.fillna('-')
    
    # Determine which features to display
    carries = checkboxes[1]
    breaks = checkboxes[2]
    tackles = checkboxes[3]
    passing = checkboxes[4]
    off_loads = checkboxes[5]
    kicking = checkboxes[6]
    goal_kicking = checkboxes[7]
    lineouts_caught = checkboxes[8]
    lineouts_thrown = checkboxes[9]
    collections = checkboxes[10]
    discipline = checkboxes[11]
    
    # display stats
    with pd.option_context('display.precision', 2):
        
        html("<b>Basic information</b>")
        html(player_stats[["Name", "Position", "Apps", "Mins"]])
        
        if carries:
            html("<b>Carries</b> per 80 minutes")
            html(player_stats[["Total carries","Total metres",
                               "Total metres/carry",
                               "Support carries"]])
        
        if breaks:
            html("<b>Breaks</b> per 80 minutes")
            html(player_stats[["No. of breaks",
                               "Defenders beaten"]])
            
        if tackles:
            html("<b>Tackles</b> per 80 minutes")
            html(player_stats[["Tackles attempted",
                               "Tackles completed %", 
                               "Tackles missed"]])
            html(player_stats[["Tackles + %",
                               "Tackled dominant %",
                               "Tackled neutral %",
                               "Tackled ineffective %"]])
        
        if passing:
            html("<b>Passes</b> per 80 minutes")
            html(player_stats[["Attempted passes",
                               "Completed passes", 
                               "Pass completion %"]])
            
        if off_loads:
            html("<b>Offloads</b> per 80 minutes")
            html(player_stats[["Off loads"]])
        
        if kicking:
            html("<b>Kicks</b> per 80 minutes")
            html(player_stats[["Total kicks in play",
                               "Penalty kicks", 
                               "Total kicks"]])
            html(player_stats[["Successful kicks in to touch", 
                               "+ve kicks %", 
                               "-ve kicks %"]])
    
        if goal_kicking:
            html("<b>Goal kicks</b> per 80 minutes")
            html(player_stats[["Penalty goals attempted",
                               "Penalty goals scored %"]])
            html(player_stats[["Conversions attempted", 
                               "Conversions scored %"]])
            html(player_stats[["Drop goals attempted", 
                               "Drop goals scored %"]])
            
        if lineouts_caught:
            html("<b>Line-outs caught</b> per 80 minutes")
            html(player_stats[["Lineouts won caught",
                               "Lineout steals"]])
    
        if lineouts_thrown:
            html("<b>Line-outs thrown</b> per 80 minutes")
            html(player_stats[["Lineouts won thrown", 
                               "Lineouts lost thrown", 
                               "Lineouts won thrown %"]])
        
        if collections:
            html("<b>Collections</b> per 80 minutes")
            html(player_stats[["Attempted collections",
                               "Collection completion %"]])
            
        if discipline:
            html("<b>Discipline</b> per 80 minutes")
            html(player_stats[["Penalties conceded",
                               "Red cards",
                               "Yellow cards"]])
        return


def display_season_by_season_stats(aggregate_data, seasons_data, names, checks):

    for name in names:
        if name.lower() not in aggregate_data["Name"].str.lower().values:
            html("Player not found: " + str(name))
            return

    season = checks[0]
    carries = checks[1]
    breaks = checks[2]
    tackles = checks[3]
    passing = checks[4]
    off_loads = checks[5]
    kicking = checks[6]
    goal_kicking = checks[7]
    lineouts_caught = checks[8]
    lineouts_thrown = checks[9]
    collections = checks[10]
    discipline = checks[11]
    
    basic_stats = pd.DataFrame()
    for name in names:
        basic_stats = basic_stats.append(aggregate_data[aggregate_data["Name"].str.lower() == name.lower()])
    
    player_stats = {}
    for i, season_data in seasons_data.items():
        player_stats[i] = pd.DataFrame()
        for name in names:
            stats_of_player = season_data[season_data["Name"].str.lower() == name.lower()]
            player_stats[i] = player_stats[i].append(stats_of_player)            
    all_stats = pd.concat(player_stats.values())
    all_stats = insert_additional_features(all_stats)
   
    stats_by_player_season = all_stats.groupby(['Name','Season']).sum()

    def plot(features):
        '''Plot features by season.
        
        Parameters
        ----------
        features : array_like
            names of columns to plot
        '''
        n = float(len(features))
        if n == 1.:
            for player, stats in stats_by_player_season.groupby(level=0):
                season_names = stats.index.get_level_values('Season')
                years = season_names.str[:4].astype(int)
                fig, axes = plt.subplots(figsize=(5, 3))
                axes.plot(years, stats[[features[0]]], '-o', label=player)
                axes.set_title(features[0] + " per 80 minutes")
                axes = [axes]
        else:    
            ncols = min(2, n)
            nrows = int(round(n/2))
            fig, axes = plt.subplots(ncols=ncols,
                                     nrows=nrows,
                                     figsize=(8*ncols,
                                              5*nrows),
                                     gridspec_kw={'wspace': 0.2,
                                                  'hspace': 0.4})
            axes = axes.flatten()
            for i, feature in enumerate(features):
                for player, stats in stats_by_player_season.groupby(level=0):
                    season_names = stats.index.get_level_values('Season')
                    years = season_names.str[:4].astype(int)

                    axes[i].plot(years, stats[[feature]], '-o', label=player)
                    axes[i].set_title(feature + " per 80 minutes")

            if int(n) < len(axes):
                axes[-1].axis('off')

        style_subplots(axes)
        plt.show()
        
    def style_subplots(axes):
        '''Style axes for display.
        
        Parameters
        ----------
        axes : matplotlib axes object
        '''
        uniq_season_names = sorted(all_stats['Season'].unique().astype(str))
        uniq_season_years = pd.Series(uniq_season_names).str[:4].astype(int).unique()

        for ax in axes:
            ax.yaxis.grid(True, which='major',
                          color=ASI_COLOUR['light_grey'], linestyle='-', linewidth=1)
            ax.set_ylim(bottom=0)
            ax.set_xticks(sorted(uniq_season_years))
            ax.set_xticklabels(uniq_season_names, rotation=20)
            ax.set_xlim(min(uniq_season_years)-1, max(uniq_season_years)+1)
            ax.legend(loc='best')    
        return
    
    with pd.option_context('display.precision', 3):
        html("<b>Basic information</b>")
        if season:
            html(basic_stats[["Name", "Position"]])
            # as string to avoid scientific notation of mins
            display(tidy(stats_by_player_season[["Apps","Mins"]].astype(str)))
        else:
            html(basic_stats[["Name", "Position", "Apps", "Mins"]].astype(str))
        plot(FEATURES['basic'])
        
                               
        if carries:
            html("<b>Carries</b> per 80 minutes")
            display(tidy(stats_by_player_season[FEATURES['carries'][:2]]))
            display(tidy(stats_by_player_season[FEATURES['carries'][2:]]))
            plot(FEATURES['carries'])
            
        if breaks: 
            html("<b>Breaks</b> per 80 minutes")
            display(tidy(stats_by_player_season[FEATURES['breaks']]))
            plot(FEATURES['breaks'])
            
        if tackles: 
            html("<b>Tackles</b> per 80 minutes")
            display(tidy(stats_by_player_season[FEATURES['tackles'][:2]]))
            display(tidy(stats_by_player_season[FEATURES['tackles'][2:4]]))
            plot(FEATURES['tackles'])
            
        if passing: 
            html("<b>Passing</b> per 80 minutes")
            display(tidy(stats_by_player_season[FEATURES['passing'][:2]]))
            display(tidy(stats_by_player_season[FEATURES['passing'][2:]]))
            plot(FEATURES['passing'])
            
        if off_loads: 
            html("<b>Offloads</b> per 80 minutes")
            display(tidy(stats_by_player_season[FEATURES['off_loads']]))
            plot(FEATURES['off_loads'])
            
        if kicking: 
            html("<b>Kicks</b> per 80 minutes")
            display(tidy(stats_by_player_season[FEATURES['kicking'][:2]]))
            display(tidy(stats_by_player_season[FEATURES['kicking'][2:4]]))
            display(tidy(stats_by_player_season[FEATURES['kicking'][4:]]))
            plot(FEATURES['kicking'])
            
        if goal_kicking: 
            html("<b>Kicks at goal</b> per 80 minutes")
            display(tidy(stats_by_player_season[FEATURES['goal_kicking'][:2]]))
            display(tidy(stats_by_player_season[FEATURES['goal_kicking'][2:4]]))
            display(tidy(stats_by_player_season[FEATURES['goal_kicking'][4:]]))
            plot(FEATURES['goal_kicking'])
            
        if lineouts_caught: 
            html("<b>Lineouts caught</b> per 80 minutes")
            display(tidy(stats_by_player_season[FEATURES['lineouts_caught']]))
            plot(FEATURES['lineouts_caught'])
            
        if lineouts_thrown: 
            html("<b>Lineouts thrown</b> per 80 minutes")
            display(tidy(stats_by_player_season[FEATURES['lineouts_thrown']][:2]))
            display(tidy(stats_by_player_season[FEATURES['lineouts_thrown']][2:]))
            plot(FEATURES['lineouts_thrown'])
            
        if collections: 
            html("<b>Collections</b> per 80 minutes")
            display(tidy(stats_by_player_season[FEATURES['collections']]))
            plot(FEATURES['collections'])
            
        if discipline:
            html("<b>Discipline</b> per 80 minutes")
            display(tidy(stats_by_player_season[FEATURES['discipline'][:2]]))
            display(tidy(stats_by_player_season[FEATURES['discipline'][2:]]))
            plot(FEATURES['discipline'])
    return
