import json
import time
from os import environ
from datetime import datetime
from dateutil import tz

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook
from dotenv import load_dotenv

load_dotenv()

TOKEN = environ["TOKEN"]
DISCORD_URL = environ["DISCORD_URL"]
CANVAS_URL = environ["CANVAS_URL"]
webhook = DiscordWebhook(DISCORD_URL, username="Wenk Bot")


def get_assignments() -> dict:
    r = requests.get(
        CANVAS_URL,
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    r.raise_for_status()
    data = r.json()
    return data


def send_assignment(data: dict) -> None:
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    webhook.remove_embeds()

    embed = DiscordEmbed(title=f"New Assignment: {data['name']}", color="3984e6")
    embed.set_author(name="Wenk Bot")
    embed.add_embed_field(name="Points Possible", value=str(data["points_possible"]))
    embed.add_embed_field(
        name="Due At",
        value=datetime.strptime(data["due_at"], "%Y-%m-%dT%H:%M:%SZ")
        .replace(tzinfo=from_zone)
        .astimezone(to_zone)
        .strftime("%I:%M:%S %p, %A, %B %d, %Y"),
    )
    embed.set_timestamp()

    webhook.add_embed(embed)
    webhook.execute()


old = get_assignments()


while True:
    new = get_assignments()
    for i in new:
        if i not in old:
            send_assignment(i)
    old = new
    time.sleep(60)
