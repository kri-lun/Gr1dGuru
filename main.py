import os
import datetime
import webbrowser


import fastf1
import matplotlib.pylab as plt
import PySimpleGUI as sg
from fastf1 import plotting


import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


## MatPlotLib config for FastF1
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=True)

## Creates cache directory path 
class CacheDir:

    default = './data/cache'

    def __init__(self, path):
        self.path = 'path'

    def Set(path):
        CacheExist = os.path.exists(path)
        if not CacheExist:
            os.makedirs(path)
        CacheDir.default = path

fastf1.Cache.enable_cache('./data/cache')

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
        self.Drivers = self.make('Drivers', ['Driver 1', 'Driver 2'])
        self.SessionSlice = self.make('SessionSlice', ['Full Session', 'Specific Lap', 'Fastest Lap'])
        self.SesVarsX = self.make('SesVarsX', ['LapNumber'])
        self.SesVarsY = self.make('SesVarsY', ['LapTime', 'Stint', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'SpeedI1', 'SpeedI2', 'SpeedST','IsPersonalBest', 'Compound', 'TyreLife', 'TrackStatus'])
        self.LapVarsX = self.make('LapVarsX', ['Time', 'SessionTime', 'Distance'])
        self.LapVarsY = self.make('LapVarsY', ['Speed', 'RPM', 'nGear', 'Throttle', 'Brake', 'DRS'])
        self.DriverVars = self.make('DriverVars', ['DriverVar1, DriverVar2'])
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
        

def make_window():
    sg.theme('DarkBlue14')
    ## Access "Lists" attributes
    lists = Lists()
    menu_def = [[('&Help'), ['&About', 'E&xit', '&GitHub']]]

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
            [sg.Listbox(lists.Drivers.list, enable_events=True, expand_x=True, size=(None,8), select_mode='single', horizontal_scroll=False, visible=False, pad=(7,7,7,7), key='-DRIVER-')],
            [sg.OptionMenu(lists.SessionSlice.list, default_value=f'Evalutate Full Session?', disabled=True, expand_x=True, visible=False, key='-SLICE-')],
            [sg.Text('Enter Lap Number', visible=False, key='-LAPASK-')],
            [sg.Input(default_text= 0, expand_x=True, visible=False, key='-LAPNUM-')],
            [sg.Button('Select Telemetry', visible=False, disabled=True, expand_x=True, key='-LOADVARS-')],
            [sg.OptionMenu(lists.LapVarsY.list, default_value='Y Variable...', expand_x=True, visible=False, key='-DRIVERYVAR-')],
            [sg.OptionMenu(lists.LapVarsX.list, default_value='X Variable...', expand_x=True, visible=False, key='-DRIVERXVAR-')],
            [sg.Button('Confirm All', visible=True, expand_x=True, key='-CONFIRM ALL-')],
            [sg.Button('Submit', visible=True, disabled=True, expand_x=True, key='-SUBMIT-')],
            ]


    ## Empty canvas space to draw graph
    graph_layout_column = [
    [sg.Canvas(size=(1200, 900), key= '-CANVAS-', background_color='#21273d')]
    ]

    layout = [
        [sg.Column(menu_layout_column, vertical_alignment='top'),
        ## Vertical seperating line
        sg.VSeparator(),
        sg.Column(graph_layout_column)],
                ]


    window = sg.Window('Gr1dGuru', layout, margins=(10, 0), finalize=True, resizable=True)

    window.set_min_size(window.size)
    
    return window


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


def make_figure(x, y):
    driver = Driver(grandprix, abb[0])
    fig = plt.figure(1, figsize=(12, 9), dpi=100, constrained_layout=True)
    ## Subplot for better analysis
    ax = plt.subplots(figsize=(12,9))

    plt.plot(x, y, color=driver.teamcolor)
    ## Title based on lap type
    if slice == "Specific Lap":
        plotTitle = f"Lap {lap_num}, {yvar} {grandprix.event.year} {grandprix.event['EventName']}, {ses}"
        plt.title(plotTitle, fontsize=12)

    elif slice != "Specific Lap":
        plotTitle = f"{slice}, {yvar} {grandprix.event.year} {grandprix.event['EventName']}, {ses}"
        plt.title(plotTitle, fontsize=12)

    ## Label axes
    plt.xlabel(xvar)
    plt.ylabel(yvar)
    plt.grid(True)
    return plt.gcf()

## Draws figure in tkinter canvas
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def submit():
    ## Input values
    global year, gp, ses, abb, slice
    global lap_num, xvar, yvar

    year = int(values['-YEAR-'])
    gp = values['-GP-'][0]
    ses = values['-SESSION-']
    abb = values['-DRIVER-']
    slice = values['-SLICE-']
    lap_num = int(values['-LAPNUM-'])
    xvar = values['-DRIVERXVAR-']
    yvar = values['-DRIVERYVAR-']

    driver = Driver(grandprix, abb[0])
    data = set_data(driver, slice, lap_num)
    fig = make_figure(data[xvar], data[yvar])
    draw_figure(window['-CANVAS-'].TKCanvas,  fig)


window = make_window() 


def main():


    ## Event loop
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
                window.Element('-SUBMIT-').update(disabled=True, visible=False)
                window.Element('-DRIVERXVAR-').update(visible=False)
                window.Element('-DRIVERYVAR-').update(visible=False)
                window.Element('-CONFIRM ALL-').update(visible=False)
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
                window.Element('-SLICE-').update(visible=True, disabled=True)
                window.Element('-LOADVARS-').update(visible=True, disabled=True)
                window.Element('-SUBMIT-').update(disabled=True)
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
                window.Element('-SUBMIT-').update(disabled=True, visible=True)
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
            window.Element('-SUBMIT-').update(disabled=False)
            window.refresh()

        ##
        elif event == '-DRIVER-':
            window.Element('-SLICE-').update(disabled=False)
            window.Element('-LOADVARS-').update(disabled=False)
            window.Element('-SUBMIT-').update(disabled=False)
            window.refresh()

        ## Load Drivers        
        elif event == '-LOADDRIVERS-':
            ButtonFunc.LoadDriverList()

        ## Load telemetry      
        elif event == '-LOADVARS-':
            ButtonFunc.LoadDriverVars()

        ## Confirm All
        elif event == '-CONFIRM ALL-':
            window.Element('-SUBMIT-').update(disabled=False)
            window.refresh()
            window.read(timeout=100)

        ## Plot        
        elif event == '-SUBMIT-':
            submit()

    window.close()
    exit(0)


## Main 
if __name__ == '__main__':
    sg.theme('DarkBlue14')
    main()
else:
    sg.theme('DarkBlue14')
    main()
