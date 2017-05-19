from __future__ import print_function

"""
For making matplotlib plots look nice. Also includes ASI styles.
"""

import matplotlib.pyplot as plt


def set_parameters(rc_params_key_value_list):
    """ Sets matplotlib.pyplot parameters.

    :param rc_params_key_value_list: list of tuples each of which is a key-value
    pair for plt.rcParams.
    :return: None.
    """

    for key_value in rc_params_key_value_list:
        try:
            plt.rcParams[key_value[0]] = key_value[1]
        except KeyError:
            print("Key not found.")


def set_asi_styles():
    """ Sets ASI styles.

    :return: None.
    """

    set_parameters([('patch.facecolor', '#00AEF9'),
                    ('patch.edgecolor', '#00AEF9'),
                    ('text.color', '#22333E'),
                    ('ytick.color', '#22333E'),
                    ('font.size', 16)])

