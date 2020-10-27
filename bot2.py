import discord
import requests
import re
import time
from bs4 import BeautifulSoup

URL = 'https://bbs.io-tech.fi/forums/naeytoenohjaimet.74/?order=post_date&direction=desc'
headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}
global olditem
olditem = 'no old item'


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'test':
            await message.channel.send('works')


async def my_background_task(client):
    await client.wait_until_ready()
    channel = client.get_channel(755455787719065681) #channel id
    while True:
        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        posts = soup.findAll("div", {"class": "structItem-title"})
        # first post
        xpost = posts[0]
        # get link, sell or buy, item name, item link
        link, sorb, item, href = get_item_info(xpost)

        xitem = get_old_item()
        print(xitem)
        if xitem != href:
            global olditem
            olditem = href
            print(xitem)
            price = find_price(link)
            print(sorb + ' ' + item + ' hintaan ' + price + '€')
            print(link)
            await channel.send(sorb + ' ' + item + ' hintaan ' + price + '€\n' + link )
        time.sleep(60)



def get_old_item():
    return olditem


def get_item_info(xpost):
    sorb = xpost.find("a", {"class": "labelLink"}).get_text()
    postlinks = xpost.findAll("a")
    item = postlinks[1].get_text()

    for a in xpost.find_all('a', href=True):
        link = 'https://bbs.io-tech.fi' + a['href']
        href = a['href']

    return link, sorb, item, href


def find_price(link):
    page = requests.get(link, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    posts = soup.findAll("div", {"class": "bbWrapper"})
    msn = posts[0].get_text()

    if msn.find('Hinta'):
        price_in_str = msn.find('Hinta')
    elif msn.find('hinta'):
        price_in_str = msn.find('hinta')
    elif msn.find('Hp:'):
        price_in_str = msn.find('Hp:')
    elif msn.find('hp:'):
        price_in_str = msn.find('hp:')
    else:
        price_in_str = 0
    xprice = msn[price_in_str:price_in_str + 12]
    price = re.findall('\d+', xprice)

    return price[0]


def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()


token = read_token()
client = MyClient()
client.loop.create_task(my_background_task(client))
client.run(token)
