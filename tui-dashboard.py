import curses
import psutil
import time
import requests
import yfinance as yf
import os
import configparser
import subprocess
from datetime import datetime
import socket
import threading
import sys
import argparse

class DashboardApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.monocle_mode = False
        self.active_window = 0
        self.windows = [self.system_info, self.weather_info, self.tasks_info, self.stocks_info]
        self.window_titles = ["System Info", "Weather Info", "Tasks", "Stocks"]
        self.setup_curses()
        self.config_file = os.path.expanduser('~/.config/dailyapp/conf.conf')
        self.ensure_config_file()
        self.is_raspberry_pi = self.check_if_raspberry_pi()

        # Start auto-refresh threads
        threading.Thread(target=self.auto_refresh_weather, daemon=True).start()
        threading.Thread(target=self.auto_refresh_stocks, daemon=True).start()

        # Initialize dynamic data
        self.weather_data = self.weather_info()
        self.stock_data = self.stocks_info()
        self.tasks_data = self.tasks_info()
        self.last_tasks_update = 0  # For updating tasks every 5 minutes

        # Get global IP address once at the beginning
        self.global_ip = self.get_global_ip()

    def setup_curses(self):
        curses.curs_set(0)  # Hide the cursor
        self.stdscr.nodelay(1)
        self.stdscr.timeout(100)
        curses.start_color()
        curses.use_default_colors()

        # Define color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)   # Green text
        curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Yellow text
        curses.init_pair(3, curses.COLOR_RED, -1)     # Red text
        curses.init_pair(4, curses.COLOR_WHITE, -1)   # Default text color

    def ensure_config_file(self):
        """Ensure the config directory and file for stock symbols exists."""
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        if not os.path.exists(self.config_file):
            # Create the config file with default content
            with open(self.config_file, 'w') as f:
                f.write("[settings]\nstocks=\n")

    def get_config_stocks(self):
        """Read stock symbols from the config file."""
        config = configparser.ConfigParser()
        config.read(self.config_file)
        try:
            stock_list = config.get("settings", "stocks").replace("{", "").replace("}", "")
            return [symbol.strip() for symbol in stock_list.split(",")] if stock_list else []
        except (configparser.NoSectionError, configparser.NoOptionError):
            return []

    def check_if_raspberry_pi(self):
        """Check if the system is a Raspberry Pi."""
        try:
            with open('/proc/cpuinfo') as f:
                cpuinfo = f.read()
                return 'BCM' in cpuinfo or 'Raspberry Pi' in cpuinfo
        except:
            return False

    def get_ip_location(self):
        """Get user location based on their IP address."""
        try:
            ip_data = requests.get("http://ipinfo.io").json()
            city = ip_data.get('city', 'Unknown')
            country = ip_data.get('country', 'Unknown')
            return f"{city}, {country}"
        except:
            return "Location Unavailable"

    def check_battery_monitor_service(self):
        """Check if battery_monitor.service is enabled and running."""
        try:
            output = subprocess.check_output(
                ["systemctl", "--user", "is-enabled", "battery_monitor.service"]
            ).decode().strip()
            is_enabled = "enabled" if output == "enabled" else "disabled"

            output = subprocess.check_output(
                ["systemctl", "--user", "is-active", "battery_monitor.service"]
            ).decode().strip()
            is_active = "active/running" if output == "active" else "inactive"

            return f"Battery Monitor: {is_enabled}, {is_active}"
        except subprocess.CalledProcessError:
            return "Battery Monitor: Not found"

    def get_local_ip(self):
        """Get the local IP address of the machine."""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return "Local IP Unavailable"

    def get_global_ip(self):
        """Get the global IP address of the machine."""
        try:
            # Simulate 'curl https://kleinpanic/ip' using requests
            response = requests.get('https://kleinpanic/ip', timeout=5)
            if response.status_code == 200:
                return response.text.strip()
            else:
                return "Global IP Unavailable"
        except:
            # Alternative method using ipify.org if the above fails
            try:
                response = requests.get('https://api.ipify.org', timeout=5)
                if response.status_code == 200:
                    return response.text.strip()
                else:
                    return "Global IP Unavailable"
            except:
                return "Global IP Unavailable"

    def system_info(self):
        cpu_usage = psutil.cpu_percent(interval=None)
        avg_load = os.getloadavg()
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage('/')
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_string = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))

        # Network Info
        net_io = psutil.net_io_counters()
        local_ip = self.get_local_ip()
        num_processes = len(psutil.pids())
        cpu_freq = psutil.cpu_freq()
        num_cpus = psutil.cpu_count(logical=True)

        # Initialize an empty list to hold the lines
        sys_info_lines = []

        # Start constructing the system info string
        sys_info_lines.append("╔════════════════════════════════════════════════╗")
        sys_info_lines.append("║                  System Info                   ║")
        sys_info_lines.append("╠════════════════════════════════════════════════╣")
        sys_info_lines.append("║                                                ║")

        # CPU Usage with color
        cpu_color = self.get_usage_color(cpu_usage)
        sys_info_lines.append(f"║ CPU Usage: {cpu_usage}%                        ")

        # CPU Frequency and cores
        sys_info_lines.append(f"║ CPU Frequency: {cpu_freq.current:.2f} MHz      ")
        sys_info_lines.append(f"║ CPUs: {num_cpus} cores                         ")
        sys_info_lines.append(f"║ Avg Load: {avg_load[0]:.2f}, {avg_load[1]:.2f}, {avg_load[2]:.2f}")

        # Memory Usage with color
        mem_color = self.get_usage_color(memory.percent)
        sys_info_lines.append(f"║ Memory Usage: {memory.percent}%                ")

        sys_info_lines.append(f"║ Swap Usage: {swap.percent}%                    ")
        sys_info_lines.append(f"║ Disk Usage: {disk.percent}%                    ")

        if self.is_raspberry_pi:
            # Get temperature (Raspberry Pi-specific)
            try:
                temp_output = subprocess.check_output(
                    ["vcgencmd", "measure_temp"]
                ).decode()
                temperature = temp_output.replace("temp=", "").replace("'C\n", "°C")
            except:
                temperature = "N/A"
            sys_info_lines.append(f"║ CPU Temp: {temperature}                        ")
        else:
            # Battery info with color
            try:
                battery = psutil.sensors_battery()
                battery_percent = int(battery.percent)
                battery_discharge = f"{battery_percent}% {'Charging' if battery.power_plugged else 'Discharging'}"
                battery_color = self.get_battery_color(battery_percent)
            except:
                battery_discharge = "N/A"
                battery_color = curses.color_pair(4)  # Default color

            battery_monitor_status = self.check_battery_monitor_service()
            sys_info_lines.append(f"║ Battery: {battery_discharge}                   ")
            sys_info_lines.append(f"║ {battery_monitor_status}             ")

        sys_info_lines.append(f"║ Processes: {num_processes}                     ")
        sys_info_lines.append(f"║ Uptime: {uptime_string}                        ")
        sys_info_lines.append(f"║ Local IP: {local_ip}                           ")
        sys_info_lines.append(f"║ Global IP: {self.global_ip}                    ")
        sys_info_lines.append(f"║ Net In/Out: {net_io.bytes_recv / (1024 * 1024):.2f}MB / {net_io.bytes_sent / (1024 * 1024):.2f}MB ")
        sys_info_lines.append("╚════════════════════════════════════════════════╝")

        return sys_info_lines, cpu_color, mem_color, battery_color if not self.is_raspberry_pi else curses.color_pair(4)

    def get_usage_color(self, usage):
        """Return color pair based on usage percentage."""
        if usage > 75:
            return curses.color_pair(3)  # Red
        elif usage > 50:
            return curses.color_pair(2)  # Yellow
        else:
            return curses.color_pair(1)  # Green

    def get_battery_color(self, battery_percent):
        """Return color pair based on battery percentage."""
        if battery_percent < 15:
            return curses.color_pair(3)  # Red
        elif battery_percent < 25:
            return curses.color_pair(2)  # Yellow
        else:
            return curses.color_pair(1)  # Green

    def weather_info(self):
        def fetch_from_wttr():
            """Fetch weather from wttr.in."""
            try:
                location = self.get_ip_location()  # Get the location based on IP

                res = requests.get('http://wttr.in/?format=%C+%t+%w+%h+%S+%s')
                if res.status_code == 200:
                    weather_data = res.text.strip().split()
                    if len(weather_data) >= 6:
                        condition = weather_data[0]
                        temp = weather_data[1]
                        wind = weather_data[2]
                        humidity = weather_data[3]
                        sunrise = weather_data[4]
                        sunset = weather_data[5]

                        # Enhanced clothing advice based on weather conditions
                        temp_val = int(temp[:-1]) if '°C' in temp else int((float(temp[:-1]) - 32) * 5/9)
                        humidity_val = int(humidity.replace('%', '')) if humidity != 'N/A' else 50
                        wind_speed = int(wind[:-3]) if 'km/h' in wind else 0  # Get wind speed if available

                        # Robust clothing suggestion logic
                        clothing = self.get_clothing_suggestion(condition, temp_val, humidity_val, wind_speed)

                        date_str = datetime.now().strftime('%m/%d/%Y')
                        time_str = datetime.now().strftime('%H:%M')

                        return f"""
╔════════════════════════════════════════════════╗
║                Weather Information             ║
╠════════════════════════════════════════════════╣
║                                                ║
║ Location: {location}                           
║ Date: {date_str} - {time_str}                  
║ Condition: {condition}                         
║ Temperature: {temp}                            
║ Wind: {wind}                                   
║ Humidity: {humidity}                           
║ Sunrise: {sunrise}                             
║ Sunset: {sunset}                               
║                                                ║
║ ────────────────────────────────────────────── ║
║ Recommended Clothing:                          ║
║ {clothing}                                     
╚════════════════════════════════════════════════╝
"""
                    else:
                        return None
                else:
                    return None
            except:
                return None

        def fetch_from_open_meteo():
            """Fetch weather from Open-Meteo."""
            try:
                # Get latitude and longitude from the IP
                lat, lon = self.get_lat_lon_from_ip()
                location = self.get_ip_location()  # Get the location using IP, not from the API

                res = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true')
                if res.status_code == 200:
                    data = res.json()['current_weather']
                    temp_celsius = data['temperature']
                    temp_fahrenheit = (temp_celsius * 9/5) + 32  # Convert to Fahrenheit
                    wind_speed = data['windspeed']
                    condition_code = data.get('weathercode', 0)

                    # Map weather codes to conditions
                    condition = self.get_condition_from_code(condition_code)

                    # Humidity is not provided by Open-Meteo free tier, so we'll set it as "N/A"
                    humidity = "N/A"

                    # Robust clothing suggestion logic
                    temp_val = temp_celsius
                    humidity_val = 50  # Default value
                    wind_speed_val = wind_speed
                    clothing = self.get_clothing_suggestion(condition, temp_val, humidity_val, wind_speed_val)

                    date_str = datetime.now().strftime('%m/%d/%Y')
                    time_str = datetime.now().strftime('%H:%M')

                    return f"""
╔════════════════════════════════════════════════╗
║                Weather Information             ║
╠════════════════════════════════════════════════╣
║                                                ║
║ Location:       {location}                     
║ Date:           {date_str} - {time_str}        
║ Condition:      {condition}                    
║ Temperature:    {temp_fahrenheit:.1f}°F ({temp_celsius:.1f}°C) 
║ Wind:           {wind_speed} km/h              
║ Humidity:       {humidity}                     
║                                                ║
║ ────────────────────────────────────────────── ║
║ Recommended Clothing:                          ║
║ {clothing}                                     
╚════════════════════════════════════════════════╝
"""
                else:
                    return None
            except:
                return None

        # Try fetching weather data from wttr.in first
        weather_data = fetch_from_wttr()

        if weather_data is None:
            # If wttr.in fails, try fetching from Open-Meteo
            weather_data = fetch_from_open_meteo()

        if weather_data is None:
            # If both APIs fail, return an error message
            return "Weather data unavailable from both sources."

        return weather_data

    def get_lat_lon_from_ip(self):
        """Get latitude and longitude based on IP address."""
        try:
            ip_data = requests.get("http://ipinfo.io").json()
            loc = ip_data.get('loc', '0,0').split(',')
            return loc[0], loc[1]
        except:
            return "0", "0"  # Default to 0,0 if location unavailable

    def get_clothing_suggestion(self, condition, temp_val, humidity_val, wind_speed):
        """Provide clothing suggestions based on weather conditions."""
        suggestion = ""

        # Weather condition-based suggestions
        if "rain" in condition.lower() or "drizzle" in condition.lower():
            suggestion += "Carry an umbrella or wear a raincoat. "
        elif "snow" in condition.lower():
            suggestion += "Wear heavy winter gear and snow boots. "
        elif "storm" in condition.lower() or "thunderstorm" in condition.lower():
            suggestion += "Stay indoors if possible due to storms. "

        # Temperature-based suggestions (in Celsius)
        if temp_val < 0:
            suggestion += "Extremely cold! Wear thermal layers and heavy coat."
        elif 0 <= temp_val < 10:
            suggestion += "Very cold! Wear heavy winter clothing."
        elif 10 <= temp_val < 15:
            suggestion += "Cold! Wear a warm jacket and layers."
        elif 15 <= temp_val < 20:
            suggestion += "Cool weather. A light jacket is recommended."
        elif 20 <= temp_val < 25:
            suggestion += "Mild temperature. A sweater or long sleeves."
        elif 25 <= temp_val < 30:
            suggestion += "Warm! Light clothing recommended."
        elif temp_val >= 30:
            suggestion += "Hot! Wear shorts and stay hydrated."

        # Wind-based suggestions
        if wind_speed > 20:
            suggestion += " It's windy; consider a windbreaker."

        # Humidity-based suggestions
        if humidity_val > 80:
            suggestion += " High humidity; dress comfortably."

        return suggestion.strip()

    def get_condition_from_code(self, code):
        """Map weather codes to conditions for Open-Meteo."""
        code_map = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }
        return code_map.get(code, "Unknown")

    def tasks_info(self):
        tasks_file = os.path.expanduser('~/.local/share/todo/tasks.txt')
        if not os.path.exists(tasks_file):
            return "No tasks available."

        tasks = []
        with open(tasks_file, 'r') as f:
            for line in f:
                task_info = line.strip().split("\t")
                if len(task_info) == 7:
                    task_num, name, category, priority, complete, due_date, recurrence = task_info
                    complete_str = "[X]" if complete == "1" else "[ ]"
                    tasks.append(f"║ {task_num}. {name} ({category}) - Priority: {priority} {complete_str}")
                    tasks.append(f"║ Due: {due_date} | Recurs: {recurrence}")
                else:
                    tasks.append(f"║ {line.strip()}")  # In case of incorrect format

        tasks_content = "\n".join(tasks) if tasks else "No tasks available."

        return f"""
╔════════════════════════════════════════════════╗
║                   Tasks List                   ║
╠════════════════════════════════════════════════╣
{tasks_content}
╚════════════════════════════════════════════════╝
"""

    def stocks_info(self):
        stock_symbols = self.get_config_stocks()
        if not stock_symbols or stock_symbols == ['']:
            return "No stocks configured in ~/.config/dailyapp/conf.conf"

        stock_info = []
        for symbol in stock_symbols:
            stock = yf.Ticker(symbol.strip())
            try:
                price = stock.history(period="1d")['Close'].iloc[-1]
                stock_info.append(f"║ {symbol.strip()}: ${price:.2f}")
            except (KeyError, IndexError):
                stock_info.append(f"║ {symbol.strip()}: Data not available")

        stock_content = "\n".join(stock_info) if stock_info else "No stock data available."

        return f"""
╔════════════════════════════════════════════════╗
║                  Stocks Info                   ║
╠════════════════════════════════════════════════╣
{stock_content}
╚════════════════════════════════════════════════╝
"""

    def auto_refresh_weather(self):
        """Auto-refresh weather every 30 minutes."""
        while True:
            self.weather_data = self.weather_info()
            time.sleep(1800)  # Refresh every 30 minutes

    def auto_refresh_stocks(self):
        """Auto-refresh stocks every 5 minutes."""
        while True:
            self.stock_data = self.stocks_info()
            time.sleep(300)  # Refresh every 5 minutes

    def draw_tiling(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        mid_y = height // 2
        mid_x = width // 2

        # Define windows (quadrants), ensuring they fit within the screen dimensions
        system_win_height = max(3, mid_y - 1)
        system_win_width = max(10, mid_x - 1)
        weather_win_height = max(3, mid_y - 1)
        weather_win_width = max(10, width - mid_x - 1)
        tasks_win_height = max(3, height - mid_y - 1)
        tasks_win_width = max(10, mid_x - 1)
        stocks_win_height = max(3, height - mid_y - 1)
        stocks_win_width = max(10, width - mid_x - 1)

        # Adjust subwindows
        system_win = self.stdscr.subwin(system_win_height, system_win_width, 0, 0)
        weather_win = self.stdscr.subwin(weather_win_height, weather_win_width, 0, mid_x + 1)
        tasks_win = self.stdscr.subwin(tasks_win_height, tasks_win_width, mid_y + 1, 0)
        stocks_win = self.stdscr.subwin(stocks_win_height, stocks_win_width, mid_y + 1, mid_x + 1)

        # Draw lines separating the windows
        self.stdscr.vline(0, mid_x, curses.ACS_VLINE, height)
        self.stdscr.hline(mid_y, 0, curses.ACS_HLINE, width)

        # Draw system info
        system_win.clear()
        system_win.box()
        system_win.addstr(1, 2, "System Info:")
        sys_info_lines, cpu_color, mem_color, battery_color = self.system_info()
        self.display_system_info(system_win, sys_info_lines, cpu_color, mem_color, battery_color)

        # Draw weather info
        weather_win.clear()
        weather_win.box()
        weather_win.addstr(1, 2, "Weather Info:")
        weather_display = self.weather_data.replace('CURRENT_TIME', datetime.now().strftime('%H:%M'))
        self.display_in_window(weather_win, 3, 2, weather_display)

        # Draw tasks info
        tasks_win.clear()
        tasks_win.box()
        tasks_win.addstr(1, 2, "Tasks:")
        self.display_in_window(tasks_win, 3, 2, self.tasks_data)

        # Draw stocks info
        stocks_win.clear()
        stocks_win.box()
        stocks_win.addstr(1, 2, "Stocks:")
        self.display_in_window(stocks_win, 3, 2, self.stock_data)

        # Refresh all windows
        system_win.refresh()
        weather_win.refresh()
        tasks_win.refresh()
        stocks_win.refresh()

    def draw_monocle(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Draw the active window in monocle mode
        window_func = self.windows[self.active_window]
        title = self.window_titles[self.active_window]

        # Center the title
        self.stdscr.addstr(0, max(0, (width // 2) - (len(title) // 2)), f"{title}:", curses.A_BOLD)

        if self.active_window == 0:
            # System Info
            sys_info_lines, cpu_color, mem_color, battery_color = self.system_info()
            self.display_system_info(self.stdscr, sys_info_lines, cpu_color, mem_color, battery_color, start_y=2, start_x=0)
        elif self.active_window == 1:
            # Weather window
            weather_display = self.weather_data.replace('CURRENT_TIME', datetime.now().strftime('%H:%M'))
            self.display_in_window(self.stdscr, 2, 0, weather_display)
        elif self.active_window == 2:
            # Tasks window
            self.display_in_window(self.stdscr, 2, 0, self.tasks_data)
        elif self.active_window == 3:
            # Stocks window
            self.display_in_window(self.stdscr, 2, 0, self.stock_data)
        else:
            content = window_func()
            self.display_in_window(self.stdscr, 2, 0, content)

        self.stdscr.refresh()

    def display_system_info(self, window, lines, cpu_color, mem_color, battery_color, start_y=3, start_x=2):
        """Display system info with color coding for CPU, Memory, and Battery."""
        max_y, max_x = window.getmaxyx()
        for i, line in enumerate(lines):
            if start_y + i < max_y - 1:
                if "CPU Usage:" in line:
                    window.addstr(start_y + i, start_x, line, cpu_color)
                elif "Memory Usage:" in line:
                    window.addstr(start_y + i, start_x, line, mem_color)
                elif "Battery:" in line:
                    window.addstr(start_y + i, start_x, line, battery_color)
                else:
                    window.addnstr(start_y + i, start_x, line, max_x - start_x - 1)

    def display_in_window(self, window, start_y, start_x, text):
        """Helper function to handle multiline text and text wrapping."""
        max_y, max_x = window.getmaxyx()
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if start_y + i < max_y - 1:
                try:
                    window.addnstr(start_y + i, start_x, line, max_x - start_x - 1)
                except curses.error:
                    pass  # Handle cases where the line doesn't fit

    EXIT_ASCII_ART = """
  ______      _ _   _               _____            _     _                         _ _ 
 |  ____|    (_) | (_)             |  __ \          | |   | |                       | | |
 | |__  __  ___| |_ _ _ __   __ _  | |  | | __ _ ___| |__ | |__   ___   __ _ _ __ __| | |
 |  __| \ \/ / | __| | '_ \ / _` | | |  | |/ _` / __| '_ \| '_ \ / _ \ / _` | '__/ _` | |
 | |____ >  <| | |_| | | | | (_| | | |__| | (_| \__ \ | | | |_) | (_) | (_| | | | (_| |_|
 |______/_/\_\_|\__|_|_| |_|\__, | |_____/ \__,_|___/_| |_|_.__/ \___/ \__,_|_|  \__,_(_)
                             __/ |                                                       
   _____                 _  |___/                     __                                 
  / ____|               | | |  _ \                _   \ \                                
 | |  __  ___   ___   __| | | |_) |_   _  ___    (_)   | |                               
 | | |_ |/ _ \ / _ \ / _` | |  _ <| | | |/ _ \         | |                               
 | |__| | (_) | (_) | (_| | | |_) | |_| |  __/    _    | |                               
  \_____|\___/ \___/ \__,_| |____/ \__, |\___|   (_)   | |                               
                                    __/ |             /_/                                

"""

    def display_goodbye_message(self, message="Exiting dashboard. Goodbye!"):
        """Display a centered ASCII art goodbye message and exit the program."""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        # Split the ASCII art into lines and remove any leading/trailing whitespace
        lines = self.EXIT_ASCII_ART.strip('\n').split('\n')
        total_lines = len(lines)
        
        # Calculate the starting y position to center the ASCII art vertically
        start_y = max(0, (height // 2) - (total_lines // 2))
        
        for i, line in enumerate(lines):
            # Calculate the starting x position to center each line horizontally
            start_x = max(0, (width // 2) - (len(line) // 2))
            try:
                self.stdscr.addstr(start_y + i, start_x, line)
            except curses.error:
                # If the line doesn't fit, skip it to prevent crashing
                pass
        
        self.stdscr.refresh()
        time.sleep(2)  # Increase pause duration if desired
        sys.exit(0)    # Exit the program cleanly

    def main_loop(self):
        try:
            # Main loop to keep the screen updated
            while True:
                key = self.stdscr.getch()

                if key == ord('q') or key == 27:  # Quit on 'q' or 'Esc'
                    self.display_goodbye_message()
                elif key == ord('m'):  # Monocle mode
                    self.monocle_mode = True
                    self.active_window = 0  # Start with the first window in monocle mode

                elif key == ord('t'):  # Tiling mode
                    self.monocle_mode = False

                elif self.monocle_mode and key == ord('j'):  # Next window in monocle mode
                    if self.active_window < len(self.windows) - 1:
                        self.active_window += 1

                elif self.monocle_mode and key == ord('k'):  # Previous window in monocle mode
                    if self.active_window > 0:
                        self.active_window -= 1

                # Update tasks every 5 minutes
                if time.time() - self.last_tasks_update >= 300:
                    self.tasks_data = self.tasks_info()
                    self.last_tasks_update = time.time()

                # Redraw based on current mode
                if self.monocle_mode:
                    self.draw_monocle()
                else:
                    self.draw_tiling()

                if curses.is_term_resized(*self.stdscr.getmaxyx()):
                    # Handle resizing gracefully
                    self.stdscr.clear()
                    if self.monocle_mode:
                        self.draw_monocle()
                    else:
                        self.draw_tiling()
                time.sleep(0.75)  # Sleep for 750ms to prevent high CPU usage
        except KeyboardInterrupt:
            self.display_goodbye_message()
def main(stdscr):
    app = DashboardApp(stdscr)
    app.main_loop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DashboardApp - Terminal-based Dashboard")
    parser.add_argument('--version', action='version', version='DashboardApp 0.0.1')
    parser.parse_args()  # Handle '--version' and exit if specified
    curses.wrapper(main)
