import threading
from moviepy.editor import VideoFileClip, concatenate_videoclips

class VideoProcessAsync:
    def __init__(self):
        self.read_lock = threading.Lock()
        self.started = False

    def start(self, filename):
        if self.started:
            print('[!] Asynchroneous video processing has already been started.')
            return None
        self.started = True
        self.filename = filename
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        
        clips = []
        print(self.filename, "############")
        print("@@@@@@@@@@@@@@@@@@@")
        for j in range(1, len(self.filename["video"])):

            local_filename = self.filename["video"][j].split('/')[-1]
            in_folder = "origin_video/"
            out_folder = "converted_video/"
            
            in_file = in_folder + local_filename
            out_file = out_folder + self.filename["output"][j] + ".mp4"

            time_line = self.filename["from_to"][j]
            arr_time_line = time_line.split(",")

            for i in range(len(arr_time_line)):
                try:
                    from_time, to_time = arr_time_line[i].split("-")
                    print("#######", from_time, "######", to_time, "######", in_file)
                except:
                    continue
                clip = VideoFileClip(in_file).subclip(int(from_time), int(to_time))
                clips.append(clip)
        
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(out_file)

        self.started = False


    def read(self):
        with self.read_lock:
            status = self.started
            
        return status

    def stop(self):
        self.started = False
        self.thread.join()

    
