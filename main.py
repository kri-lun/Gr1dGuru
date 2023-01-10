import datetime
import os
import webbrowser

import fastf1
import matplotlib.pylab as plt
import PySimpleGUI as sg
from fastf1 import plotting
import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

## MatPlotLib config for FastF1
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=True)

## Creates cache directory path
class CacheDir:

    default = 'data/cache'

    def __init__(self, path):
        self.path = 'path'

    def Set(path):
        CacheExist = os.path.exists(path)
        if not CacheExist:
            os.makedirs(path)
        CacheDir.default = path

fastf1.Cache.enable_cache('data/cache')


## Gather info about driver
class Driver:
    def __init__(self, grandprix, abb):
        ## Driver abbreviation
        self.id = abb
        ## Get lap information from driver
        driver_session = grandprix.laps.pick_driver(self.id)
        self.bio = grandprix.get_driver(self.id)
        self.ses = driver_session
        self.tel = driver_session.get_car_data().add_distance()
        self.best = driver_session.pick_fastest()
        self.best_tel = driver_session.pick_fastest().get_car_data().add_distance()
        ## Color used in line graph
        self.teamcolor = fastf1.plotting.team_color(self.bio['TeamName'])



## Lists of data
class Lists:
    def __init__(self):
        self.Years = self.make('Years', list(range(2018, (int(datetime.datetime.today().year)))))
        self.GrandPrix = self.make('GrandPrix', list(fastf1.get_event_schedule(self.Years.list[-1])['EventName']))
        self.Sessions = self.make('Sessions', ['FP1', 'FP2', 'FP3', 'Qualifying', 'Race'])
        self.Drivers = self.make('Drivers', ['Select session'])
        self.DriversComp = self.make('DriversComp', [])
        self.SessionSlice = self.make('SessionSlice', ['Full Session', 'Specific Lap', 'Fastest Lap'])
        self.SesVarsX = self.make('SesVarsX', ['LapNumber'])
        self.SesVarsY = self.make('SesVarsY', ['LapTime', 'Stint', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'SpeedI1', 'SpeedI2', 'SpeedST','IsPersonalBest', 'Compound', 'TyreLife', 'TrackStatus'])
        self.LapVarsX = self.make('LapVarsX', ['Time', 'SessionTime', 'Distance'])
        self.LapVarsY = self.make('LapVarsY', ['Speed', 'RPM', 'nGear', 'Throttle', 'Brake', 'DRS'])
        self.DriverVars = self.make('DriverVars', ['Var 1', 'Var 2'])
        self.Laps = self.make('Laps', [1, 2, 3, 4, 5])

    ## Define attributes in "Lists" class
    def make(self, name, _list):
        class Make:
            def __init__(self, name, _list):
                self.name = name
                self.list = _list

            def print_list(self):
                print(self.list)
        return Make(name, _list)
        

## Get lap type
def set_data(driver, slice, lap_num):
    if slice == "Fastest Lap":
        self = driver.best_tel
    
    elif slice == "Specific Lap":
        lap_n = driver.ses[driver.ses['LapNumber'] == lap_num]
        lap_n_tel = lap_n.get_car_data().add_distance()
        self = lap_n_tel

    elif slice == "Full Session":
        self = driver.ses

    return self

 
def make_figure():
        fig = plt.figure(1, figsize=(16,9), constrained_layout=True)
        ## Subplot for better analysis
        ax = fig.subplots()
        return fig, ax

## Subplot data
def plot_ax(driver, data, figure, xvar, yvar, ax):
    ax.plot(data[xvar], data[yvar], color=driver.teamcolor, label=f'{driver.id}')
    ax.set_xlim(data[xvar].min(), data[xvar].max())


## Adds new dataset for comparison
def compare(grandprix, driver, slice, xvar, yvar, fig, ax, lap_num):
    for abb in driver:
        driver = Driver(grandprix, abb)
        data = set_data(driver, slice, lap_num)
        plot_ax(driver, data, fig, xvar, yvar, ax)


## Figure title
def set_title(grandprix, driver, yvar, slice, ses, lap_num, comp):
    global title
 
    if slice == "Specific Lap":
        analysis = f"Lap {lap_num}, {yvar} \n {grandprix.event.year} {grandprix.event['EventName']}, {ses}"

    elif slice != "Specific Lap":
        analysis = f"{slice}, {yvar} \n {grandprix.event.year} {grandprix.event['EventName']}, {ses}"

    if comp == True:
        title = analysis

    elif comp != True:
        title = f"{driver.bio['FullName']} " + analysis
    plt.suptitle(f"{title}")


def design_plot(ax, xvar, yvar):
        ## Axes title/label
        ax.set_xlabel(xvar)
        ax.set_ylabel(yvar)
 
        ax.minorticks_on()
        ax.grid(visible=True, axis='both', which='major', linewidth=0.9, alpha=0.3)

        ax.grid(visible=True, axis='both', which='minor', linestyle=':', linewidth=0.6, alpha=0.3)

        ## Driver info 
        ax.legend()

## Plot
def show_plot():
    plt.show()


def analyse():
    ## Input variables
    global year, gp, ses, abb, slice
    global lap_num, xvar, yvar, comp

    year = int(values['-YEAR-'])
    gp = values['-GP-'][0]
    ses = values['-SESSION-']
    abb = values['-DRIVER-']
    slice = values['-SLICE-']
    lap_num = int(values['-LAPNUM-'])
    xvar = values['-DRIVERXVAR-']
    yvar = values['-DRIVERYVAR-']
    comp = values['-COMPARE-']


    fig, ax = make_figure()

    ## Check compare checkbox status
    if comp == True:
        compare(grandprix, abb, slice, xvar, yvar, fig, ax, lap_num)
        driver = Driver(grandprix, abb[0])

    elif comp != True:
        driver = Driver(grandprix, abb[0])
        data = set_data(driver, slice, lap_num)
        plot_ax(driver, data, fig, xvar, yvar, ax)
        
    design_plot(ax, xvar, yvar)
    set_title(grandprix, driver, yvar, slice, ses, lap_num, comp)


    ## Plot
    show_plot()


def make_window():
    sg.theme('DarkBlue14')
    lists = Lists()
    menu_def = [[('&Help'), ['&About', 'E&xit', 'GitHub']]]

    header_layout = [[sg.Image(source='src/common/images/icon_header.png', size=(120, 60), expand_x=True, expand_y=True)],]


    ## Input menu
    menu_layout_column = [
            [sg.Menubar(menu_def, key='-MENU-')],
            [sg.Frame('', header_layout, size=(475,100), key='-HEAD-')],
            [sg.OptionMenu(lists.Years.list, default_value=f'{lists.Years.list[-1]}', expand_x=True, key='-YEAR-')],
            [sg.Button('Load Season', size=(10,1), expand_x=True)],
            [sg.Listbox(lists.GrandPrix.list, enable_events=True, expand_x=True, size=(None,8), select_mode='single', horizontal_scroll=False, visible=False, pad=(7,7,7,7), key='-GP-')],
            [sg.OptionMenu(lists.Sessions.list, default_value=f'Select Session...', expand_x=True, visible=False, key='-SESSION-')],
            [sg.Button('Drivers in Session', visible=False, expand_x=True, key='-LOADDRIVERS-')],
            ]

    ## Empty canvas space to draw graph
    second_menu_layout_column = [
            [sg.Listbox(lists.Drivers.list, enable_events=True, expand_x=True, size=(40,8), select_mode='single', horizontal_scroll=False, visible=False, pad=(7,7,7,7), key='-DRIVER-')],
            [sg.Checkbox('Compare drivers?', enable_events=True, visible=False, key='-COMPARE-')],
            [sg.OptionMenu(lists.SessionSlice.list, default_value=f'Evalutate Full Session?', disabled=True, expand_x=True, visible=False, key='-SLICE-')],
            [sg.Text('Enter Lap Number', visible=False, key='-LAPASK-')],
            [sg.Input(default_text= 0, expand_x=True, visible=False, key='-LAPNUM-')],
            [sg.Button('Select Telemetry', visible=False, disabled=True, expand_x=True, key='-LOADVARS-')],
            [sg.OptionMenu(lists.LapVarsY.list, default_value='Y Variable...', expand_x=True, visible=False, key='-DRIVERYVAR-')],
            [sg.OptionMenu(lists.LapVarsX.list, default_value='X Variable...', expand_x=True, visible=False, key='-DRIVERXVAR-')],
            [sg.Button('Confirm All', visible=False, expand_x=True, key='-CONFIRM ALL-')],
            [sg.Button('Submit', visible=False, disabled=True, expand_x=True, key='-PLOT-')],
    ]


    layout = [
        [sg.Column(menu_layout_column, vertical_alignment='top'),
        sg.VSeperator(),
        sg.Column(second_menu_layout_column, vertical_alignment='top')],
                ]


    window = sg.Window('Gr1dGuru', layout, margins=(10, 10), finalize=True, resizable=False)

    window.set_min_size(window.size)
    
    return window


def main():
    window = make_window()

    ## Event Loop
    while True:
        global values
        event, values = window.read(timeout=100)
        
        
        class ButtonFunc:

            ## About
            def About():
                about_layout = [[sg.Text('Gr1dGuru allows you to create simple Formula 1 lap time and telemetry graphs.')],
                                [sg.Text('Use the selection boxes to highlight your desired data and submit it!')],
                                [sg.Text('GridGuru is not affiliated with Formula 1 or the FIA.')]]
                about_win = sg.Window('About Gr1dGuru', about_layout, size=(500,100), modal=True, keep_on_top=True)
                event = about_win.read()
                if event == sg.WIN_CLOSED:
                    about_win.close()


            def GitHub():
                [webbrowser.open("https://github.com/kri-lun/Gr1dGuru")]


            ## Load Grand Prix weekends
            def LoadGPList():
                lists = Lists()
                lists.GrandPrix = lists.make('Grand Prix', list(fastf1.get_event_schedule(int(values['-YEAR-']))['EventName']))
                window.Element('-GP-').update(values=lists.GrandPrix.list, visible=True)
                window.Element('-SESSION-').update(visible=True)
                window.Element('-LOADDRIVERS-').update(visible=True, disabled=True)
                window.Element('-DRIVER-').update(visible=False)
                window.Element('-SLICE-').update(visible=False, disabled=True)
                window.Element('-LOADVARS-').update(visible=False, disabled=True)
                window.Element('-PLOT-').update(disabled=True, visible=False)
                window.Element('-DRIVERXVAR-').update(visible=False)
                window.Element('-DRIVERYVAR-').update(visible=False)
                window.Element('-CONFIRM ALL-').update(visible=False)
                window.Element('-COMPARE-').update(visible=False)
                window.Element('-LAPASK-').update(visible=False)
                window.Element('-LAPNUM-').update(visible=False)
                window.refresh()
                window.read(timeout=100)

            ## Load Drivers
            def LoadDriverList():
                lists = Lists()
                CacheDir.Set(CacheDir.default)
                fastf1.Cache.enable_cache(CacheDir.default)
                global grandprix
                grandprix = fastf1.get_session(int(values['-YEAR-']), str(values['-GP-']), str(values['-SESSION-']))
                grandprix.load()
                driver_list = grandprix.results['Abbreviation']
                Lists.Drivers = lists.make('Drivers', list(driver_list))
                window.Element('-DRIVER-').update(values=Lists.Drivers.list)
                window.Element('-DRIVER-').update(visible=True)
                window.Element('-COMPARE-').update(visible=True)
                window.Element('-SLICE-').update(visible=True, disabled=True)
                window.Element('-LOADVARS-').update(visible=True, disabled=True)
                window.Element('-PLOT-').update(disabled=True)
                window.Element('-LAPASK-').update(visible=False)
                window.Element('-LAPNUM-').update(visible=False)
                window.refresh()
                window.read(timeout=100)

            def LoadDriverVars():
                ## Get "Lists"
                lists = Lists()

                if values['-SLICE-'] == 'Full Session':
                    window.Element('-DRIVERXVAR-').update(values=lists.SesVarsX.list)
                    window.Element('-DRIVERYVAR-').update(values=lists.SesVarsY.list)
                    window.Element('-LAPASK-').update(visible=False)
                    window.Element('-LAPNUM-').update(visible=False)

                elif values['-SLICE-'] == 'Fastest Lap':
                    window.Element('-DRIVERXVAR-').update(values=lists.LapVarsX.list)
                    window.Element('-DRIVERYVAR-').update(values=lists.LapVarsY.list)
                    window.Element('-LAPASK-').update(visible=False)
                    window.Element('-LAPNUM-').update(visible=False)
                
                if values['-SLICE-'] == 'Specific Lap':
                    window.Element('-DRIVERYVAR-').update(values=lists.LapVarsX.list)
                    window.Element('-DRIVERXVAR-').update(values=lists.LapVarsY.list)
                    window.Element('-LAPASK-').update(visible=True)
                    window.Element('-LAPNUM-').update(visible=True)

                window.Element('-DRIVERXVAR-').update(visible=True)
                window.Element('-DRIVERYVAR-').update(visible=True)
                window.Element('-CONFIRM ALL-').update(visible=True)
                window.Element('-PLOT-').update(disabled=True, visible=True)
                window.refresh()
                window.read(timeout=100)


        ## Exit
        if event in (None, 'Exit'):
            break

        ##
        elif event == 'About':
            ButtonFunc.About()

        ##
        elif event == 'GitHub':
            ButtonFunc.GitHub()

        ##
        elif event == 'Load Season':
            ButtonFunc.LoadGPList()

        ##
        elif event == '-GP-':
            window.Element('-LOADDRIVERS-').update(disabled=False)
            window.Element('-PLOT-').update(disabled=False)
            window.refresh()

        ##
        elif event == '-DRIVER-':
            window.Element('-SLICE-').update(disabled=False)
            window.Element('-LOADVARS-').update(disabled=False)
            window.Element('-PLOT-').update(disabled=False)
            window.refresh()

        ##
        elif event == '-COMPARE-':
            if values['-COMPARE-'] == True:
                window.Element('-DRIVER-').update(select_mode='multiple')
                window.Element('-SLICE-').update(disabled=True)
                window.refresh()
                window.read(timeout=100)
            if values['-COMPARE-'] == False:
                window.Element('-DRIVER-').update(select_mode='single')
                window.Element('-SLICE-').update(disabled=True)
                window.refresh()
                window.read(timeout=100)

        ## Load Drivers        
        elif event == '-LOADDRIVERS-':
            ButtonFunc.LoadDriverList()

        ## Load telemetry        
        elif event == '-LOADVARS-':
            ButtonFunc.LoadDriverVars()

        ## Confirm All
        elif event == '-CONFIRM ALL-':
            window.Element('-PLOT-').update(disabled=False)
            window.refresh()
            window.read(timeout=100)

        ## Plot        
        elif event == '-PLOT-':
            analyse()

    window.close()
    exit(0)


## Main 
if __name__ == '__main__':
    sg.theme('DarkGrey14')
    main()
else:
    sg.theme('DarkGrey14')
    main()

