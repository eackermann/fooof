"""
07: Tuning & Troubleshooting
============================

Tips & tricks for choosing FOOOF parameters, tuning fits, and troubleshooting.
"""

###################################################################################################

import numpy as np

# FOOOF imports
from fooof import FOOOF, FOOOFGroup

# Import some utilities, and tools for creating synthetic power-spectra
from fooof.synth.params import param_sampler
from fooof.synth.gen import gen_power_spectrum, gen_group_power_spectra
from fooof.core.utils import group_three

###################################################################################################

# Set random state, for consistency for generating synthetic data
np.random.seed(321)

####################################################################################################
# FOOOF Settings
# --------------
#
# With default settings, FOOOF is minimally constrained. It defaults as such
# since there are not universal settings that work across all different dataset
# modalities. Appropriate settings also vary with power spectrum quality (noise,
# or effectively, the smoothness of the power spectrum), and frequency ranges.
#
# For any given dataset, FOOOF will likely need some tuning of parameters
# for optimal performance.
#
# To do so, we suggest using a combination of the following considerations:
#
# - A priori constraints, given your data, such as the number
#   of peaks you expect to extract
# - Qualitative analysis, guided by examing the the plotted
#   model fit results, as compared to input data
# - Quantitative analysis, considering the model fit and error
#   (however, see note at the bottom regarding interpreting model fit error)
#
# Tuning FOOOF is an imperfect art, and should be done carefully, as assumptions
# built into the settings chosen will impact the model results.
#
# We also recommend that FOOOF settings should not be changed between power
# spectra (across channels, trials, or subjects), if they are to be meaningfully
# compared. We therefore recommend first testing out FOOOF across some
# representative spectra, in order to select FOOOF settings, which you then keep
# constant for the full analysis.
#

####################################################################################################
# Tuning FOOOF
# ------------
#
# With the defaults, FOOOF is relatively unconstrained, and therefore, most
# commonly FOOOF will overfit, being overzealous at fitting small noisy bumps
# as peaks. If you move to a new dataset, you may also find you need to relax
# some settings, for better fits.
#
# You also need to make sure you pick an appropriate aperiodic fitting procedure,
# and that your data meets the assumptions of the approach you choose.
#
# The remainder of this notebook goes through some examples of setting FOOOF
# parameters to be most appropriate for various datasetes.
#

###################################################################################################
# Interpreting Model Fit Quality Measures
# ---------------------------------------
#
# FOOOF calculates and returns a couple metrics to assist with assessing the
# quality of the model fits. It calculates both the model fit error, as the
# root mean-squared error (RMSE) between the full model fit (`fooofed\_spectrum\_`)
# and the original power spectrum, as well as the R-squared correspondance
# between the original spectrum and the FOOOFed result.
#
# These scores can be used to assess how the model is performing. However
# interpreting these measures requires a bit of nuance. FOOOF is NOT optimized
# to minimize fit error / maximize r-squared at all costs. To do so typically
# results in fitting a large number of gaussian processes, in a way that overfits noise.
#
# FOOOF is therefore tuned to try and measure the aperiodic signal and peaks
# in a parsimonious manner, such as to not overfit noise, and following a
# fuzzy definition of only fitting peaks where there are actually significant
# peaks over and above the aperiodic signal, and the noise.
#
# One way we tested this is by assessing the model as compared to how expert
# human raters labeled putative oscillatory 'peaks'. As such, overall the
# model is not directly designed to optimize model fit error / r-squared.
#
# Given this, while high error / low r-squared may indicate a poor model fit,
# very low error / high r-squared may also indicate a power spectrum that is
# overfit, in particular in which the peak parameters from the model may
# reflect overfitting by modelling too many peaks, and thus not offer a
# good description of the underlying data.
#
# We therefore recommend that, for a given dataset, initial explorations
# should involve checking both cases in which model fit error is particularly
# large, as well as when it is particularly low. These explorations can be
# used to set parameters that are suitable for running across a group.
# There are not universal parameters that optimize this, and so FOOOF
# leaves it up to the user to set parameters appropriately to not
# under- or over-fit for a given modality / dataset / application.
#

###################################################################################################
# Reducing Overfitting
# --------------------
#
# If FOOOF appears to be overfitting (for example, fitting too many Gaussians to small bumps), try:
#
# - Setting a lower-bound bandwidth-limit, to exclude fitting very narrow peaks, that may be noise
# - Setting a maximum number of peaks that the algorithm may fit: `max_n_peaks`
#
#   - If set, the algorithm will fit (up to) the `max_n_peaks` highest power peaks.
# - Setting a minimum absolute peak height: `min_peak_height`
#

###################################################################################################

# Generate a noisy synthetic power spectrum

# Set the frequency range to generate the power spectrum
f_range = [1, 50]
# Set aperiodic background signal parameters, as [offset, exponent]
ap_params = [20, 2]
# Gaussian peak parameters
gauss_params = [10, 1.0, 2.5, 20, 0.8, 2, 32, 0.6, 1]
# Set the level of noise to generate the power spectrum with
nlv = 0.1

# Create a synthetic power spectrum
freqs, spectrum = gen_power_spectrum(f_range, ap_params, gauss_params, nlv)

###################################################################################################

# Fit an (unconstrained) FOOOF model, liable to overfit
fm = FOOOF()
fm.report(freqs, spectrum)

###################################################################################################
#
# Notice that in the above fit, we are very likely to think that FOOOF has
# been overzealous in fitting peaks, and is therefore overfitting.
#
# This is also suggested by the model r-squared, which is suspiciously
# high, given the amount of noise we expect.
#
# To reduce this kind of overfitting, we can update the FOOOF parameters.
#

###################################################################################################

# Update settings to fit a more constrained FOOOF model, to reduce overfitting
fm = FOOOF(peak_width_limits=[1, 8], max_n_peaks=6, min_peak_height=0.4)
fm.report(freqs, spectrum)

###################################################################################################
#
# The synthetic definition is defined in terms of Gaussian parameters (these are
# slightly different from the peak parameters - see the note in tutorial 02).
#
# We can compare how FOOOF, with our updated settings, compares to the
# ground truth of the synthetic spectrum.
#

###################################################################################################

# Compare ground truth synthetic parameters to model fit results
print('Ground Truth \t\t FOOOF Reconstructions')
for sy, fi in zip(np.array(group_three(gauss_params)), fm._gaussian_params):
    print('{:5.2f} {:5.2f} {:5.2f} \t {:5.2f} {:5.2f} {:5.2f}'.format(*sy, *fi))

###################################################################################################
# Power Spectra with No Peaks
# ---------------------------
#
# A known case in which FOOOF can overfit is in power spectra in which no peaks
# are present. In this case, the standard deviation can be very low, and so the
# relative peak height check (`min_peak_threshold`) is very liberal at keeping gaussian fits.
#
# If you expect, or know, you have power spectra without peaks in your data,
# we therefore recommend making sure you set some value for `min_peak_height`,
# as otherwise FOOOF is unlikely to appropriately fit power spectra as having
# no peaks. Setting this value requires checking the scale of your power spectra,
# allowing you to define an absolute threshold for extracting peaks.
#

###################################################################################################
# Reducing Underfitting
# ---------------------
#
# If you are finding that FOOOF is underfitting:
#
# - First check and perhaps loosen any restrictions from `max_n_peaks` and `min_peak_height`
# - Try updating `peak_threshold` to a lower value
# - Bad fits may come from issues with aperiodic signal fitting
#

###################################################################################################
# Create a cleaner synthetic power spectrum
# -----------------------------------------

# Set the frequency range to generate the power spectrum
f_range = [1, 50]
# Aperiodic parameters, as [offset, exponent]
ap_params = [20, 2]
# Gaussian peak parameters
gauss_params = [10, 1.0, 1.0, 20, 0.3, 1.5, 32, 0.25, 1]
# Set the level of noise to generate the power spectrum with
nlv = 0.025

# Create a synthetic power spectrum
freqs, spectrum = gen_power_spectrum([1, 50], ap_params, gauss_params, nlv=nlv)

# Update settings to make sure they are sensitive to smaller peaks in smoother power spectra
fm = FOOOF(peak_width_limits=[1, 8], max_n_peaks=6, min_peak_height=0.2)
fm.report(freqs, spectrum)

###################################################################################################

# Check reconstructed parameters from synthetic definition
print('Ground Truth \t\t FOOOF Reconstructions')
for sy, fi in zip(np.array(group_three(gauss_params)), fm._gaussian_params):
    print('{:5.2f} {:5.2f} {:5.2f} \t {:5.2f} {:5.2f} {:5.2f}'.format(*sy, *fi))

###################################################################################################
# Checking Fits Across a Group
# ----------------------------

# Set the parameters options for aperiodic signal and Gaussian peaks
ap_opts = param_sampler([[20, 2], [50, 2.5], [35, 1.5]])
gauss_opts = param_sampler([[], [10, 0.5, 2], [10, 0.5, 2, 20, 0.3, 4]])

# Generate a group of power spectra
freqs, power_spectra, syn_params = gen_group_power_spectra(10, [3, 50], ap_opts, gauss_opts)

###################################################################################################

# Initialize a FOOOFGroup
fg = FOOOFGroup(peak_width_limits=[1, 6])

###################################################################################################

# Fit FOOOF and report on the group
fg.report(freqs, power_spectra)

###################################################################################################

# Find the index of the worst FOOOF fit from the group
worst_fit_ind = np.argmax(fg.get_all_data('error'))

# Extract this FOOOF fit from the group, into a FOOOF object
fm = fg.get_fooof(worst_fit_ind, regenerate=True)

###################################################################################################
#
# Check out the model fit of the extracted FOOOF model
fm.print_results()
fm.plot()


###################################################################################################
#
# You can also loop through all the results in a test group, extracting all fits
# that meet some criterion that makes them worth checking.
#
# This might be checking for fits above some error threshold, as below, but note
# that you may also want to do a similar procedure to examine fits with the lowest
# error, to check if FOOOF may be overfitting, or perhaps fits with a particularly
# large number of gaussians.

###################################################################################################

# Extract all fits that are above some error threshold, for further examination.
#  You could also do a similar analysis for particularly low errors
to_check = []
for ind, res in enumerate(fg):
    if res.error > 0.010:
        to_check.append(fg.get_fooof(ind, regenerate=True))

# A more condensed version of the procedure above can also be used, like this:
#to_check = [fg.get_fooof(ind, True) for ind, res in enumerate(fg) if res.error > 0.010]

###################################################################################################

# Loop through the problem fits, checking the plots, and saving out reports, to check later.
for ind, fm in enumerate(to_check):
    fm.plot()
    fm.save_report('Report_ToCheck_#' + str(ind))

###################################################################################################
# Reporting Bad Fits
# ------------------
#
# If, after working through these suggestions, you are still getting bad fits,
# and/or are just not sure what is going on, please get in touch! We will hopefully
# be able to make further recommendations, and this also serves as a way for us to
# investigate when and why FOOOF fails, so that we can continue to make it better.
#
# You can report issues on Github `here <https://github.com/fooof-tools/fooof>`_
# or get in touch with us by e-mail at voytekresearch@gmail.com.
#
# FOOOF also includes a helper method to print out instructions for reporting
# bad fits / bugs back to us, as demonstrated below.
#

###################################################################################################

# Print out instructions to report bad fits
#  Note you can also call this from FOOOFGroup, and from instances (ex: fm.print_report_issue())
FOOOF.print_report_issue()
