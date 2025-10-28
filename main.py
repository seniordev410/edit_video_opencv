
############ Susanna edited #########

from time import time
from kivy.app import App
from os.path import dirname, join
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.uix.popup import Popup

from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.boxlayout import BoxLayout
# set the initial size
from kivy.config import Config

import os
import requests

from download_async import *
from videoprocess_async import *

MAX_SIZE = (500, 800)
Config.set('graphics', 'width', MAX_SIZE[0])
Config.set('graphics', 'height', MAX_SIZE[1])
Config.set('graphics', 'resizable', False)

#############################

screen = {"screen":"main"}
user= {"email":"", "pass":"" ,"name":""}
column= {"add":""}
download = {"download":""}
report = {"mail":""}
play_list = {"ID":"", "names":""}

status_current = {"download":"", "process":""}

# final videos list
final_list = {"video":"", "from_to":"", "output":""}
# for downloading list
downloading_list = []
# for processing list
processing_list = []

from_to_list = []
video_list = []
output_list = []

def error_handling():
    return ('---UI---Error: {}  {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


########### Pop Up message #######
class UloginFail(Popup):
    def __init__(self, obj, **kwargs):
        super(UloginFail, self).__init__(**kwargs)
        self.obj = obj

##################################
class MyListItem(BoxLayout):
    def __init__(self, **kwargs):
        super(MyListItem, self).__init__(**kwargs)
        ##### video downloading thread
        self.down_video = DownloadVideo()
        self.down_status = False
        self.current_video = 0
        Clock.schedule_interval(self.watch_download_end, 0.8)

        ##### video processing thread
        self.process_video = VideoProcessAsync()
        self.process_status = False
        self.process_current = 0
        Clock.schedule_interval(self.watch_process_end, 0.9)
        ##### output file name 
    def export_click(self, text):
        # make 2 folders , origin_video, converted_video
        assure_path_exists("origin_video/")
        assure_path_exists("converted_video/")

        url = "https://match-meeting.com/iphone_cut.php?token=bJLbvhkcKcghjcFRthyserdrTSewegdtzjf6ufvzkj&\
        email=" + user["email"] + "&key=" + user["pass"] + "&ID=" + text

        result = requests.get(url)
        json_result = result.json()
        temp_video = ""
        temp_from_to_list = ""

        
        for i in range(len(json_result)):
            if json_result[i]["Video"] != temp_video:
                
                # before from_to info save
                from_to_list.append(temp_from_to_list)
                video_list.append(temp_video)
                output_list.append(text) # output filename
                
                # save new from-to info
                temp_from_to_list = json_result[i]["start"] + "-" + json_result[i]["end"]
            else:
                temp_from_to_list +=  "," + json_result[i]["start"] + "-" + json_result[i]["end"]
            
            temp_video = json_result[i]["Video"]
            
            # last video process
            if i >= len(json_result)-1:
                from_to_list.append(temp_from_to_list)
                video_list.append(temp_video)
                output_list.append(text) # output filename
            

        final_list["video"] = video_list
        final_list["from_to"] = from_to_list
        final_list["output"] = output_list
        
        # check all file downloaded
        all_downloaded = True
        for i in range(1, len(final_list["video"])):
            path = "origin_video/" + final_list["video"][i].split('/')[-1]
            if os.path.exists(path) is not True:
                all_downloaded = False

        all_process = True
        for i in range(1, len(final_list["output"])):
            path = "converted_video/" + final_list["output"][i]
            if os.path.exists(path) is not True:
                all_process = False

        if all_downloaded and all_process:

            processing_list.append(final_list)
                
        
        for i in range(1, len(final_list["video"])):
            path = "origin_video/" + final_list["video"][i].split('/')[-1]
            if os.path.exists(path) is not True:
                # downlaod video list 
                downloading_list.append(final_list["video"][i])
        
          
                
        
    def watch_download_end(self, dt):
        self.down_status = self.down_video.read()
        if self.down_status is False:
            if self.current_video < len(downloading_list):
                
                # start next video download
                self.down_video.start(downloading_list[self.current_video])
                try:
                    status_current["download"] = "starting " + downloading_list[self.current_video]
                except:
                    status_current["download"] = "starting downloading..."
                self.current_video += 1
            else:
                status_current["download"] = "  finished"
                downloading_list.clear()
                # check all file downloaded
                all_downloaded = True
                if len(final_list["video"]) <= 0:
                    all_downloaded = False
                try:
                    for i in range(1, len(final_list["video"])):
                        path = "origin_video/" + final_list["video"][i].split('/')[-1]
                        if os.path.exists(path) is not True:
                            all_downloaded = False

                    if all_downloaded:
                        processing_list.append(final_list)
                except Exception as e:
                    print(e, "######")
        else:
            try:
                status_current["download"] = "downloading " + downloading_list[self.current_video] + "..."
            except:
                status_current["download"] = "downloading .... "

    def watch_process_end(self, dt):
        self.process_status = self.process_video.read()
        if self.process_status is False:

            if self.process_current < len(processing_list):
                
                # start next video process
                
                self.process_video.start(processing_list[self.process_current])
                try:
                    status_current["process"] = "starting " + processing_list[self.process_current]["output"][0] 
                except:
                    status_current["process"] = "starting processing" 
                self.process_current += 1
            else:
                status_current["process"] = "  finished"
                processing_list.clear()
        else:
            try:
                status_current["process"] = "in progress " + processing_list[self.process_current]["output"][0] + "..."
            except:
                status_current["process"] = "in progress " + "..."
            
class ScreenManagement(ScreenManager):
    pass


class ListScreen(Screen):
    def __init__(self, **kwargs):
        super(ListScreen, self).__init__(**kwargs)
        
        Clock.schedule_interval(self.load_list, 0.2)
        Clock.schedule_interval(self.show_status, 0.8)
    def load_list(self, dt):
        
        if play_list["ID"] is not "":
            Clock.unschedule(self.load_list)
            self.ids["lbl_username"].text = user["name"]
            ### show status bar##########
            
            for i in range(len(play_list["ID"])):
                widget = MyListItem()
                widget.ids["lbl_text"].text = play_list["names"][i]
                widget.ids["lbl_id"].text = play_list["ID"][i]
                self.ids.container.add_widget(widget)
    def show_status(self, dt):
        if  self.ids is not "":
            self.ids["lbl_down"].text = "Download: " + status_current["download"]   
            self.ids["lbl_process"].text = "Process: " + status_current["process"]      
    
    def logout(self):
        user["email"] = ""
        user["pass"] = ""
        self.parent.current = 'LoginPage'

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        
    def login(self):
        txt_email = self.ids["edt_email"].text
        txt_pass = self.ids["edt_key"].text
        url = "https://match-meeting.com/iphone_cut.php?token=authbJLbvhkcKcghjcFRthyserdrTSewegdtzjf6ufvzkj&\
        email=" + txt_email + "&key=" + txt_pass
        result = requests.get(url)
        json_result = result.json()
        if json_result["status"]==1:
            user["email"] = txt_email
            user["pass"] = txt_pass
            user["name"] = json_result["username"]
            id_list = []
            names_list = []
            i = 0
            while True:
                try:
                    names_list.append(json_result[str(i)]["names"])
                    id_list.append(json_result[str(i)]["id"])
                    i += 1
                except:
                    break

            play_list["ID"] = id_list
            play_list["names"] = names_list
            print(play_list, "###############")
            self.parent.current = "ListPage"
            
        else:
            popup = UloginFail(self)    
            popup.open()

        


class MyApp(App):
    
    def check_resize(self, instance, x, y):
        # resize X
        if x > MAX_SIZE[0]:
            Window.size = (500, Window.size[1])
        # resize Y
        if y > MAX_SIZE[1]:
            Window.size = (Window.size[0], 700)   
    def mainscreen(self):
        screen["screen"] = "main"
        
    def build(self):
        self.title = 'FacEAI PRO'
        Window.size = (500, 800)
        Window.bind(on_resize=self.check_resize)

        return ScreenManagement()


if __name__ == '__main__':
    Builder.load_file("main.kv")
    MyApp().run()
    