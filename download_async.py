import requests
import threading

class DownloadVideo:
    def __init__(self):
        
        self.started = False
        self.read_lock = threading.Lock()

    def start(self, url):
        self.url = url
        print("##############", url)
        if self.started:
            print('[!] Asynchroneous video downloading has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self.download_file, args=())
        self.thread.start()
        return self

    def download_file(self):
        local_filename = self.url.split('/')[-1]
        path = "origin_video/"
        # NOTE the stream=True parameter below
        with requests.get(self.url, stream=True) as r:
            r.raise_for_status()
            with open(path + local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        # f.flush()
        print("finished download")
        self.started = False
        return local_filename

    def read(self):
        with self.read_lock:
            status = self.started
            
        return status

    def stop(self):
        self.started = False
        self.thread.join()
