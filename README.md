# DashboardApp

A comprehensive terminal-based dashboard application for UNIX-like systems that displays real-time system information, weather updates, task management, and stock data in an elegant ASCII-styled interface. Compatible with various Linux distributions and macOS, DashboardApp offers a retro yet functional experience for monitoring essential metrics directly from your terminal.

![DashboardApp Logo](path_to_logo_image) <!-- Optional: Add a logo if available -->

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
  - [Key Bindings](#key-bindings)
- [Configuration](#configuration)
  - [Stocks](#stocks)
  - [Weather](#weather)
  - [Tasks](#tasks)
- [Tasks Integration](#tasks-integration)
- [Tasks File Format](#tasks-file-format)
- [Supported Terminals](#supported-terminals)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## Features
- **Real-Time System Information:** Monitor CPU, memory, swap, disk usage, network I/O, number of processes, uptime, and IP addresses.
- **Current Weather Information:** Fetch and display weather data based on your IP-based location with intelligent clothing recommendations.
- **Task Management:** Integrate with a robust text-based task system to manage your to-dos seamlessly.
- **Stock Tracking:** Monitor stock prices using configurable stock symbols and display them concisely.
- **ASCII-Styled Interface:** Enjoy a visually appealing retro terminal experience with custom-designed ASCII art.
- **Dynamic Layout Modes:**
  - **Tiling Mode:** View multiple information panels simultaneously for a comprehensive overview.
  - **Monocle Mode:** Focus on one information panel at a time with easy navigation between panels.
- **Graceful Exit:** Exit the application with a beautifully rendered ASCII art goodbye message.
- **Version Information:** Easily check the application version using the `--version` argument.

## Prerequisites
Before installing DashboardApp, ensure your system meets the following requirements:

- **Python 3.x** installed
- **Git** installed (optional but recommended for cloning the repository)
- **Supported Terminal** (see [Supported Terminals](#supported-terminals))
- **Todo Task Manager:** DashboardApp integrates with the [todo_task_manager](https://github.com/kleinpanic/todo_task_manager) for task management. Ensure it's installed and configured.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/kleinpanic/tui-dashboard.git
cd tui-dashboard
```

### 2. Run the Install Script
```bash
chmod +x install.sh
./install.sh
```

The install script will:
- Check and install Python 3 if it's missing.
- Set up a Python virtual environment and install necessary dependencies.
- Install utilities and fonts required for optimal ASCII graphics rendering.
- Detect and inform you about your shell and terminal type for compatibility.

### 3. Install Todo Task Manager
DashboardApp relies on the [todo_task_manager](https://github.com/kleinpanic/todo_task_manager) for task management functionalities. To install it:

```bash
git clone https://github.com/kleinpanic/todo_task_manager.git
cd todo_task_manager
# Follow the installation instructions provided in the todo_task_manager repository
```

Ensure that the `todo_task_manager` is properly installed and configured before running DashboardApp to enable full task management capabilities.

## Usage

### Running the Application
1. **Activate the Virtual Environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Start the Dashboard:**
   ```bash
   python3 tui-dashboard.py
   ```

### Command-Line Arguments
- **Display Version:**
  ```bash
  python3 tui-dashboard.py --version
  ```
  This will print the current version of DashboardApp and exit.

### Key Bindings
- `m`: Switch to **Monocle Mode** (focus on one window at a time).
- `t`: Switch to **Tiling Mode** (view all windows simultaneously).
- `j`: Navigate to the **next window** in Monocle Mode.
- `k`: Navigate to the **previous window** in Monocle Mode.
- `q`, `Q`, or `Esc`: **Quit** the application gracefully with an ASCII art goodbye message.

## Configuration

### Stocks
Configure stock symbols in `~/.config/dailyapp/conf.conf`:
```ini
[settings]
stocks=AAPL,GOOGL,TSLA
```
- **stocks:** Comma-separated list of stock symbols you wish to track.

### Weather
The application fetches weather data based on your IP location. Ensure you have an active internet connection for accurate and timely information.

### Tasks
Tasks are managed via the [todo_task_manager](https://github.com/kleinpanic/todo_task_manager) and stored in `.local/share/todo/tasks.txt`. Ensure this file exists and follows the correct format as specified below.

## Tasks Integration

DashboardApp seamlessly integrates with the [todo_task_manager](https://github.com/kleinpanic/todo_task_manager) to display and manage tasks within the dashboard interface. This integration allows you to view, add, complete, and manage tasks without leaving the terminal environment.

### Setting Up
1. **Install Todo Task Manager:**
   Follow the installation instructions in the [todo_task_manager repository](https://github.com/kleinpanic/todo_task_manager).

2. **Configure Tasks File:**
   Ensure that your tasks are properly formatted and stored in `.local/share/todo/tasks.txt`.

3. **Customize Tasks Functionality:**
   - **Using Todo Task Manager:** Use the todo task manager as-is to manage your tasks efficiently.
   - **Custom Integration:** If you prefer not to use the todo task manager, you can modify the `tasks_info` method in `dashboard.py` to suit your preferred task management system.

## Tasks File Format

The task manager expects tasks to be stored in `.local/share/todo/tasks.txt`. Each line should follow the format:

```
<Number>    <Name>    <Category>    <Priority>    <Completion (1 or 0)>    <Due Date>    <Recurrence>
```

**Example:**
```
1    Finish report    Work    High    0    2024-10-20    Weekly
```

- **Number:** Unique identifier for the task.
- **Name:** Description of the task.
- **Category:** Category or project the task belongs to.
- **Priority:** Priority level (e.g., High, Medium, Low).
- **Completion:** `1` indicates completed (`[X]`), `0` indicates not completed (`[ ]`).
- **Due Date:** Deadline for the task.
- **Recurrence:** Recurrence pattern (e.g., Daily, Weekly, None).

**Note:** This functionality is powered by the [todo_task_manager](https://github.com/kleinpanic/todo_task_manager) built in C. To customize this functionality, either install the todo task manager or modify the `tasks_info` method in `dashboard.py` to adapt to your preferred task management system.

## Supported Terminals

DashboardApp has been tested and works on the following terminals:

- `xterm`
- `gnome-terminal`
- `iTerm2` (macOS)
- `tmux`
- `screen`
- `rxvt`
- `st`
- `alacritty`
- Any standard Linux terminal (`linux`, `ansi`, etc.)

**Note:** If you encounter display issues, ensure that your terminal supports ANSI escape codes and that required utilities and fonts are installed. Additionally, tools like `figlet` and `toilet` enhance the ASCII art experience.

## Contributing

Contributions are welcome! To contribute to DashboardApp:

1. **Fork the Repository:**
   ```bash
   git clone https://github.com/kleinpanic/tui-dashboard.git
   cd tui-dashboard
   ```

2. **Create a New Branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Commit Your Changes:**
   ```bash
   git commit -am 'Add new feature'
   ```

4. **Push the Branch:**
   ```bash
   git push origin feature/my-feature
   ```

5. **Open a Pull Request:**
   Go to the [GitHub repository](https://github.com/kleinpanic/tui-dashboard) and open a pull request.

**Please ensure that:**
- Changes are well-documented.
- Code is properly commented.
- Tests are added for new features (if applicable).

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Credits

- **Figlet** and **Toilet** for ASCII graphics.
- **Python** community for the robust ecosystem.
- Weather data courtesy of **wttr.in** and **Open-Meteo**.
- Stock data fetched using **yfinance**.
- Task management powered by [todo_task_manager](https://github.com/kleinpanic/todo_task_manager).
- Inspired by various terminal-based dashboard applications.
