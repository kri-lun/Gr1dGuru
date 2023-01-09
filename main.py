import datetime
import os

import fastf1
import matplotlib.pylab as plt
import pandas as pd
import PySimpleGUI as sg
from fastf1 import plotting
import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

## Setter opp matplotlib med fastf1. Lar oss plotte timedelta verdier bedre.
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1', misc_mpl_mods=True)

## Lager directory hvor data kan bli cachet. Dersom filstien ikke eksisterer, lager metoden en ny filsti. 
class CacheDir:

    default = './data/cache'

    def __init__(self, path):
        path = 'path'

    def Set(path):
        CacheExist = os.path.exists(path)
        if not CacheExist:
            os.makedirs(path)
        CacheDir.default = path

fastf1.Cache.enable_cache('./data/cache')

## Klasse som tar argumentene grandprix og abb(abbreviation/forkortelse for navnet til sjåføren)
## Henter fører informasjon fra grandprix argument og assigner til "laps" og "driver_info" variabler for gjenbruk.
class Driver:
    def __init__(self, grandprix, abb):
        self.id = abb
        driver_session = grandprix.laps.pick_driver(self.id)
        self.bio = grandprix.get_driver(self.id)
        self.ses = driver_session
        self.tel = driver_session.get_car_data().add_distance()
        self.best = driver_session.pick_fastest()
        self.best_tel = driver_session.pick_fastest().get_car_data().add_distance()
        self.teamcolor = fastf1.plotting.team_color(self.bio['TeamName'])



## Klasse som lager lister om diverse informasjon som brukeren kan velge å analysere i GUI.
class Lists:
    def __init__(self):
        self.Years = self.make('Years', list(range(2018, (int(datetime.datetime.today().year)+1))))
        self.GrandPrix = self.make('GrandPrix', list(fastf1.get_event_schedule(self.Years.list[-1])['EventName']))
        self.Sessions = self.make('Sessions', ['FP1', 'FP2', 'FP3', 'Qualifying', 'Race'])
        self.Drivers = self.make('Drivers', ['Driver 1', 'Driver 2'])
        self.DriversComp = self.make('DriversComp', [])
        self.SessionSlice = self.make('SessionSlice', ['Full Session', 'Specific Lap', 'Fastest Lap'])
        self.SesVarsX = self.make('SesVarsX', ['LapNumber'])
        self.SesVarsY = self.make('SesVarsY', ['LapTime', 'Stint', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'SpeedI1', 'SpeedI2', 'SpeedST','IsPersonalBest', 'Compound', 'TyreLife', 'TrackStatus'])
        self.LapVarsX = self.make('LapVarsX', ['Time', 'SessionTime', 'Distance'])
        self.LapVarsY = self.make('LapVarsY', ['Speed', 'RPM', 'nGear', 'Throttle', 'Brake', 'DRS'])
        self.DriverVars = self.make('DriverVars', ['Var 1', 'Var 2'])
        self.Laps = self.make('Laps', [1, 2, 3, 4, 5])


    def make(self, name, _list):
        class Make:
            def __init__(self, name, _list):
                self.name = name
                self.list = _list

            def print_list(self):
                print(self.list)
        return Make(name, _list)
        

## Funksjon som lar brukeren bestemme hvilke runder som skal analyseres. 
## best_tel henter data fra sjåførens beste runde, lap_num tar et user input og henter data fra int inputen til brukeren. Full session henter data fra hele kvalifiseringsøkten.
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

## Definerer egenskaper til matplotlib plot som vises i resultat-vinduet. 
## Bruker subplot funksjon for å kunne plotte og COMPAREe forskjellige førere sin data samtidig i samme figur. 
def make_figure():
        fig = plt.figure(1, figsize=(16,9), constrained_layout=True)
        ax = fig.subplots()
        return fig, ax

def plot_ax(driver, data, figure, xvar, yvar, ax):
    ax.plot(data[xvar], data[yvar], color=driver.teamcolor, label=f'{driver.id}')
    ax.set_xlim(data[xvar].min(), data[xvar].max())

## Plotter data fra data argument til hver akse i subploten. 
## Setter fargen på linjen til sjåførens lagfarge. Label blir satt til f-string for å importere verdien av driver.id
## Setter minimum og maksimal grense til x-aksen ved å hente data fra 'data'. Sørger for at all data passer i figuren.  

def compare(grandprix, driver, slice, xvar, yvar, fig, ax, lap_num):
    for abb in driver:
        driver = Driver(grandprix, abb)
        data = set_data(driver, slice, lap_num)
        plot_ax(driver, data, fig, xvar, yvar, ax)

## Bestemmer beskrivelse av analyse i tittel over graf. F.eks Fastest lap, Brake, \n 2020 Austrian Grand Prix, Q.
def set_title(grandprix, driver, yvar, slice, ses, lap_num, comp):
    global title
    ## Dersom valg av runde er spesifikk runde, blir runde-nr med i tittelen. 
    if slice == "Specific Lap":
        analysis = f"Lap {lap_num}, {yvar} \n {grandprix.event.year} {grandprix.event['EventName']}, {ses}"

    ## Hvis valg av runde ikke er en spesifikk runde, består tittelen av enten full økt eller raskeste runde.
    elif slice != "Specific Lap":
        analysis = f"{slice}, {yvar} \n {grandprix.event.year} {grandprix.event['EventName']}, {ses}"

    ## Hvis COMPAREing av sjåfører er valgt, gjelder kun regler ovenfor. 
    if comp == True:
        title = analysis

    ## Dersom kun en sjåfør er valgt, vil dens fulle navn vises i tittelen sammen med tidligere regler. 
    elif comp != True:
        title = f"{driver.bio['FullName']} " + analysis
    plt.suptitle(f"{title}")

def design_plot(ax, xvar, yvar):
        ## xvar og yvar representerer hva brukeren vil vise av telemetry. F.eks throttle og distance
        ax.set_xlabel(xvar)
        ax.set_ylabel(yvar)

        ## Skrur på minorticks for å gi et bedre bilde av telemetrydata. 
        ax.minorticks_on()
        ax.grid(visible=True, axis='both', which='major', linewidth=0.9, alpha=0.3)

        ## Endrer minorticks linjestil og linjebredde for å stå ut mindre enn hovedrutene.
        ax.grid(visible=True, axis='both', which='minor', linestyle=':', linewidth=0.6, alpha=0.3)

        ## Viser en oversikt av sjåfør som vises i abb(abbreviation/forkortelse) og hvilken farge som representerer hver sjåfør. 
        ax.legend()

## Viser graf
def show_plot():
    plt.show()

##def save_fig():

def analyse():
    ## Globale input verdier
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

    ## Lager figur
    fig, ax = make_figure()

    ## Sjekk compare status
    ## Henter sjåfør data for 
    # Plot Variables
    if comp == True:
        compare(grandprix, abb, slice, xvar, yvar, fig, ax, lap_num)
        driver = Driver(grandprix, abb[0])

    elif comp != True:
        driver = Driver(grandprix, abb[0])
        data = set_data(driver, slice, lap_num)
        plot_ax(driver, data, fig, xvar, yvar, ax)
        
    design_plot(ax, xvar, yvar)
    set_title(grandprix, driver, yvar, slice, ses, lap_num, comp)


    # Show Plot
    show_plot()




def make_window():
    sg.theme('DarkBlue14')
    lists = Lists()
    menu_def = [[('&Help'), ['&About', 'E&xit']]]

    header_layout = [[sg.Image(source='src/common/images/icon_header.png', size=(120, 60), expand_x=True, expand_y=True)],]


    ## Input meny
    ## Ulike valg for X og Y akse Telemetry for å gjøre brukerens valg mest mulig kompatibel med hverandre. 
    menu_layout_column = [
            [sg.Menubar(menu_def, key='-MENU-')],
            [sg.Frame('', header_layout, size=(500,100), key='-HEAD-')],
            [sg.OptionMenu(lists.Years.list, default_value=f'{lists.Years.list[-1]}', expand_x=True, key='-YEAR-')],
            [sg.Button('Load Season', size=(10,1), expand_x=True)],
            [sg.Listbox(lists.GrandPrix.list, enable_events=True, expand_x=True, size=(None,10), select_mode='single', horizontal_scroll=False, visible=False, pad=(7,7,7,7), key='-GP-')],
            [sg.OptionMenu(lists.Sessions.list, default_value=f'Select Session...', expand_x=True, visible=False, key='-SESSION-')],
            [sg.Button('Drivers in Session', visible=False, expand_x=True, key='-LOADDRIVERS-')],
            [sg.Listbox(lists.Drivers.list, enable_events=True, expand_x=True, size=(None,10), select_mode='single', horizontal_scroll=False, visible=False, pad=(7,7,7,7), key='-DRIVER-')],
            [sg.Checkbox('Compare drivers?', enable_events=True, visible=False, key='-COMPARE-')],
            [sg.OptionMenu(lists.SessionSlice.list, default_value=f'Evalutate Full Session?', disabled=True, expand_x=True, visible=False, key='-SLICE-')],
            [sg.Text('Enter Lap Number', visible=False, key='-LAPASK-')],
            [sg.Input(default_text= 0, expand_x=True, visible=False, key='-LAPNUM-')],
            [sg.Button('Select Telemetry', visible=False, disabled=True, expand_x=True, key='-LOADVARS-')],
            [sg.OptionMenu(lists.LapVarsY.list, default_value='Y Variable...', expand_x=True, visible=False, key='-DRIVERYVAR-')],
            [sg.OptionMenu(lists.LapVarsX.list, default_value='X Variable...', expand_x=True, visible=False, key='-DRIVERXVAR-')],
            [sg.Button('Confirm All', visible=True, expand_x=True, key='-CONFIRM ALL-')],
            [sg.Button('Submit', visible=True, disabled=True, expand_x=True, key='-PLOT-')],
            ]


    graph_layout_column = [
    [sg.Canvas(size=(600, 600), key= '-CANVAS-', background_color='DarkGrey',)]
    ]

    layout = [
        [sg.Column(menu_layout_column),
        sg.VSeparator(),
        sg.Column(graph_layout_column)],
                ]


    window = sg.Window('Gr1dGuru', layout, margins=(10, 10), finalize=True, resizable=False)

    window.set_min_size(window.size)
    
    return window


def main():
    window = make_window()

    # Window Open, Begin Event Loop
    while True:
        global values
        event, values = window.read(timeout=100)
        
        
        class ButtonFunc:

            #About
            def About():
                about_layout = [[sg.Text('Gr1dGuru allows you to create simple Formula 1 lap time and telemetry graphs.')],
                                [sg.Text('Use the selection boxes to highlight your desired data and submit it!')],
                                [sg.Text('GridGuru is not affiliated with Formula 1 or the FIA.')]]
                about_win = sg.Window('About Gr1dGuru', about_layout, size=(500,100), modal=True, keep_on_top=True)
                event = about_win.read()
                if event == sg.WIN_CLOSED:
                    about_win.close()


            # Load GPs
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

            # Load Drivers
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
                ## SesVars og LapVars kan kun hentes ved å skape en instance av Lists klassen og loade inn listen ved hjelp av lists istedenfor Lists.
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


        ##
        if event in (None, 'Exit'):
            break

        ##
        elif event == 'About':
            ButtonFunc.About()

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

        ## Load Driver VARSs        
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


## Main funksjon
if __name__ == '__main__':
    sg.theme('DarkGrey14')
    main()
else:
    sg.theme('DarkGrey14')
    main()

