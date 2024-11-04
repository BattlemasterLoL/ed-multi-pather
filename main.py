import requests
import json
import math
from nicegui import ui, app
import asyncio
from datetime import datetime
import itertools
import pandas as pd
import csv
from io import StringIO
import os


class EDSMCalculator:
    def __init__(self):
        self.systems = []
        self.route_log = []
        self.jump_range = 0
        self.system_names = self.load_system_names()

    async def get_system_coordinates(self, system_name):
        """Fetch coordinates for a given star system from the EDSM API."""
        url = "https://www.edsm.net/api-v1/system"
        params = {
            "systemName": system_name.strip(),
            "showCoordinates": 1
        }

        try:
            # Make the API request asynchronously using asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.get(url, params=params))
            response.raise_for_status()

            data = response.json()

            if not data:
                return None

            if "coords" not in data:
                return None

            return {
                "name": data["name"],
                "coordinates": {
                    "x": data["coords"]["x"],
                    "y": data["coords"]["y"],
                    "z": data["coords"]["z"]
                }
            }

        except Exception as e:
            return None

    def calculate_distance(self, coords1, coords2):
        """Calculate the Euclidean distance between two sets of coordinates."""
        return math.sqrt(
            (coords2["x"] - coords1["x"]) ** 2 +
            (coords2["y"] - coords1["y"]) ** 2 +
            (coords2["z"] - coords1["z"]) ** 2
        )

    def calculate_route_distances(self):
        """Calculate distances between consecutive systems in the route."""
        distances = []
        total_distance = 0

        for i in range(len(self.systems) - 1):
            system1 = self.systems[i]
            system2 = self.systems[i + 1]

            distance = self.calculate_distance(
                system1["coordinates"], system2["coordinates"])
            total_distance += distance
            distances.append((system1["name"], system2["name"], distance))

        return distances, total_distance

    def format_system_row(self, system):
        """Format system data for table display."""
        return {
            'name': system['name'],
            'x': f"{system['coordinates']['x']:.2f}",
            'y': f"{system['coordinates']['y']:.2f}",
            'z': f"{system['coordinates']['z']:.2f}"
        }

    def format_route_row(self, route):
        """Format route history data for table display."""
        return {
            'timestamp': route['timestamp'],
            'systems': ' → '.join(route['systems']),
            'distance': f"{route['distance']:.2f}"
        }

    def optimize_route(self):
        """Find the shortest route through all systems."""
        if len(self.systems) < 2:
            return self.systems

        shortest_distance = float('inf')
        shortest_route = None

        for route in itertools.permutations(self.systems[1:]):
            # Always start with the first system
            route = [self.systems[0]] + list(route)
            total_distance = sum(self.calculate_distance(route[i]["coordinates"], route[i+1]["coordinates"])
                                 for i in range(len(route)-1))

            if total_distance < shortest_distance:
                shortest_distance = total_distance
                shortest_route = route

        return shortest_route

    def log_route(self, systems, total_distance):
        """Log the calculated route with timestamp."""
        self.route_log.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'systems': [system['name'] for system in systems],
            'distance': total_distance
        })

    def calculate_jumps(self, distance, jump_range):
        """Calculate estimated number of jumps needed."""
        if jump_range <= 0:
            return 0
        return math.ceil(distance / jump_range)

    def load_system_names(self):
        """Load system names from systems.csv"""
        try:
            df = pd.read_csv('systems.csv', header=None)
            return df[0].tolist()  # Assuming single column of system names
        except Exception as e:
            print(f"Error loading systems.csv: {e}")
            return []

    def export_route_to_csv(self, filename='route_export.csv'):
        """Export the current route to a CSV file on the desktop."""
        if not self.systems:
            return False

        # Get the path to the desktop
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        # Create the full file path
        file_path = os.path.join(desktop_path, filename)

        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['System Name', 'X', 'Y', 'Z'])  # Header
                for system in self.systems:
                    writer.writerow([
                        system['name'],
                        system['coordinates']['x'],
                        system['coordinates']['y'],
                        system['coordinates']['z']
                    ])
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def import_route_from_csv(self, file_content):
        """Import systems from a CSV file."""
        try:
            # Read CSV content
            csv_data = pd.read_csv(file_content)

            # Validate columns
            required_columns = ['System Name', 'X', 'Y', 'Z']
            if not all(col in csv_data.columns for col in required_columns):
                return False, "Invalid CSV format. Required columns: System Name, X, Y, Z"

            # Import systems
            imported_systems = []
            for _, row in csv_data.iterrows():
                system_data = {
                    "name": row['System Name'],
                    "coordinates": {
                        "x": float(row['X']),
                        "y": float(row['Y']),
                        "z": float(row['Z'])
                    }
                }
                imported_systems.append(system_data)

            self.systems.extend(imported_systems)
            return True, f"Successfully imported {len(imported_systems)} systems"

        except Exception as e:
            return False, f"Error importing CSV: {str(e)}"


# Initialize the calculator
calculator = EDSMCalculator()

# Create the UI


@ui.page('/')
def home():
    # Main container with responsive grid
    with ui.element('div').classes('w-full p-4 mx-auto max-w-7xl'):
        # Grid container
        with ui.element('div').classes('grid grid-cols-1 md:grid-cols-2 gap-4'):
            # Input Card
            with ui.card().classes('w-full'):
                ui.label('EDSM System Distance Calculator').classes(
                    'text-h4 text-center')

                # Jump Range input
                with ui.row().classes('w-full items-center'):
                    jump_range_input = ui.number(
                        label='Enter Ship Jump Range (Ly)',
                        min=0,
                        step=0.1,
                        format='%.1f'
                    ).classes('flex-grow')

                # System input area with autocomplete and Add System button
                with ui.row().classes('w-full items-center gap-2'):
                    system_input = ui.select(
                        options=calculator.system_names,
                        with_input=True,
                        label='Enter system name',
                        on_change=lambda e: None
                    ).classes('flex-grow')

                    async def add_system():
                        if not system_input.value:
                            return

                        system_data = await calculator.get_system_coordinates(system_input.value)

                        if system_data:
                            calculator.systems.append(system_data)
                            update_systems_table()
                            # Recalculate route if we have enough systems
                            if len(calculator.systems) >= 2:
                                await calculate_route()
                            system_input.value = ''
                        else:
                            ui.notify(f'System "{system_input.value}" not found or has no coordinates', type='negative')

                    ui.button('Add System', on_click=add_system).classes(
                        'bg-blue-500')

                # Systems table
                systems_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': 'System Name', 'field': 'name'},
                        {'name': 'x', 'label': 'X', 'field': 'x'},
                        {'name': 'y', 'label': 'Y', 'field': 'y'},
                        {'name': 'z', 'label': 'Z', 'field': 'z'},
                    ],
                    rows=[calculator.format_system_row(
                        system) for system in calculator.systems]
                ).classes('w-full')

                def update_systems_table():
                    systems_table.rows = [calculator.format_system_row(
                        system) for system in calculator.systems]

                # Action buttons
                with ui.row().classes('w-full justify-center gap-4 mt-4'):
                    async def calculate_route():
                        if len(calculator.systems) < 2:
                            ui.notify(
                                'Please add at least two systems', type='warning')
                            return

                        jump_range = float(jump_range_input.value or 0)
                        calculator.jump_range = jump_range

                        # Calculate entered route
                        distances, total_distance = calculator.calculate_route_distances()
                        calculator.log_route(
                            calculator.systems, total_distance)
                        update_results(distances, total_distance,
                                       results_table, total_label, jump_range)

                        # Calculate optimized route
                        optimized_route = calculator.optimize_route()
                        opt_distances = [(optimized_route[i]['name'], optimized_route[i+1]['name'],
                                          calculator.calculate_distance(optimized_route[i]['coordinates'], optimized_route[i+1]['coordinates']))
                                         for i in range(len(optimized_route)-1)]
                        opt_total_distance = sum(
                            distance for _, _, distance in opt_distances)

                        calculator.log_route(
                            optimized_route, opt_total_distance)
                        update_results(opt_distances, opt_total_distance,
                                       optimized_results_table, optimized_total_label, jump_range)
                        update_route_history()

                    def clear_systems():
                        calculator.systems = []
                        update_systems_table()
                        results_table.rows = []
                        optimized_results_table.rows = []
                        total_label.text = 'Total Distance: 0 Ly'
                        optimized_total_label.text = 'Optimized Total Distance: 0 Ly'
                        jumps_label.text = 'Estimated Jumps: 0'
                        optimized_jumps_label.text = 'Estimated Jumps: 0'

                    ui.button('Calculate Route', on_click=calculate_route).classes(
                        'bg-green-500')
                    ui.button('Clear All', on_click=clear_systems).classes(
                        'bg-red-500')

                    def export_route():
                        if calculator.export_route_to_csv():
                            ui.notify(
                                'Route exported successfully to route_export.csv', type='positive')
                        else:
                            ui.notify(
                                'Failed to export route. Please ensure you have a route calculated.', type='negative')

                    ui.button('Export Route', on_click=export_route).classes(
                        'bg-yellow-500')

                    async def handle_upload(e):
                        try:
                            content = e.content.read().decode()
                            success, message = calculator.import_route_from_csv(
                                StringIO(content))
                            if success:
                                ui.notify(message, type='positive')
                                update_systems_table()
                                # Automatically calculate route after successful import
                                if len(calculator.systems) >= 2:
                                    # Check if jump range is set, if not, prompt or default to last value
                                    if calculator.jump_range > 0:
                                        await calculate_route()
                                    else:
                                        ui.notify(
                                            'Please enter a valid jump range.', type='warning')
                            else:
                                ui.notify(message, type='negative')
                        except Exception as ex:
                            ui.notify(f"Error processing file: {str(ex)}", type='negative')

                    upload = ui.upload(
                        label='Import Route',
                        auto_upload=True,
                        on_upload=handle_upload,
                    ).props('accept=".csv"').style('width: 60%;')

            # Original Route Results card
            with ui.card().classes('w-full'):
                ui.label('Entered Route Details').classes('text-h5')
                results_table = ui.table(
                    columns=[
                        {'name': 'from', 'label': 'From', 'field': 'from'},
                        {'name': 'to', 'label': 'To', 'field': 'to'},
                        {'name': 'distance',
                            'label': 'Distance (Ly)', 'field': 'distance'},
                        {'name': 'jumps', 'label': 'Est. Jumps', 'field': 'jumps'},
                    ],
                    rows=[]
                ).classes('w-full')

                with ui.row().classes('w-full justify-between items-center'):
                    total_label = ui.label(
                        'Total Distance: 0 Ly').classes('text-h6 mt-4')
                    jumps_label = ui.label(
                        'Estimated Jumps: 0').classes('text-h6 mt-4')

            # Optimized Route Results card
            with ui.card().classes('w-full'):
                ui.label('Optimized Route Details').classes('text-h5')
                ui.label('(Shortest path starting from first entered system)').classes(
                    'text-subtitle2')

                optimized_results_table = ui.table(
                    columns=[
                        {'name': 'from', 'label': 'From', 'field': 'from'},
                        {'name': 'to', 'label': 'To', 'field': 'to'},
                        {'name': 'distance',
                            'label': 'Distance (Ly)', 'field': 'distance'},
                        {'name': 'jumps', 'label': 'Est. Jumps', 'field': 'jumps'},
                    ],
                    rows=[]
                ).classes('w-full')

                with ui.row().classes('w-full justify-between items-center'):
                    optimized_total_label = ui.label(
                        'Optimized Total Distance: 0 Ly').classes('text-h6 mt-4')
                    optimized_jumps_label = ui.label(
                        'Estimated Jumps: 0').classes('text-h6 mt-4')

            # Route History card
            with ui.card().classes('w-full'):
                ui.label('Route History').classes('text-h5')
                route_history_table = ui.table(
                    columns=[
                        {'name': 'timestamp', 'label': 'Time', 'field': 'timestamp'},
                        {'name': 'systems', 'label': 'Systems', 'field': 'systems'},
                        {'name': 'distance',
                            'label': 'Total Distance (Ly)', 'field': 'distance'},
                    ],
                    rows=[]
                ).classes('w-full')

    def update_results(distances, total_distance, table, label, jump_range):
        total_jumps = 0
        table.rows = []

        for from_sys, to_sys, distance in distances:
            jumps = calculator.calculate_jumps(
                distance, jump_range) if jump_range > 0 else 0
            total_jumps += jumps
            table.rows.append({
                'from': from_sys,
                'to': to_sys,
                'distance': f"{distance:.2f}",
                'jumps': jumps if jump_range > 0 else 'N/A'
            })

        is_optimized = table == optimized_results_table
        prefix = "Optimized " if is_optimized else ""
        label.text = f'{prefix}Total Distance: {total_distance:.2f} Ly'

        jumps_text = f'Estimated Jumps: {total_jumps}' if jump_range > 0 else 'Estimated Jumps: N/A'
        if is_optimized:
            optimized_jumps_label.text = jumps_text
        else:
            jumps_label.text = jumps_text

    def update_route_history():
        route_history_table.rows = [calculator.format_route_row(
            route) for route in calculator.route_log]


app.on_startup(lambda: print(
    '\033[32mApp available at the following URLs:\033[0m\n' +
    '\n'.join(
        '\033[36m\033[4m' + url + '\033[0m' for url in app.urls
    )
))

ui.run(
    dark=True,
    title='EDSM Distance Calculator'
)
