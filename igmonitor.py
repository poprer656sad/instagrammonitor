import subprocess, sys, json, time, re, random, datetime, multiprocessing, asyncio

def install_dependencies():
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lxml'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'httpx'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'discord-webhook'])

try:
    import httpx, lxml.html as html
    from discord_webhook import DiscordWebhook, DiscordEmbed
except:
    install_dependencies()
    import httpx, lxml.html as html
    from discord_webhook import DiscordWebhook, DiscordEmbed

class instagram():
    def __init__(self, account, proxy=None, timeout=20):
        self.proxyval = proxy
        self.timeout = timeout
        self.account = account
        try:
            with open('{}.json'.format(self.account),'r+') as igdata:
                data = json.loads(igdata.readlines()[0].strip())
                self.url = data['url']
                self.lastpost = data['lastid']
        except:
            print('excepted')
            self.url, self.lastpost = '',''
        if proxy != None:
            self.session = httpx.Client(http2=True, proxies='http://' + proxy)
        else:
            self.session = httpx.Client(http2=True)
        while True:
            self.get_site(self.account)
            time.sleep(1.5)

    def get_site(self, account):
        headers = {
            'authority': 'www.instagram.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        }
        response = self.session.get('https://www.instagram.com/{}/'.format(account), headers=headers, timeout=15)
        print(response.text)
        page = html.fromstring(response.content)
        url = json.loads(page.xpath('.//body/script')[0].text[21:-1])['entry_data']['ProfilePage'][0]['graphql']['user']['external_url'].strip()
        lastpost = json.loads(page.xpath('.//body/script')[0].text[21:-1])['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges'][0]['node']['shortcode']
        if url != self.url:
            self.url = url
            self.send_bio_webhook()
        if lastpost != self.lastpost:
            self.lastpost = lastpost
            self.get_new_post()
        with open('{}.json'.format(self.account),'w+') as igdata:
            json.dump({'url':self.url,'lastid':self.lastpost}, igdata)

    def get_new_post(self):
        headers = {
            'authority': 'www.instagram.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        }
        response = self.session.get('https://www.instagram.com/p/{}/'.format(self.lastpost), headers=headers, timeout=20)
        post = html.fromstring(response.content).xpath('.//head/meta')[10].get('content')
        self.send_post_webhook(post)

    def send_bio_webhook(self):
        webhook = DiscordWebhook(
            url='webhooklink',
            username= self.account)
        embed = DiscordEmbed(title='new website', description='', color=4254719,
                             url='https://www.instagram.com/{}/'.format(self.account))
        embed.set_author(name='Instagram', url='', icon_url="https://i.imgur.com/Lz2dWcW.png")
        embed.set_timestamp()
        embed.add_embed_field(name='New Url', value=self.url, inline=False)
        embed.set_footer(text='Instagram')
        webhook.add_embed(embed)
        response = webhook.execute()

    def send_post_webhook(self, posturl):
        webhook = DiscordWebhook(
            url='webhooklink',
            username= self.account)
        embed = DiscordEmbed(title='new post', description='', color=4254719,
                             url='https://www.instagram.com/p/{}/'.format(self.lastpost))
        embed.set_author(name='Instagram', url='', icon_url="https://i.imgur.com/Lz2dWcW.png")
        embed.set_timestamp()
        embed.add_embed_field(name='New Post', value='https://www.instagram.com/p/{}/'.format(self.lastpost), inline=False)
        embed.set_image(url=posturl)
        embed.set_footer(text='Instagram')
        webhook.add_embed(embed)
        response = webhook.execute()

instagram('account name')
