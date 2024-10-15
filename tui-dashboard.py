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

    def setup_curses(self):
        curses.curs_set(0)  # Hide the cursor
        self.stdscr.nodelay(1)
        self.stdscr.timeout(100)

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
        stock_list = config.get("settings", "stocks").replace("{", "").replace("}", "")
        return stock_list.split(",") if stock_list else []

    def check_if_raspberry_pi(self):
        """Check if the system is a Raspberry Pi."""
        try:
            with open('/proc/cpuinfo') as f:
                return any("Raspberry Pi" in line for line in f)
        except:
            return False

    def get_ip_location(self):
        """Get user location based on their IP address."""
        try:
            ip_data = requests.get("http://ipinfo.io").json()
            return ip_data.get('city', 'Unknown') + ", " + ip_data.get('country', 'Unknown')
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

    def system_info(self):
        cpu_usage = psutil.cpu_percent()
        avg_load = os.getloadavg()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_string = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))

        # Network Info
        net_io = psutil.net_io_counters()

        # Raspberry Pi-specific info
        if self.is_raspberry_pi:
            # Get temperature (Raspberry Pi-specific)
            try:
                temp_output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
                temperature = temp_output.replace("temp=", "").replace("'C\n", "°C")
            except:
                temperature = "N/A"
            
            return f"""
╔════════════════════════════════════════════════╗
║                  System Info                   ║
╠════════════════════════════════════════════════╣
║                                                ║
║ CPU: {cpu_usage}%                              
║ Avg Load: {avg_load[0]:.2f}, {avg_load[1]:.2f}, {avg_load[2]:.2f}
║ Memory: {memory.percent}%                   
║ Disk Usage: {disk.percent}%                  
║ CPU Temp: {temperature}                     
║ Uptime: {uptime_string}                     
║ Net In/Out: {net_io.bytes_recv / (1024 * 1024):.2f}MB / {net_io.bytes_sent / (1024 * 1024):.2f}MB
╚════════════════════════════════════════════════╝
"""
        
        # Non-Raspberry Pi-specific info (Battery, etc.)
        else:
            try:
                battery = psutil.sensors_battery()
                battery_discharge = f"{int(battery.percent)}% {'Charging' if battery.power_plugged else 'Discharging'}"
            except:
                battery_discharge = "N/A"

            battery_monitor_status = self.check_battery_monitor_service()

            return f"""
╔════════════════════════════════════════════════╗
║                  System Info                   ║
╠════════════════════════════════════════════════╣
║                                                ║
║ CPU: {cpu_usage}%                              
║ Avg Load: {avg_load[0]:.2f}, {avg_load[1]:.2f}, {avg_load[2]:.2f}
║ Memory: {memory.percent}%                   
║ Disk Usage: {disk.percent}%                  
║ Battery: {battery_discharge}              
║ {battery_monitor_status}            
║ Uptime: {uptime_string}                     
║ Net In/Out: {net_io.bytes_recv / (1024 * 1024):.2f}MB / {net_io.bytes_sent / (1024 * 1024):.2f}MB
╚════════════════════════════════════════════════╝
"""

    def weather_info(self):
        def fetch_from_wttr():
            """Fetch weather from wttr.in."""
            try:
                location = self.get_ip_location()  # Get the location based on IP

                res = requests.get('http://wttr.in/?format=%C+%t+%w+%h+%S+%s+%D')
                if res.status_code == 200:
                    weather_data = res.text.strip().split()
                    condition = weather_data[0]
                    temp = weather_data[1]
                    wind = weather_data[2]
                    humidity = weather_data[3]
                    sunrise = weather_data[4]
                    sunset = weather_data[5]
                    date = weather_data[6]

                    # Convert date to 24-hour format with full date (e.g., YYYY-MM-DD HH:MM)
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')

                    # Enhanced clothing advice based on weather conditions
                    temp_val = int(temp[:-1]) if 'C' in temp else 25  # Default to 25C if unknown
                    humidity_val = int(humidity.replace('%', ''))
                    wind_speed = int(wind[:-3]) if 'km/h' in wind else 0  # Get wind speed if available

                    if "rain" in condition.lower():
                        clothing = "Raincoat and waterproof shoes!"
                    elif "snow" in condition.lower():
                        clothing = "Heavy winter gear and snow boots!"
                    elif temp_val < 5:
                        clothing = "Heavy winter gear!"
                    elif 5 <= temp_val < 15:
                        clothing = "Warm jacket recommended."
                    elif 15 <= temp_val < 22:
                        clothing = "Light jacket or sweater."
                    elif 22 <= temp_val < 30 and wind_speed < 20 and humidity_val < 70:
                        clothing = "T-shirt and shorts!"
                    elif temp_val >= 30 and wind_speed < 20:
                        clothing = "Stay cool with very light clothing."
                    else:
                        clothing = "Light clothing suitable for warm weather."

                    return f"""
╔════════════════════════════════════════════════╗
║                Weather Information             ║
╠════════════════════════════════════════════════╣
║                                                ║
║ Location: {location}                           
║ Date: {date} - {datetime.now().strftime('%H:%M')}  
║ Condition: {condition}                         
║ Temp: {temp}                                   
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
                    
                    # Humidity is not provided by Open-Meteo free tier, so we'll set it as "N/A"
                    humidity = "N/A"

                    # Convert date to 24-hour format with full date (e.g., YYYY-MM-DD HH:MM)
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')

                    # Simple clothing advice based on temperature
                    temp_val = temp_celsius
                    wind_speed_val = wind_speed

                    if temp_val < 5:
                        clothing = "Heavy winter gear!"
                    elif 5 <= temp_val < 15:
                        clothing = "Warm jacket recommended."
                    elif 15 <= temp_val < 22:
                        clothing = "Light jacket or sweater."
                    elif 22 <= temp_val < 30 and wind_speed_val < 20:
                        clothing = "T-shirt and shorts!"
                    elif temp_val >= 30 and wind_speed_val < 20:
                        clothing = "Stay cool with very light clothing."
                    else:
                        clothing = "Light clothing suitable for warm weather."

                    return f"""
╔════════════════════════════════════════════════╗
║                Weather Information             ║
╠════════════════════════════════════════════════╣
║                                                ║
║ Location:       {location}                     
║ Date:           {current_time}                 
║ Temperature:    {temp_fahrenheit:.2f}°F ({temp_celsius:.2f}°C) 
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
                stock_info.append(f"║ {symbol}: ${price:.2f}")
            except (KeyError, IndexError):
                stock_info.append(f"║ {symbol}: Data not available")

        stock_content = "\n".join(stock_info) if stock_info else "No stock data available."
    
        return f"""
╔════════════════════════════════════════════════╗
║                  Stocks Info                   ║
╠════════════════════════════════════════════════╣
{stock_content}
╚════════════════════════════════════════════════╝
"""

    def auto_refresh_weather(self):
        """Auto-refresh weather every 15 minutes."""
        while True:
            self.weather_data = self.weather_info()
            time.sleep(900)  # Refresh every 15 minutes

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
        self.display_in_window(system_win, 3, 2, self.system_info())

        # Draw weather info
        weather_win.clear()
        weather_win.box()
        weather_win.addstr(1, 2, "Weather Info:")
        self.display_in_window(weather_win, 3, 2, self.weather_data)

        # Draw tasks info
        tasks_win.clear()
        tasks_win.box()
        tasks_win.addstr(1, 2, "Tasks:")
        self.display_in_window(tasks_win, 3, 2, self.tasks_info())

        # Draw stocks info
        stocks_win.clear()
        stocks_win.box()
        stocks_win.addstr(1, 2, "Stocks:")
        self.display_in_window(stocks_win, 3, 2, self.stocks_info())

        # Refresh all windows
        system_win.refresh()
        weather_win.refresh()
        tasks_win.refresh()
        stocks_win.refresh()

    def draw_monocle(self):
        self.stdscr.clear()
        width = self.stdscr.getmaxyx()[1]  # Only get the width, as height is not needed

        # Draw the active window in monocle mode
        window_func = self.windows[self.active_window]
        title = self.window_titles[self.active_window]

        # Center the title
        self.stdscr.addstr(0, (width // 2) - (len(title) // 2), f"{title}:", curses.A_BOLD)
        self.display_in_window(self.stdscr, 2, 0, window_func())

        self.stdscr.refresh()

    def display_in_window(self, window, start_y, start_x, text):
        """Helper function to handle multiline text and text wrapping."""
        max_y, max_x = window.getmaxyx()
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if start_y + i < max_y - 1:
                window.addnstr(start_y + i, start_x, line, max_x - start_x - 1)

    def main_loop(self):
        # Main loop to keep the screen updated
        while True:
            key = self.stdscr.getch()

            if key == ord('q') or key == 27:  # Quit on 'q' or 'Esc'
                break

            elif key == ord('m'):  # Monocle mode
                self.monocle_mode = True
                self.active_window = 0  # Start with the first window in monocle mode
                self.draw_monocle()

            elif key == ord('t'):  # Tiling mode
                self.monocle_mode = False
                self.draw_tiling()

            elif self.monocle_mode and key == ord('j'):  # Next window in monocle mode
                if self.active_window < 3:
                    self.active_window += 1
                    self.draw_monocle()

            elif self.monocle_mode and key == ord('k'):  # Previous window in monocle mode
                if self.active_window > 0:
                    self.active_window -= 1
                    self.draw_monocle()

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

            time.sleep(0.05)  # Sleep to prevent high CPU usage

def main(stdscr):
    app = DashboardApp(stdscr)
    app.main_loop()

if __name__ == "__main__":
    curses.wrapper(main)
