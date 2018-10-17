
from scipy import signal
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import multipletau # not included in Anaconda and thus needs 'pip install multipletau'
#from statsmodels.tsa.stattools import acf

'''
TODO
traceをどうやって渡すかを考える
'''

def detrend(self, detrend_method='savgol', n_div=20):
    '''
    Detrending noisy data
    :param self: traces
    :param detrend_method:
    :param n_div:
    :return:
    '''
    #atraces = self.traces
    print('Default detrend value: savgol filter, linear is an optional method')
    if detrend_method == 'linear':
        n_break = int(L/n_div) # ndiv: number of partiations in linear detrending
        #print(n_break)
        for (i, trace) in enumerate(traces):
            break_points = np.arange(start=n_break, stop=trace.shape[0]-n_break,step=n_break)
            #print(break_points)
            trace_detrend = signal.detrend(trace, bp=break_points)
            traces[i, :] = trace_detrend + intensity_means[i]
            trace_detrend_ma = np.convolve(traces[i, :], np.ones(step_ma)/step_ma, mode='same')

    elif detrend_method == 'savgol': #Savitzky-Golay filter
        decay_factors = []
        for (i, trace) in enumerate(traces):
            trace_ma = traces_ma[i][idx_trunc]
            sparse_trace_smoothed = signal.savgol_filter(trace_ma, window_length=501, polyorder=3)
            intpfunc = interp1d(idx_trunc, sparse_trace_smoothed, kind='linear')
            trace_smoothed = intpfunc(idx_full)
            f0 = trace_smoothed[0]
            decay_factor = np.sqrt(trace_smoothed/f0)
            decay_factors.append(decay_factor)
            traces[i, :] = np.divide(traces_ble[i][:], decay_factor) + f0 * (1 - decay_factor)
            trace_detrend_ma = np.convolve(traces[i, :], np.ones(step_ma)/step_ma, mode='same')
    else:
        print("invalid value")

    return trace_detrend_ma


def bt_correction(self, blethr_coef=0.0375):
    '''
    Bleedthrough correction
    :param self:
    :param blethr_coef: to the 1st channel from the 2nd dye (From green to red)
    :return:
    '''
    traces_ble = [traces[0,:] -  blethr_coef * traces[1, :], traces[1, :]]
    traces_ma = []
    for (dye, trace) in zip(dyes, traces_ble):
        trace_ma = np.convolve(trace, np.ones(step_ma)/step_ma, mode='same')
        traces_ma.append(trace_ma)
    return traces_ma

def mt_correction(self, t0=0, tf=4000000):
    '''
    Multiple tau correction
    :param self: refer traces
    :param t0:
    :param tf: number of timepoint data
    :return:
    '''
    autocors = []
    # calculation of autocorrelation
    for trace in traces:
        y_mtau = multipletau.autocorrelate(trace[t0:tf], normalize=True)
        autocors.append(y_mtau)

    # calculation of crosscorrelation
    xcor = multipletau.correlate(traces[0, t0:tf], traces[1, t0:tf], normalize=True)
    xcor = xcor / np.sqrt(np.mean(decay_factors[0])) / np.sqrt(np.mean(decay_factors[1]))

    return autocors, xcor

def diff_autocor_fixeds(t, tau, N):
    # input
    # t: time
    # tau: correlation time parameter
    # N: molecular number
    # output
    # g: auto correlation function
    s = 5.8
    si2 = 1/s/s
    r = t / tau
    return 1/N * (1/ (1 + r)) * np.sqrt((1 / (1 + si2 * r)))

def model_fitting(self, autocors, xcor, t1=1, t2=150):
    '''
    sampling_intervalの値を取ってくる
    :param self:
    :param xcor:
    :param t1:
    :param t2:
    :return:
    '''
    timepoints = xcor[t1:t2, 0] * sampling_interval
    auto_popts = []

    # autocorrelation fitting triplet
    for autocor in autocors:
        G = autocor[t1:t2, 1]
        popt, pcov = curve_fit(diff_autocor_fixeds, timepoints, G, p0=[1000, 100])
        auto_popts.append(popt)

    # Cross-correlation fitting
    G = xcor[t1:t2, 1]
    param_bounds = ([10, 0], [np.inf, np.inf])
    cross_popt, pcov = curve_fit(diff_autocor_fixeds, timepoints, G, p0=[1000, 1000], bounds=param_bounds)
    print('Boundratio G' + str(auto_popts[0][1] / cross_popt[1]))
    print('Boundratio R' + str(auto_popts[1][1] / cross_popt[1]))

    return auto_popts, cross_popt





