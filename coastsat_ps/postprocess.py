import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal
import copy
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import os

from coastsat_pl.preprocess_tools import create_folder


#%%

def get_closest_datapoint(dates, dates_ts, values_ts):
    """
    Extremely efficient script to get closest data point to a set of dates from a very
    long time-series (e.g., 15-minutes tide data, or hourly wave data)
    
    Make sure that dates and dates_ts are in the same timezone (also aware or naive)
    
    KV WRL 2020

    Arguments:
    -----------
    dates: list of datetimes
        dates at which the closest point from the time-series should be extracted
    dates_ts: list of datetimes
        dates of the long time-series
    values_ts: np.array
        array with the values of the long time-series (tides, waves, etc...)
        
    Returns:    
    -----------
    values: np.array
        values corresponding to the input dates
        
    """
    
    # check if the time-series cover the dates
    if dates[0] < dates_ts[0] or dates[-1] > dates_ts[-1]: 
        raise Exception('Time-series do not cover the range of your input dates')
    
    # get closest point to each date (no interpolation)
    temp = []
    def find(item, lst):
        start = 0
        start = lst.index(item, start)
        return start
    for i,date in enumerate(dates):
        print('\rExtracting closest points: %d%%' % int((i+1)*100/len(dates)), end='')
        temp.append(values_ts[find(min(item for item in dates_ts if item > date), dates_ts)])
    values = np.array(temp)
    
    return values


#%% Tidal correction

def tidal_correction(settings, tide_settings, sl_csv):

    # Initialise
    if type(tide_settings['beach_slope']) is list:
        if len(tide_settings['beach_slope']) != len(settings['transects_load'].keys()):
            raise Exception('Beach slope list length does not match number of transects')
    
    # unpack settings
    weight = tide_settings['weighting']
    contour = tide_settings['contour']
    offset = tide_settings['offset']
    
    # import sl data
    sl_csv_tide = copy.deepcopy(sl_csv)
    sl_csv_tide.loc[:,'Date'] = pd.to_datetime(sl_csv_tide.loc[:,'Date'], utc = True)
    
    # Import tide daa
    tide_data = pd.read_csv(os.path.join(settings['user_input_folder'], settings['tide_data']), parse_dates=['dates'])
    dates_ts = [_.to_pydatetime() for _ in tide_data['dates']]
    tides_ts = np.array(tide_data['tide'])
    
    # get tide levels corresponding to the time of image acquisition
    dates_sat = sl_csv_tide['Date'].to_list()
    sl_csv_tide['Tide'] = get_closest_datapoint(dates_sat, dates_ts, tides_ts)
    
    # Perform correction for each transect
    for i, ts in enumerate(settings['transects_load'].keys()):
        # Select beach slope
        if type(tide_settings['beach_slope']) is not list:
            beach_slope = tide_settings['beach_slope']
        else:
            beach_slope = tide_settings['beach_slope'][i]
        
        # Select ts data
        ps_data = copy.deepcopy(sl_csv_tide[['Date',ts, 'Tide']])
        ps_data = ps_data.set_index('Date')
        
        # apply correction
        correction = weight*(ps_data['Tide']-contour)/beach_slope + offset
        sl_csv_tide.loc[:, ts] += correction.values
    
    # save csv
    sl_csv_tide.to_csv(settings['sl_transect_csv'].replace('.csv', '_tide_corr.csv'))
    
    return sl_csv_tide


#%% Single transect plot

def ts_plot_single(settings, sl_csv, transect):
    
    # import PS data and remove nan
    ps_data = copy.deepcopy(sl_csv[['Date',transect]])
    ps_data.loc[:,'Date'] = pd.to_datetime(sl_csv.loc[:,'Date'], utc = True)
    ps_data = ps_data.set_index('Date')
    ps_data = ps_data[np.isfinite(ps_data[transect])]
    mean_ps = np.nanmean(ps_data[transect])
    
    # Initialise figure
    fig = plt.figure(figsize=(8,4))
    ax = fig.add_subplot(111)
    ax.set_title('Transect ' + transect + ' Timeseries Plot')
    ax.set(ylabel='Chainage [m]')
    ax.set(xlabel='Date [UTC]')      
          
    # PL plots
    #l1 = ax.fill_between(ps_data.index, ps_data[transect], y2 = mean_GT, alpha = 0.35, color = 'grey', label='PS Data', zorder = 0)
    #l1 = ax.scatter(ps_data.index, ps_data[transect], color = 'k', label='PS Data', marker = 'x', s = 10, linewidth = 0.5, zorder = 1)#, alpha = 0.75)
    l1, = ax.plot(ps_data.index, ps_data[transect], linewidth = 0.75, alpha = 1, color = 'grey', label='PS Data', zorder = 1)

    # Mean Position line
    l2 = ax.axhline(y = mean_ps, color='k', linewidth=0.75, label='Mean PS Position')

    # Interpolate to 2 week rolling mean
    savgol = False
    if savgol == True:
        roll_days = 15
        interp_PL = pd.DataFrame(ps_data.resample('D').mean().interpolate(method = 'linear'))
        interp_PL_sav = signal.savgol_filter(interp_PL[np.isfinite(interp_PL)][transect], roll_days, 2)
        l3, = ax.plot(interp_PL.index, interp_PL_sav, linewidth = 0.75, alpha = 0.7, color = 'r', label=str(roll_days) + ' Day SavGol Filter', zorder = 2)
        #l3 = ax.fill_between(interp_PL.index, interp_PL[ts], y2 = mean_GT, alpha = 0.35, color = 'grey', label=str(roll_days) + ' Day SavGol Filter', zorder = 0)
    
        # Set legend
        ax.legend(handles = [l1, l2, l3], ncol = 3, bbox_to_anchor = (1,1), loc='upper right', framealpha = 1, fontsize = 'xx-small')
    else:
        # Set legend
        ax.legend(handles = [l1, l2], ncol = 3, bbox_to_anchor = (1,1), loc='upper right', framealpha = 1, fontsize = 'xx-small')

    
    # Find axis bounds
    if abs(max(ps_data[transect])) > abs(min(ps_data[transect])):
        bound = abs(max(ps_data[transect]))-mean_ps+5
    else:
        bound = abs(min(ps_data[transect]))-mean_ps+5
    
    # Set axis limits
    ax.set_ylim(top = mean_ps + bound)
    ax.set_ylim(bottom = mean_ps - bound)

    ax.set_xlim([min(ps_data.index)-(max(ps_data.index)-min(ps_data.index))/40,
                  max(ps_data.index)+(max(ps_data.index)-min(ps_data.index))/40])

    # Set grid and axis label ticks
    ax.grid(b=True, which='major', linestyle='-')
    ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.tick_params(labelbottom=False, bottom = False)
    ax.tick_params(axis = 'y', which = 'major', labelsize = 6)
        
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    #ax.xaxis.set_major_locator(mdates.MonthLocator())
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))

    #ax.set_yticklabels([])
    ax.tick_params(labelbottom=True, bottom = True) 
    ax.xaxis.set_minor_locator(mdates.MonthLocator())

    # save plot
    save_folder = os.path.join(settings['sl_thresh_ind'], 'Timeseries Plots')
    create_folder(save_folder)    
    fig.tight_layout()
    save_file = os.path.join(save_folder, 'transect_' + transect + '_timeseries.png')
    fig.savefig(save_file, dpi=200)

    plt.show()


