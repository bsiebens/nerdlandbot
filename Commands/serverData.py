from os import path

import json

_configFolder = "./GuildConfigs/"
_guildConfigCache = dict()


async def save_configs(guild_id: int):
    for key in _guildConfigCache:
        config = _guildConfigCache[key]

        if config.guild_changed:
            config.save(guild_id)


async def get_guild_data(guild_id: int):
    # check if memory cache contains server config
    if guild_id in _guildConfigCache.keys():
        return _guildConfigCache[guild_id]

    # check if server config file exists
    config = None
    fileName = __get_file_path(guild_id)

    if path.exists(fileName):
        # Load data
        config = await __read_file(fileName)
        config.guild_changed = False
    else:
        # Init new instance of ServerData
        config = GuildData(guild_id)

    _guildConfigCache[guild_id] = config
    return config


async def __read_file(filename: str):
    # TODO: Actually make this async
    with open(filename) as config:
        data = json.load(config)

        serverData = GuildData()
        serverData.notification_lists = data["notification_lists"]

        return serverData


def __get_file_path(guild_id: int):
    return _configFolder + str(guild_id) + ".json"


class GuildData:
    guild_id: int
    guild_changed: bool
    notification_lists: dict()

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.guild_changed = False
        self.notification_lists = dict()

    def sub_user(self, list_name: str, user_id: int):
        if self.notification_lists.keys():
            return "This list does not exist"
            # TODO: print lists with reactions to sub
        elif user_id in self.notification_lists[list_name]["users"]:
            return "You are already subscribed to this list"
        else:
            self.notification_lists[list_name]["users"].append(user_id)
            self.guild_changed = True
            self.save()
            return "Subscribed <@" + str(user_id) + "> to " + list_name

    def unsub_user(self, list_name: str, user_id: int):
        if list_name not in self.notification_lists.keys():
            return "That list does not seem to exist, cannot unsubscribe"
        else:
            if user_id in self.notification_lists[list_name]["users"]:
                self.notification_lists[list_name]["users"].remove(user_id)
                self.guild_changed = True
                self.save()
                return "Unsubscribed <@" + str(user_id) + "> from " + list_name
            else:
                return "You dont seem to be subscribed to this list"

    def notify(self, list_name: str):
        if list_name not in self.notification_lists.keys():
            return "That list does not seem to exist"
        else:
            if self.notification_lists[list_name]:

                mentionList = []
                for id in self.notification_lists[list_name]["users"]:
                    mentionList.append("<@" + str(id) + ">")
                return "Notifying " + ", ".join(mentionList)
            else:
                return "Nobody to notify"

    async def save(self):
        await __write_file()
        self.guild_changed = False

    async def __write_file(self):
        with open(__get_file_path(self.guild_id), "w+") as config:
            json.dump(self.__dict__, config, indent=4, sort_keys=True)
