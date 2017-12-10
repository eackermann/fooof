"""Generate reports from FOOOF and FOOOF derivative objects."""

import os

import matplotlib.pyplot as plt
from matplotlib import gridspec

from fooof.strings import gen_settings_str, gen_results_str_fm, gen_results_str_fg
from fooof.plts.fg import plot_fg_bg, plot_fg_gf, plot_fg_osc_cens

###################################################################################################
###################################################################################################

def create_report_fm(fm, save_name, save_path='', plt_log=False):
    """Generate and save out a report for FOOOF object.

    Parameters
    ----------
    fm : FOOOF() object
        FOOOF object, containing results from fitting a PSD.
    save_name : str
        Name to give the saved out file.
    save_path : str, optional
        Path to directory in which to save. If not provided, saves to current directory.
    plt_log : bool, optional
        Whether or not to plot the frequency axis in log space. default: False
    """

    font = _report_settings()

    # Set up outline figure, using gridspec
    fig = plt.figure(figsize=(16, 20))
    grid = gridspec.GridSpec(3, 1, height_ratios=[0.8, 1.0, 0.7])

    # First - text results
    ax0 = plt.subplot(grid[0])
    results_str = gen_results_str_fm(fm)
    ax0.text(0.5, 0.2, results_str, font, ha='center')
    ax0.set_frame_on(False)
    ax0.set_xticks([])
    ax0.set_yticks([])

    # Second - data plot
    ax1 = plt.subplot(grid[1])
    fm.plot(plt_log=plt_log, ax=ax1)

    # Third - FOOOF settings
    ax2 = plt.subplot(grid[2])
    settings_str = gen_settings_str(fm, False)
    ax2.text(0.5, 0.2, settings_str, font, ha='center')
    ax2.set_frame_on(False)
    ax2.set_xticks([])
    ax2.set_yticks([])

    # Save out the report
    plt.savefig(os.path.join(save_path, save_name + '.pdf'))
    plt.close()


def create_report_fg(fg, save_name, save_path=''):
    """Generate and save out a report for FOOOFGroup object.

    Parameters
    ----------
    fg : FOOOFGroup() object
        FOOOFGroup object, containing results from fitting a group of PSDs.
    save_name : str
        Name to give the saved out file.
    save_path : str, optional
        Path to directory in which to save. If not provided, saves to current directory.
    """

    font = _report_settings()

    # Initialize figure
    fig = plt.figure(figsize=(16, 20))
    gs = gridspec.GridSpec(3, 2, wspace=0.35, hspace=0.25, height_ratios=[1.5, 1.0, 1.2])

    # First / top: text results
    ax0 = plt.subplot(gs[0, :])
    results_str = gen_results_str_fg(fg)
    ax0.text(0.5, 0.0, results_str, font, ha='center')
    ax0.set_frame_on(False)
    ax0.set_xticks([])
    ax0.set_yticks([])

    # Background parameters plot
    ax1 = plt.subplot(gs[1, 0])
    plot_fg_bg(fg, ax1)

    # Goodness of fit plot
    ax2 = plt.subplot(gs[1, 1])
    plot_fg_gf(fg, ax2)

    # Oscillations plot
    ax3 = plt.subplot(gs[2, :])
    plot_fg_osc_cens(fg, ax3)

    # Save out the report
    plt.savefig(os.path.join(save_path, save_name + '.pdf'))
    plt.close()


def _report_settings():
    """Return settings to be used for all reports."""

    # Set the font description for saving out text with matplotlib
    font = {'family': 'monospace',
            'weight': 'normal',
            'size': 16}

    return font
