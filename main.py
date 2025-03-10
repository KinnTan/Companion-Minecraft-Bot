import argparse
from javascript import require, On, Once, AsyncTask, once, off
from simple_chalk import chalk

parser = argparse.ArgumentParser(description='Run the mineflayer bot with custom arguments.')
parser.add_argument('--username', type=str, default='Companion', help='Username for the bot')
parser.add_argument('--host', type=str, default='localhost', help='Server host')
parser.add_argument('--port', type=int, default=25565, help='Server port')
parser.add_argument('--version', type=str, default='1.21.1', help='Minecraft version')
# Use action='store_true' so --hideErrors sets the flag to True; if omitted, it stays False.
parser.add_argument('--hideErrors', action='store_true', help='Hide errors flag')
args = parser.parse_args()

bot_args = {
    "username": args.username,
    "host": args.host,
    "port": args.port,
    "version": args.version,
    "hideErrors": args.hideErrors,
}

# javascript libraries
mineflayer = require("mineflayer")
mineflayer_pathfinder = require("mineflayer-pathfinder")
pvp = require("mineflayer-pvp").plugin
vec3 = require("vec3")
armorManager = require("mineflayer-armor-manager")

# Global Flags
reconnect = True
is_following = False
is_follow_protect = False
followTarget = None
guardPos = None
looking = True


def lookingTrue():
    global looking
    looking = True


def pathfind_to_goal(bot, goal_location):
    global looking
    looking = False
    bot.pathfinder.setGoal(
        mineflayer_pathfinder.pathfinder.goals.GoalNear(
            goal_location["x"], goal_location["y"], goal_location["z"], 1
        )
    )
    bot.chat("Navigating to your location. Please wait...")


def pathfind_to_goalfollow(bot, target_player):
    global is_following, looking
    looking = False
    is_following = True
    bot.pathfinder.setGoal(
        mineflayer_pathfinder.pathfinder.goals.GoalFollow(target_player, 1), True)
    bot.chat("I'm now following you. Stay close!")


def best_sword(bot):
    swords = [item for item in bot.inventory.items() if "sword" in item.name]
    if not swords:
        return None
    ranking = {
        "netherite_sword": 5,
        "diamond_sword": 4,
        "iron_sword": 3,
        "stone_sword": 2,
        "wooden_sword": 1,
    }

    def sword_value(item):
        for sword_type, value in ranking.items():
            if sword_type in item.name:
                return value
        return 0

    best = max(swords, key=lambda item: sword_value(item))
    return best


def equip_sword(bot):
    sword = best_sword(bot)
    if sword:
        bot.equip(sword, "hand")


def equip_shield(bot):
    for item in bot.inventory.items():
        if "shield" in item.name:
            bot.equip(item, "off-hand")
            break


def stop_follow(bot):
    global is_following, is_follow_protect, followTarget
    is_following = False
    is_follow_protect = False
    followTarget = None
    bot.pathfinder.setGoal(None)
    print(chalk.yellow("Stopping current follow action."))
    bot.chat("Stopping follow mode. Standing by.")
    return


def guard_area(bot, pos):
    global guardPos
    guardPos = pos.clone()
    print(chalk.blue("Guarding area at: " + str(guardPos)))
    bot.chat("Guarding this location")
    if not bot.pvp.target:
        move_to_guard_pos(bot, guardPos)


def stop_guarding(bot):
    global guardPos
    guardPos = None
    bot.pvp.stop()
    bot.pathfinder.setGoal(None)
    print(chalk.blue("Stopped guarding."))
    bot.chat("I will no longer guard this area.")


def move_to_guard_pos(bot, pos):
    global guardPos
    if guardPos is None:
        return
    else:
        print(chalk.cyan("Moving to guard position: " + str(guardPos)))
        bot.pathfinder.setGoal(
            mineflayer_pathfinder.pathfinder.goals.GoalNear(
                pos["x"], pos["y"], pos["z"], 1
            )
        )
    print(chalk.cyan("Moving to guard position: " + str(guardPos)))


def compute_distance(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def start_bot():
    bot = mineflayer.createBot(bot_args)
    bot.loadPlugin(mineflayer_pathfinder.pathfinder)
    bot.loadPlugin(pvp)
    bot.loadPlugin(armorManager)

    @On(bot, "spawn")
    def on_spawn(this):

        @On(bot, "login")
        def login(this):
            bot_socket = bot._client.socket
            server = bot_socket.server if bot_socket.server else bot_socket._host
            print(chalk.green(f"Logged in to {server}"))
            bot.chat("Hello! I'm online and ready to assist you.")

        @On(bot, "playercollect")
        def playercollect(collector, itemDrop):
            if collector != bot.entity:
                return
            AsyncTask(bot, 150, lambda: equip_sword(bot))
            AsyncTask(bot, 250, lambda: equip_shield(bot))
            AsyncTask(bot, 350, lambda: bot.armorManager.equipAll())

        @On(bot, "stoppedAttacking")
        def stopped_attacking(this):
            if guardPos is not None:
                move_to_guard_pos(bot, guardPos)
            elif is_follow_protect and followTarget is not None:
                print(chalk.cyan(print("Resuming follow mode after combat.")))
                pathfind_to_goalfollow(bot, followTarget)

        @On(bot, "physicsTick")
        def tick(this):
            global guardPos, is_follow_protect, looking
            if guardPos is None and not is_follow_protect:
                if looking is True:
                    other_entity = bot.nearestEntity()
                    if other_entity:
                        bot.lookAt(vec3(other_entity.position.x, other_entity.position.y + other_entity.height,
                                        other_entity.position.z))
                return
            entity = bot.nearestEntity()
            if entity and entity.kind == "Hostile mobs":
                if compute_distance(entity.position, bot.entity.position) < 16:
                    equip_sword(bot)
                    bot.pvp.attack(entity)

        @On(bot, "goal_reached")
        def on_goal_reached(this, goal):
            global looking
            looking = True
            bot.chat("I have arrived at your destination!")

        @On(bot, "messagestr")
        def messagestr(this, message, messagePosition, jsonMsg, sender, verified=None):
            if messagePosition == "chat":
                if "quit" in message:
                    bot.chat("Goodbye! Shutting down now.")
                    bot.reconnect = False
                    this.quit()

                elif "come here" in message:
                    if is_following:
                        bot.chat("I'm already following you!")
                    else:
                        local_players = bot.players
                        player_location = None
                        for el in local_players:
                            player_data = local_players[el]
                            if player_data["uuid"] == sender:
                                if not player_data.entity:
                                    bot.chat("You seem to be too far away for me to see.")
                                    return
                                vec3_temp = player_data.entity.position
                                player_location = vec3(vec3_temp["x"], vec3_temp["y"], vec3_temp["z"])
                                break
                        if player_location:
                            bot.chat("Got it! I'm on my way to you.")
                            pathfind_to_goal(bot, player_location)

                elif "follow me" in message:

                    local_players = bot.players
                    target_player = None
                    for el in local_players:
                        player_data = local_players[el]
                        if player_data["uuid"] == sender:
                            target_username = player_data["username"]
                            if target_username in bot.players:
                                target_player = bot.players[target_username]
                            break
                    if target_player:
                        if not target_player.entity:
                            bot.chat("I can't see you please come closer.")
                            return
                        else:
                            print(chalk.cyan(print(f"Now following")))
                            bot.chat("Following you now. Let’s stick together!")
                            pathfind_to_goalfollow(bot, target_player.entity)
                    else:
                        bot.chat("I couldn't locate you. Please try again.")

                elif "protect me" in message:

                    local_players = bot.players
                    target_player = None
                    for el in local_players:
                        player_data = local_players[el]
                        if player_data["uuid"] == sender:
                            target_username = player_data["username"]
                            if target_username in bot.players:
                                target_player = bot.players[target_username]
                            break
                    if target_player:
                        if not target_player.entity:
                            bot.chat("I can't see you please come closer.")
                            return
                        else:
                            bot.chat(
                                "Following you and protecting you now. I will fight off any hostile mobs that come close!")
                            global is_follow_protect, followTarget
                            is_follow_protect = True
                            followTarget = target_player.entity
                            print(chalk.cyan(print(f"Now following and Protecting")))
                            pathfind_to_goalfollow(bot, target_player.entity)
                    else:
                        bot.chat("I couldn't locate you. Please try again.")

                elif "fight me" in message:
                    local_players = bot.players
                    target_entity = None
                    for el in local_players:
                        player_data = local_players[el]
                        if player_data["uuid"] == sender:
                            if not player_data.entity:
                                bot.chat("You seem too far away to fight.")
                                return
                            target_entity = player_data.entity
                            break
                    if target_entity:
                        global looking
                        looking = False
                        bot.chat("Engaging combat mode! Prepare yourself!")
                        bot.pvp.attack(target_entity)
                        equip_sword(bot)

                elif "guard here" in message:
                    local_players = bot.players
                    player_location = None
                    for el in local_players:
                        player_data = local_players[el]
                        if player_data["uuid"] == sender:
                            if not player_data.entity:
                                bot.chat("I can't see you well enough to guard here.")
                                return
                            pos = player_data.entity.position
                            player_location = vec3(pos.x, pos.y, pos.z)
                    if player_location:
                        bot.chat("Understood. I will guard this area at " + str(player_location) + ".")
                        guard_area(bot, player_location)

                elif "stop" in message:
                    if guardPos is not None:
                        bot.chat("Alright, stopping guard mode.")
                        stop_guarding(bot)
                    else:
                        lookingTrue()
                        bot.chat("Okay, halting all current actions.")
                        stop_follow(bot)
                        bot.pvp.stop()

        @On(bot, "kicked")
        def kicked(this, reason, loggedIn):
            if loggedIn:
                print(chalk.red(f"Kicked whilst trying to connect: {reason}"))
                bot.chat("I've been kicked from the server!")

        @On(bot, "end")
        def end(this, reason):
            print(chalk.red(f"Disconnected: {reason}"))
            bot.chat("Disconnected from the server. Attempting to restart...")
            off(bot, "login", login)
            off(bot, "kicked", kicked)
            off(bot, "messagestr", messagestr)
            if reconnect:
                print(chalk.magenta("RESTARTING BOT"))
                start_bot()
            off(bot, "end", end)


start_bot()
