# DashboardApp

A terminal-based dashboard application for UNIX-like systems that displays system information, weather, tasks, and stock data in an ASCII-styled interface. This project is compatible with various Linux distributions and macOS.

![DashboardApp Logo](path_to_logo_image) <!-- Optional: Add a logo if available -->

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
- [Configuration](#configuration)
- [Tasks Integration](#tasks-integration)
- [Tasks File Format](#tasks-file-format)
- [Supported Terminals](#supported-terminals)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## Features
- **Real-Time System Information:** Monitor CPU, memory, swap, disk usage, network I/O, and more.
- **Current Weather Information:** Fetch and display weather data based on your location.
- **Task Management:** Integrate with a simple text-based task system to manage your to-dos.
- **Stock Tracking:** Monitor stock prices and display them in a concise format.
- **ASCII-Styled Interface:** Enjoy a retro terminal experience with beautifully designed ASCII art.
- **Dynamic Layout Modes:**
  - **Tiling Mode:** View multiple information panels simultaneously.
  - **Monocle Mode:** Focus on one information panel at a time with easy navigation.
- **Graceful Exit:** Exit the application with a visually appealing ASCII art goodbye message.
- **Version Information:** Easily check the application version using the `--version` argument.

## Prerequisites
Before installing the DashboardApp, ensure your system meets the following requirements:

- **Python 3.x** installed
- **Git** installed (optional but recommended for cloning the repository)
- **Supported Terminal** (see [Supported Terminals](#supported-terminals))
- **Todo Task Manager:** The DashboardApp integrates with the [todo_task_manager](https://github.com/kleinpanic/todo_task_manager) for task management. Ensure it's installed and configured.

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
- Check and install Python 3 if missing.
- Set up a Python virtual environment and install necessary dependencies.
- Install utilities and fonts required for ASCII graphics.
- Detect and inform you about the shell and terminal type.

### 3. Install Todo Task Manager
Since DashboardApp relies on the [todo_task_manager](https://github.com/kleinpanic/todo_task_manager), ensure it's installed:

```bash
git clone https://github.com/kleinpanic/todo_task_manager.git
cd todo_task_manager
# Follow the installation instructions provided in the todo_task_manager repository
```

## Usage

### Running the Application
1. **Activate the Virtual Environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Start the Dashboard:**
   ```bash
   python3 dashboard.py
   ```

### Command-Line Arguments
- **Display Version:**
  ```bash
  python3 dashboard.py --version
  ```
  This will print the current version of DashboardApp and exit.

### Key Bindings
- `m`: Switch to **Monocle Mode** (focus on one window at a time).
- `t`: Switch to **Tiling Mode** (view all windows simultaneously).
- `j`: Navigate to the **next window** in Monocle Mode.
- `k`: Navigate to the **previous window** in Monocle Mode.
- `q` or `Q` or `Esc`: **Quit** the application gracefully with an ASCII art goodbye message.

## Configuration

### Stocks
Configure stock symbols in `~/.config/dailyapp/conf.conf`:

```ini
[settings]
stocks=AAPL,GOOGL,TSLA
```

### Weather
The application fetches weather data based on your IP location. Ensure you have an active internet connection for accurate information.

### Tasks
Tasks are managed via the [todo_task_manager](https://github.com/kleinpanic/todo_task_manager) and stored in `.local/share/todo/tasks.txt`. Ensure this file exists and follows the correct format.

## Tasks Integration

DashboardApp integrates with the [todo_task_manager](https://github.com/kleinpanic/todo_task_manager) to display and manage tasks within the dashboard. The task management functionality expects tasks to be stored in `.local/share/todo/tasks.txt`.

### Setting Up
1. **Install Todo Task Manager:**
   Follow the installation instructions in the [todo_task_manager repository](https://github.com/kleinpanic/todo_task_manager).

2. **Configure Tasks File:**
   Ensure that your tasks are properly formatted and stored in `.local/share/todo/tasks.txt`.

3. **Customize Tasks Functionality:**
   - **Using Todo Task Manager:** Install and use the todo task manager as-is to manage your tasks.
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

DashboardApp has been tested and works on:

- `xterm`
- `gnome-terminal`
- `iTerm2` (macOS)
- `tmux`
- `screen`
- `rxvt`
- `st`
- `alacritty`
- Any standard Linux terminal (`linux`, `ansi`, etc.)

If you encounter display issues, ensure that your terminal supports ANSI escape codes and that required utilities and fonts are installed.

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
- Weather data courtesy of **wttr.in**.
- Stock data fetched using **yfinance**.
- Task management powered by [todo_task_manager](https://github.com/kleinpanic/todo_task_manager).
- Inspired by various terminal-based dashboard applications.

