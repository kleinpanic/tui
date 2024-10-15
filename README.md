# DashboardApp

A terminal-based dashboard application for UNIX-like systems that displays system information, weather, tasks, and stock data in an ASCII-styled interface. This project is compatible with various Linux distributions and macOS.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Tasks File Format](#tasks-file-format)
- [Supported Terminals](#supported-terminals)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## Features
- Display real-time system information including CPU, memory, and network usage.
- Fetch and display current weather information based on location.
- Manage tasks with a simple text-based task system.
- Track stock prices and display them in a concise format.
- ASCII-styled interface for a retro terminal experience.

## Prerequisites
Before installing the DashboardApp, make sure your system meets the following requirements:
- **Python 3.x** installed
- **Git** installed (optional but recommended for cloning the repository)
- **Supported terminal** (see [Supported Terminals](#supported-terminals))

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DashboardApp.git
   cd DashboardApp
   ```

2. Run the install script:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   The install script will:
   - Check and install Python 3 if missing
   - Set up a Python virtual environment and install necessary dependencies
   - Install utilities and fonts required for ASCII graphics
   - Detect and inform you about the shell and terminal type

## Usage
To run the application:
1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Start the dashboard:
   ```bash
   python3 dashboard.py
   ```
3. Use the following keys while running:
   - `m`: Switch to monocle mode
   - `t`: Switch to tiling mode
   - `j`/`k`: Navigate through windows in monocle mode
   - `q`: Quit the application

## Configuration
- **Tasks**: Ensure that tasks are stored in `.local/share/todo/tasks.txt`. Refer to the [Tasks File Format](#tasks-file-format) section for details.
- **Stocks**: Configure stock symbols in `~/.config/dailyapp/conf.conf`:
  ```
  [settings]
  stocks=AAPL,GOOGL,TSLA
  ```

## Tasks File Format
The task manager expects tasks to be stored in `.local/share/todo/tasks.txt`. Each line should follow the format:
```
<Number>    <Name>    <Category>    <Priority>    <Completion (1 or 0)>    <Due Date>    <Recurrence>
```
Example:
```
1    Finish report    Work    High    0    2024-10-20    Weekly
```

- **Completion**: `1` indicates completed (`[X]`), `0` indicates not completed (`[ ]`).

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

If you encounter display issues, make sure `figlet` and `toilet` are installed and that your terminal supports ASCII art.

## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push the branch (`git push origin feature/my-feature`).
5. Open a pull request.

Contributions are welcome! Please ensure that any changes are well-documented and covered with comments.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Credits
- **Figlet** and **Toilet** for ASCII graphics
- **Python** community for the robust ecosystem
- Weather data courtesy of **wttr.in**
- Stock data fetched using **yfinance**
```

