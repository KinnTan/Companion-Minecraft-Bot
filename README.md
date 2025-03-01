# Companion - A Simple Minecraft Bot

**Companion** is a very simple Minecraft bot built in Python using [Mineflayer](https://github.com/PrismarineJS/mineflayer). This repository provides a Python script that creates and manages a Minecraft bot. The bot is designed to interact in-game by following commands, navigating the world, engaging in combat, and guarding areas based on in-chat messages.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Bot Commands](#bot-commands)
- [References and Credits](#references--credits)
- [Note](#note)


## Requirements

- **Python:** 3.7+
- **Node.js:** Compatible version (e.g., v18+)
- **Dependencies:**
  - [JavaScript (JSPyBridge)](https://pypi.org/project/javascript/)  
  - [mineflayer](https://github.com/PrismarineJS/mineflayer)
  - [mineflayer-pathfinder](https://github.com/PrismarineJS/mineflayer-pathfinder)
  - [mineflayer-pvp](https://github.com/PrismarineJS/mineflayer-pvp)
  - [mineflayer-armor-manager](https://github.com/PrismarineJS/MineflayerArmorManager)
  - [vec3](https://pypi.org/project/vec3/)
  - [simple_chalk](https://pypi.org/project/simple-chalk/)


## Installation

1. **Clone the Repository** (or download the script):
    ```bash
    git clone https://github.com/KinnTan/companion-minecraft-bot.git
    cd companion-minecraft-bot
    ```

2. **Install Python Dependencies:**  
    ```bash
    pip install javascript simple-chalk vec3 
    ```

3. **Install Node.js Dependencies:**  
   Use npm or yarn to install the necessary JavaScript packages:
    ```bash
    npm install mineflayer mineflayer-pathfinder mineflayer-pvp mineflayer-armor-manager
    ```

## Usage

Run the bot with customizable parameters through the command-line:
```bash
python companion.py --username Companion --host localhost --port 25565 --version 1.21.1 [--hideErrors]
```

**Command-Line Arguments:**
- `--username`: Bot’s username (default: "Companion")
- `--host`: Minecraft server host (default: "localhost")
- `--port`: Server port (default: 25565)
- `--version`: Minecraft version (default: "1.21.1")
- `--hideErrors`: Flag to hide error messages (default: False)

## Bot Commands

Once the bot is connected to the server, it listens for several chat commands:
- **"come here"**: The bot navigates to the sender’s location.
- **"follow me"**: Initiates follow mode, tracking the sender.
- **"protect me"**: The bot follows and protects the sender by engaging nearby hostile mobs.
- **"fight me"**: Commands the bot to engage in combat with the sender.
- **"guard here"**: The bot will guard the current location.
- **"stop"**: Stops any current actions (guarding, following, or combat).

The bot responds via in-game chat messages to confirm actions.

## References & Credits

- **Mineflayer API Documentation:**  
  [Official Mineflayer Repository](https://github.com/PrismarineJS/mineflayer)  
  This contains the full API details and example code for Mineflayer and its plugins.  

- **Mineflayer in Python by 0x26e:**  
  [YouTube Playlist](https://www.youtube.com/playlist?list=PL8Uh__5X0ZE5t_yy29GFsX5U1bFyX7oUB)  
  [Github: MineflayerPython](https://github.com/0x26e/MineflayerPython)  

- **Mineflayer in JavaScript by TheDudeFromCI:**  
  [Youtube](https://www.youtube.com/playlist?list=PLh_alXmxHmzGy3FKbo95AkPp5D8849PEV)  
  [GitHub: Mineflayer-Youtube-Tutorials](https://github.com/TheDudeFromCI/Mineflayer-Youtube-Tutorials)  


- **Other Example Code and Plugin Api:**   
  [mineflayer-pathfinder](https://github.com/PrismarineJS/mineflayer-pathfinder/tree/master/examples) [API](https://github.com/PrismarineJS/mineflayer-pathfinder?tab=readme-ov-file#api)  
  [mineflayer-pvp](https://github.com/PrismarineJS/mineflayer-pvp/tree/master/examples) [API](https://github.com/PrismarineJS/mineflayer-pvp/blob/master/docs/api.md)  
  [mineflayer-armor-manager](https://github.com/PrismarineJS/MineflayerArmorManager/blob/master/example.js)  

## Note
Expect Bugs, a lot of them and unexpected crash a lot of them too
