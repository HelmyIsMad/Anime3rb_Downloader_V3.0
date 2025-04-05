# importing needed modules
import cloudscraper # to make requests with JS enabled
import sys # to interact with the system
import os # to interact with the system
import time # to sleep (AKA wait)
import threading # to create threads (parallel processes)
import tkinter as tk # to create the GUI
import tkinter.ttk as ttk # to create the GUI
from tkinter.constants import * # to create the GUI
from bs4 import BeautifulSoup # to parse HTML and scrape
from collections import deque # to implement the queues

# the main scraper that is used to make requests and retrieve data
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False,
        "desktop" : True
    }
)

# the headers that are used in making requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'Accept': 'application/json',
}

# the function that is used to set the style of the GUI
def _style_code():
    style = ttk.Style()
    style.theme_use('default')
    style.configure('.', font = "TkDefaultFont")
    if sys.platform == "win32":
       style.theme_use('winnative')

# the main class of the app
class MyApp:
    def __init__(self, top=None):
        self.realQueue = deque() # a queue for the anime episodes
        self.animeQueue = deque() # a queue for the animes themselves
        self.busyGettingLinks = False # a flag to indicate that the thread is getting the download links
        self.busyDownloading = False # a flag to indicate that the thread is downloading

        self.consoleMsg = ""

        # window init
        top = tk.Tk()
        top.geometry("720x480")
        top.resizable(0, 0)
        top.title("Anime3rb.com Downloader by Helmy")
        self.top = top

        # the top bar where the buttons are
        self.menuBar = tk.Frame(self.top)
        self.menuBar.place(relx=0.0, rely=0.0, relheight=0.1, relwidth=1.0)

        # the queue button
        self.QueueButton = tk.Button(self.menuBar)
        self.QueueButton.place(relx=0.5, rely=0.0, height=50, width=360)
        self.QueueButton.configure(activebackground="#d9d9d9")
        self.QueueButton.configure(activeforeground="black")
        self.QueueButton.configure(background="#9c4ddd")
        self.QueueButton.configure(disabledforeground="#ff0000")
        self.QueueButton.configure(font="-family {Segoe UI} -size 17")
        self.QueueButton.configure(foreground="#000000")
        self.QueueButton.configure(highlightbackground="#d9d9d9")
        self.QueueButton.configure(highlightcolor="#000000")
        self.QueueButton.configure(text='''Downloading Queue''')
        self.QueueButton.configure(command = self.switchToQueue)

        # the download button
        self.DownloadButton = tk.Button(self.menuBar)
        self.DownloadButton.place(relx=0.0, rely=0.0, height=50, width=360)
        self.DownloadButton.configure(activebackground="#50da53")
        self.DownloadButton.configure(activeforeground="black")
        self.DownloadButton.configure(background="#50da53")
        self.DownloadButton.configure(disabledforeground="#ff0000")
        self.DownloadButton.configure(font="-family {Segoe UI} -size 17")
        self.DownloadButton.configure(foreground="#000000")
        self.DownloadButton.configure(highlightbackground="#d9d9d9")
        self.DownloadButton.configure(highlightcolor="#000000")
        self.DownloadButton.configure(state='disabled')
        self.DownloadButton.configure(text='''Download Anime''')
        self.DownloadButton.configure(command = self.switchToDownload)

        # the queue frame
        self.Queue = tk.Frame(self.top)
        self.Queue.place(relx=0.0, rely=0.104, relheight=0.896, relwidth=1.0)
        self.Queue.configure(relief="groove")
        self.Queue.configure(background="#c0c0c0")
        self.Queue.configure(highlightbackground="#d9d9d9")
        self.Queue.configure(highlightcolor="#000000")

        # idk why i did that but thats a separator :D 
        self.Separator = ttk.Separator(self.Queue)
        self.Separator.place(relx=0.0, rely=0.302,  relwidth=1.0)

        # the queue info Label, the one at the top
        self.QueueInfo = ttk.Label(self.Queue)
        self.QueueInfo.place(relx=0.09, rely=0.023, height=27, width=600)
        self.QueueInfo.configure(background="#eaeaea")
        self.QueueInfo.configure(font="-family {Segoe UI} -size 13")
        self.QueueInfo.configure(borderwidth="0")
        self.QueueInfo.configure(anchor='center')
        self.QueueInfo.configure(justify='center')
        self.QueueInfo.configure(text='''Queue is Empty''')
        self.QueueInfo.configure(compound='center')

        # the progression bar (Duh XD)
        self.ProgressionBar = ttk.Progressbar(self.Queue)
        self.ProgressionBar.place(relx=0.361, rely=0.14, relwidth=0.278, relheight=0.0, height=19)
        self.ProgressionBar.configure(length="200")
        self.ProgressionBar.configure(mode='determinate')
        self.ProgressionBar.configure(orient="horizontal")
        self.ProgressionBar.configure(value="0")

        # The label on which the percentage is displayed
        self.Percentage = ttk.Label(self.Queue)
        self.Percentage.place(relx=0.375, rely=0.209, height=27, width=183)
        self.Percentage.configure(background="#eaeaea")
        self.Percentage.configure(font="-family {Segoe UI} -size 13")
        self.Percentage.configure(borderwidth="0")
        self.Percentage.configure(anchor='center')
        self.Percentage.configure(justify='center')
        self.Percentage.configure(compound='center')

        # the Frame where i put the queue and the scrollbar
        self.TheQueue = tk.Frame(self.Queue)        
        self.TheQueue.place(relx=0.056, rely=0.372, relheight=0.586, relwidth=0.882)
        self.TheQueue.configure(background="white")
        self.TheQueue.configure(highlightbackground="#d9d9d9")
        self.TheQueue.configure(highlightcolor="#000000")

        # the canvas to display the queue in a seperate window.
        self.MyCanvas = tk.Canvas(self.TheQueue)
        self.MyCanvas.place(relx=0, rely=0, relheight=1, relwidth=1)
        self.MyCanvas.configure(background="white")
        self.MyCanvas.configure(highlightbackground="#d9d9d9")
        self.MyCanvas.configure(highlightcolor="#000000")

        # you can figure this one out right? XD 
        self.myScrollbar = ttk.Scrollbar(self.TheQueue, orient="vertical", command=self.MyCanvas.yview)
        self.myScrollbar.place(relx=0.97, rely=0, relheight=1, relwidth=0.03)

        # connecting the canvas to the scrollbar
        self.MyCanvas.configure(yscrollcommand=self.myScrollbar.set)

        # the frame where the actual queue is displayed
        self.secondFrame = tk.Frame(self.MyCanvas)
        self.secondFrame.bind("<Configure>", lambda e: self.MyCanvas.configure(scrollregion = self.MyCanvas.bbox("all")))
        self.secondFrame.configure(relief='groove')
        self.secondFrame.configure(borderwidth="2")
        self.secondFrame.configure(background="#c0c0c0")
        self.secondFrame.configure(highlightbackground="#d9d9d9")
        self.secondFrame.configure(highlightcolor="#000000")

        # connecting the frame to the canvas in a new window
        self.MyCanvas.create_window((0,0), window=self.secondFrame, anchor="nw", width = 615)

        # the download Frame
        self.Download = tk.Frame(self.top)
        self.Download.place(relx=0.0, rely=0.104, relheight=0.896, relwidth=1.0)
        self.Download.configure(relief='groove')
        self.Download.configure(borderwidth="2")
        self.Download.configure(relief="groove")
        self.Download.configure(background="#c0c0c0")
        self.Download.configure(highlightbackground="#d9d9d9")
        self.Download.configure(highlightcolor="#000000")

        # the Console label
        self.consoleLabel = tk.Label(self.Download)
        self.consoleLabel.place(relx=0.001, rely=0.8, height=50, width=180)
        self.consoleLabel.configure(background="#c0c0c0")
        self.consoleLabel.configure(font="-family {Segoe UI} -size 18 -weight bold")
        self.consoleLabel.configure(foreground="#000000")
        self.consoleLabel.configure(highlightbackground="#d9d9d9")
        self.consoleLabel.configure(highlightcolor="#000000")
        self.consoleLabel.configure(text='''Console:''')

        # the console
        self.console = tk.Label(self.Download)
        self.console.place(relx=0.25, rely=0.825, relwidth=0.6)
        self.console.configure(background="white")
        self.console.configure(font="-family {Segoe UI} -size 18")
        self.console.configure(foreground="red")
        

        # The link Entry
        self.LinkInput = tk.Entry(self.Download)
        self.LinkInput.place(relx=0.25, rely=0.250, height=30, relwidth=0.728)
        self.LinkInput.configure(background="white")
        self.LinkInput.configure(borderwidth="3")
        self.LinkInput.configure(disabledforeground="#a3a3a3")
        self.LinkInput.configure(font="-family {Courier New} -size 15")
        self.LinkInput.configure(foreground="#000000")
        self.LinkInput.configure(highlightbackground="#d9d9d9")
        self.LinkInput.configure(highlightcolor="#000000")
        self.LinkInput.configure(insertbackground="#000000")
        self.LinkInput.configure(selectbackground="#d9d9d9")
        self.LinkInput.configure(selectforeground="black")

        # The Start Download Button
        self.StartDownload = tk.Button(self.Download)
        self.StartDownload.place(relx=0.347, rely=0.419, height=86, width=217)
        self.StartDownload.configure(activebackground="#00ff4d")
        self.StartDownload.configure(activeforeground="black")
        self.StartDownload.configure(background="#00ff4d")
        self.StartDownload.configure(disabledforeground="#a3a3a3")
        self.StartDownload.configure(font="-family {Segoe UI} -size 17 -weight bold")
        self.StartDownload.configure(foreground="#000000")
        self.StartDownload.configure(highlightbackground="#d9d9d9")
        self.StartDownload.configure(highlightcolor="#000000")
        self.StartDownload.configure(state='normal')
        self.StartDownload.configure(text='''Download''')
        self.StartDownload.configure(command = lambda: threading.Thread(target=self.start_download).start())

        # The Enter Link Label
        self.EnterLink = ttk.Label(self.Download)
        self.EnterLink.place(relx=0.028, rely=0.186, height=77, width=154)
        self.EnterLink.configure(background="#c0c0c0")
        self.EnterLink.configure(font="-family {Segoe UI} -size 22 -weight bold")
        self.EnterLink.configure(relief="flat")
        self.EnterLink.configure(text='''Enter Link:''')
        self.EnterLink.configure(compound='left')
        _style_code() # this is magic XD

        # a variable to store the value of the link entry
        self.link = tk.StringVar()
        self.LinkInput.configure(textvariable=self.link)

        # a variable to store the value of the progress bar
        self.ProgressionPercentage = tk.DoubleVar()
        self.ProgressionBar.configure(variable=self.ProgressionPercentage)

    # a function to switch to the download frame
    def switchToDownload(self):
        self.Queue.place_forget()
        self.Download.place(relx=0.0, rely=0.104, relheight=0.896, relwidth=1.0)
        self.DownloadButton.configure(state='disabled')
        self.QueueButton.configure(state='normal')

    # a function to switch to the queue frame
    def switchToQueue(self):
        self.Download.place_forget()
        self.Queue.place(relx=0.0, rely=0.104, relheight=0.896, relwidth=1.0)
        self.DownloadButton.configure(state='normal')
        self.QueueButton.configure(state='disabled')
    
    # a function to start the download process, connected to the start download button
    def start_download(self):
        link: str = self.link.get()

        if not link.startswith("https://anime3rb.com/titles/") and not link.startswith("https://www.anime3rb.com/titles/"):
            threading.Thread(target=lambda: self.handle_error("link")).start()
            return

        self.link.set("")
        self.animeQueue.append(link)
        while self.busyGettingLinks:
            time.sleep(1)
        link = self.animeQueue.popleft()
        page = scraper.get(link, headers = headers)
        soup = BeautifulSoup(page.content, "html.parser")
        page.close()
        animeName = link[link.index("titles") + 7:]
        cnt = self.getEpsCnt(soup)

        episode_links = self.getEpsLinks(link, cnt)
        gettingLinks = threading.Thread(target=self.get_download_links, args=[episode_links, animeName])
        gettingLinks.start()
        while self.busyDownloading:
            time.sleep(1)
        self.start_downloads(animeName, cnt)

    # a function to get the episode count (I really need to change its algorithm)    
    def getEpsCnt(self, soup: BeautifulSoup) -> int:
        try:
            cnt1 = soup.find_all('p', class_="text-lg leading-relaxed")[1].text.strip()
            container = soup.find("div", class_="videos-container relative overflow-auto w-full h-[calc(100%-100px)]")
            cnt = len(container.find_all('a', href=True))
            if cnt1 != cnt:
                threading.Thread(target=lambda: self.handle_error("cnt")).start()
            return int(cnt)
        except (IndexError, ValueError, AttributeError):
            print("Failed to retrieve episode count.")
            scraper.close()
            sys.exit(1)

    # a function to generate the episode links
    def getEpsLinks(self, url: str, cnt: int) -> list[str]:
        res = []
        i = url.index("titles")
        base_url = url[:i] + "episode" + url[i + 6:]

        for episode in range(1, cnt + 1):
            res.append(f"{base_url}/{episode}")
        return res
    
    # a function to get the download links
    def get_download_links(self, episode_links: list[str], name: str):
        self.busyGettingLinks = True
        for i, episode in enumerate(episode_links, start=1):
            page = self.get_with_retries(episode)
            soup = BeautifulSoup(page.content, "html.parser")
            page.close()

            download_links_holder = soup.find("div", class_="flex-grow flex flex-wrap gap-4 justify-center")
            if not download_links_holder:
                print(f"Failed to find download links for {episode}")
                continue

            download_links = download_links_holder.find_all("label")
            desired = [None, None]

            for link in download_links:
                if "480" in link.text:
                    desired = [480, link]
                elif "720" in link.text and desired[0] != 1080:
                    desired = [720, link]
                elif not desired[1]:  
                    desired = [1080, link]  

            if desired[1]:
                ep_name = f"{name} - Episode {i}"
                if episode == episode_links[-1]:
                    ep_name += " [END]"
                anime = Anime(desired[1].parent.find("a")["href"], i, ep_name)
                self.realQueue.append(anime)
                anime.frame.pack(fill = "x")
                
            else:
                print(f"No valid download link found for {episode}")

        self.busyGettingLinks = False

    # a function to start the downloads of an anime
    def start_downloads(self, name: str, cnt: int):
        self.busyDownloading = True
        while not self.realQueue:
            time.sleep(1)
        
        while self.realQueue:
            anime: Anime = self.realQueue.popleft()
            link = anime.link
            epNum = anime.epNum
            anime.frame.pack_forget()
            del anime
            # print(f"Starting download for episode {counter}/{episodes}...", end='\r')

            ep_name = f"{name} - Episode {epNum}"
            if epNum == cnt:
                ep_name += " [END]"
            ep_name += '.mp4'

            self.download_video(link, ep_name)
            # print(f"Episode {counter}/{episodes} downloaded successfully!")

        self.busyDownloading = False

    # a function to download a video
    def download_video(self, link: str, name: str):
        video = scraper.get(link, headers=headers, stream=True)

        if video.status_code != 200:
            print(f"Failed to download {name}")
            return

        total_size = int(video.headers.get('content-length', 0))
        os.makedirs("output", exist_ok=True)
        with open(f"output/{name}", 'wb') as f:
            for chunk in video.iter_content(chunk_size=1024):
                f.write(chunk)
                self.QueueInfo.configure(text = f"Downloading {name}")
                self.ProgressionPercentage.set(f.tell() / total_size * 100)
                self.Percentage.configure(text=f"{f.tell() / total_size * 100:.2f}%")
        
        video.close()
        if not self.realQueue:
            self.QueueInfo.configure(text = "Queue is empty")
            self.ProgressionPercentage.set(0)
            self.Percentage.configure(text="")
    
    # useless.....
    def get_with_retries(self, url, delay = 3, retries = 3):
        for _ in range(retries):
            try:
                # print(headers)
                return scraper.get(url, headers=headers)
            except:
                print("Connection error. Retrying...")
                time.sleep(delay)
        return scraper.get(url, headers=headers)
    
    # handle errors
    def handle_error(self, error):
        if error == "link":
            self.consoleMsg = "Invalid link. Please enter a valid link."
        elif error == "cnt":
            self.consoleMsg = "Invalid episode count please check\n(from anime3rb not me T_T)"
        self.console.configure(text = self.consoleMsg)
        time.sleep(2)
        self.console.configure(text = "")

# creating the app
app = MyApp()

# an Anime object to store the Anime Episode Link and its tkinter frame object (the one preset at the queue)
class Anime:
    def __init__(self, link, EpNum, title):
        self.link = link
        self.frame = tk.Frame(app.secondFrame)
        self.epNum = EpNum
        self.title = title

        # Create a label to display the item
        label = tk.Label(self.frame, text=self.title, width=40, anchor="w")
        label.pack(side="left")

        # Create a delete button for each item
        delete_button = tk.Button(self.frame, text="Delete", command = self.suicide)
        delete_button.pack(side="right")

    def suicide(self): # T_T
        app.realQueue.remove(self)
        self.frame.pack_forget()
        del self

# running the app
app.top.mainloop()

# closing the scraper and exiting
scraper.close()
sys.exit(0)