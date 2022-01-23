import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Watcher:
    def __init__(self, path):
        self.observer = Observer()
        self.path = path

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.path, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
                #print('timer')
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()



class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        # if event.is_directory:
        #     return None
        print(
            "[{}] noticed: [{}] on: [{}] ".format(
                time.asctime(), event.event_type, event.src_path
            )
        )


if __name__ == "__main__":
    w = Watcher("/home/pi/SolarPro/")
    w.run()