from javascript import require, On, Once, AsyncTask, once, off

# javascript libraries
mineflayer = require("mineflayer")
mineflayer_pathfinder = require("mineflayer-pathfinder")
pvp = require('mineflayer-pvp').plugin
armorManager = require("mineflayer-armor-manager")
vec3 = require("vec3")

bot_args = {"username": "test-bot", "host": "localhost", "port": 25565, "version": "1.21.1", "hideErrors": False}

#global
reconnect = True
is_following = False

def pathfind_to_goal(bot, goal_location):
    bot.pathfinder.setGoal(
        mineflayer_pathfinder.pathfinder.goals.GoalNear(
            goal_location["x"], goal_location["y"], goal_location["z"], 1
        )
    )


def pathfind_to_goalfollow(bot, target_player):
    global is_following
    is_following = True
    bot.pathfinder.setGoal(
        mineflayer_pathfinder.pathfinder.goals.GoalFollow(target_player, 1), True
    )

def lookatplayer(bot, sender):
    for look in bot.players:
        player_data = bot.players[look]
        if player_data["uuid"] == sender:
            if not player_data.entity:
                return
            vec3_temp = player_data.entity.position
            player_location = vec3(
                vec3_temp["x"], vec3_temp["y"] + 1, vec3_temp["z"]
            )

        if player_location:
            bot.lookAt(player_location)
        break

def stop_follow(bot):
    global is_following
    is_following = False
    bot.pathfinder.setGoal(None)
    print("Stopping.")
    return

def start_bot():
    bot = mineflayer.createBot(bot_args)
    #load plugins
    bot.loadPlugin(mineflayer_pathfinder.pathfinder)
    bot.loadPlugin(pvp)
    bot.loadPlugin(armorManager)

    @On(bot, "login")
    def login(this):
        bot_socket = bot._client.socket
        print(
            f"Logged in to {bot_socket.server if bot_socket.server else bot_socket._host }"
        )


    @On(bot, "kicked")
    def kicked(this, reason, loggedIn):
        if loggedIn:
            print(f"Kicked whilst trying to connect: {reason}")

    @On(bot, "messagestr")
    def messagestr(this, message, messagePosition, jsonMsg, sender, verified=None):

        if messagePosition == "chat":
            if "quit" in message:
                bot.chat("Goodbye!")
                bot.reconnect = False
                this.quit()

            if "look at me" in message:
                lookatplayer(bot, sender)

            if "come here" in message:
                if is_following:
                    bot.chat("Currently Following You")
                else:
                    # Find all nearby players
                    local_players = bot.players

                    # Search for our specific player
                    for el in local_players:
                        player_data = local_players[el]
                        if player_data["uuid"] == sender:
                            if not player_data.entity:
                                bot.chat("You are too far away! I can't see you.")
                                return
                            vec3_temp = player_data.entity.position
                            player_location = vec3(
                                vec3_temp["x"], vec3_temp["y"], vec3_temp["z"]
                            )
                            break
                    if player_location:
                        pathfind_to_goal(bot, player_location)

            if "stop" in message:
                bot.chat("Stopping...")
                stop_follow(bot)
                bot.pvp.stop()
                return

            if "follow me" in message:
                print("following player")
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
                        bot.chat("You are too far away! I can't see you.")
                        return
                    else:
                        print(f"Now following {target_player.username}")
                        pathfind_to_goalfollow(bot, target_player.entity)
                else:
                    print(f"Player with UUID {sender} not found.")

            if "fight me" in message:
                local_players = bot.players
                target_entity = None
                for el in local_players:
                    player_data = local_players[el]
                    if player_data["uuid"] == sender:
                        if not player_data.entity:
                            bot.chat("You're too far away!")
                            return
                        target_entity = player_data.entity
                        break
                if target_entity:
                    bot.chat("Prepare to fight!")
                    bot.pvp.attack(target_entity)

    @On(bot, "end")
    def end(this, reason):
        print(f"Disconnected: {reason}")
        off(bot, "login", login)
        off(bot, "kicked", kicked)
        off(bot, "messagestr", messagestr)
        if reconnect:
            print("RESTARTING BOT")
            start_bot()
        off(bot, "end", end)

start_bot()