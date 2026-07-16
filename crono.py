#!/usr/bin/env python3

import pygame, os, sys
from pathlib import Path
from platformdirs import user_config_dir

os.environ['SDL_VIDEO_CENTERED'] = '1'

def get_path(relative_path):
    if getattr(sys, 'frozen', False):
        # ./binario
        base_path = os.path.dirname(sys.executable)
    else:
        # python .py
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    return os.path.join(base_path, relative_path)

def clean_newline(s):
    return "".join([char for char in s if char not in "\n"])

class App:
    def __init__(self, config_path, last_time, last_mode, last_timer_start):
        
        pygame.init()
        pygame.display.set_mode(flags=pygame.HIDDEN)
        pygame.display.set_caption("Crono")

        self.icon = self.load_image("data/images/icon.png")
        pygame.display.set_icon(self.icon)

        self.config_path = config_path

        self.save_path = self.config_path / "save.txt"

        self.w, self.h = 35 * 8 + 15 * 3 + 5, 50
        self.screen = pygame.display.set_mode((self.w, self.h))

        self.clock = pygame.time.Clock()
        self.fps = 30
        self.running = True

        self.bg_color = "black"
        self.red = "red"
        self.yellow = "#ffb000"
        self.green = "#26a269"
        self.blue = "#12488b"
        self.gray = "#808080"
        self.white = "#ffffff"
        self.text_color = self.gray

        self.fonts = {}
        self.path_font = get_path("data/fonts/lemonmilk.otf")
        self.font_size = 48
        self.font_size_mini = 36

        self.text = {}

        self.type_message = self.get_text("Type here", 36, self.white)
        self.error_message = self.get_text("Invalid format", 36, self.white)
        self.restart_message = self.get_text("Are you sure to restart?", 20, self.white)
        self.switch_timer_message = self.get_text("Switch to timer?", 30, self.white)
        self.mode_timer_message = self.get_text("Timer mode", 30, self.white)
        self.switch_crono_message = self.get_text("Switch to crono?", 30, self.white)
        self.mode_crono_message = self.get_text("Cronometer mode", 30, self.white)

        self.two_sec = 60 * 2
        self.one_sec = 60
        self.half_sec = 60 * 1/2
        self.message_time = self.one_sec + self.half_sec

        self.time_input = ""
        self.time = int(last_time) if last_time != None and last_time.isdigit() else 0
        self.timer_start = int(last_timer_start) if last_timer_start != None and last_timer_start.isdigit() else 60000 * 5 

        self.pause = True
        self.finish = False

        self.milliseconds_allowed = True

        self.mode_crono = True if last_mode == "crono" or last_mode == None else False
        self.mode_timer = True if last_mode == "timer" else False
        self.mode_editor = False
        self.mode_dialog = True
        self.dialog_wait = False
        self.ask_restart = False

        self.mode = last_mode if last_mode != None else "crono"
        self.dialog = self.mode_crono_message if self.mode_crono else self.mode_timer_message
        if self.mode_timer:
            self.time = self.timer_start

    def load_image(self, path):
        return pygame.image.load(get_path(path)).convert_alpha()

    def center_pos(self, surf):
        return ((self.w - surf.get_width()) // 2, (self.h - surf.get_height()) // 2)

    def get_font(self, size):

        if not size in self.fonts.keys():     
            self.fonts[size] = pygame.font.Font(self.path_font, size)

        return self.fonts[size]

    def get_text(self, string, size=0, color=None):

        if size == 0:
            size = self.font_size

        if color == None:
            color = self.text_color

        if not string in self.text.keys():
            self.text[string] = {}
            self.text[string][size] = {}
            self.text[string][size][color] = self.get_font(size).render(string, True, color)

        elif not size in self.text[string].keys():
            self.text[string][size] = {}
            self.text[string][size][color] = self.get_font(size).render(string, True, color)

        elif not color in self.text[string][size].keys():
            self.text[string][size][color] = self.get_font(size).render(string, True, color)

        return self.text[string][size][color]

    def show_dialog(self, surf, time):
        self.pause = True
        self.mode_dialog = True
        self.dialog = surf
        self.message_time = time
        self.dialog_wait = True if time == -1 else False

    def run(self):

        while self.running:
            for event in pygame.event.get():

                # close de app
                if event.type == pygame.QUIT:
                    
                    with open(self.save_path, 'w') as f:
                        f.write(str(self.time) + '\n')
                        f.write(self.mode + '\n')
                        f.write(str(self.timer_start))
                    self.running = False

                # keyboard events
                if event.type == pygame.KEYDOWN:
                    
                    if event.key == pygame.K_m:
                        self.milliseconds_allowed = not self.milliseconds_allowed

                    if self.dialog_wait:

                        if self.mode_crono:

                            if self.ask_restart:

                                if event.key == pygame.K_r:
                                    self.time = 0
                                self.ask_restart = False
                                self.mode_dialog = False

                            else:

                                if event.key in [pygame.K_t, pygame.K_y, pygame.K_RETURN, pygame.K_KP_ENTER]:
                                    self.mode_crono = False
                                    self.mode_timer = True
                                    self.mode = "timer"
                                    self.time = self.timer_start
                                    self.show_dialog(self.mode_timer_message, self.one_sec)
                                else:
                                    self.mode_dialog = False

                        elif self.mode_timer:

                            if self.ask_restart:

                                if event.key == pygame.K_r:
                                    self.time = self.timer_start
                                self.ask_restart = False
                                self.mode_dialog = False

                            else:

                                if event.key in [pygame.K_c, pygame.K_y, pygame.K_RETURN, pygame.K_KP_ENTER]:
                                    self.mode_timer = False
                                    self.mode_crono = True
                                    self.mode = "crono"
                                    self.time = 0
                                    self.show_dialog(self.mode_crono_message, self.one_sec)
                                else:
                                    self.mode_dialog = False

                        self.dialog_wait = False

                    elif self.mode_editor:

                        if event.key in [pygame.K_ESCAPE, pygame.K_e]:
                            self.mode_editor = False

                        # backspace - delete last digit
                        if event.key == pygame.K_BACKSPACE:
                            self.time_input = self.time_input[:-1]
                        else:
                            char = event.unicode
                            if char in "0123456789:.":
                                self.time_input += char

                        # validate and apply time input
                        if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:

                            if self.check_text(self.time_input):

                                start_point = self.make_time(self.time_input)
                                if self.mode_timer:
                                    self.timer_start = start_point

                                self.time = start_point
                                self.mode_editor = False
                                self.time_input = ""

                            else:
                                self.show_dialog(self.error_message, self.one_sec)

                    elif self.mode_crono:
                        
                        if event.key == pygame.K_SPACE:
                            self.pause = not self.pause
                            self.finish = False
                        
                        if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                            if self.text_color == self.gray:
                                self.pause = False
                                self.finish = False
                            else:
                                self.pause = True
                                self.finish = True

                        if event.key == pygame.K_t:
                            self.show_dialog(self.switch_timer_message, -1)
                            
                        if event.key == pygame.K_e:
                            self.mode_editor = True
                            self.pause = True

                        if event.key == pygame.K_r:

                            if self.time == 0:
                                continue
                            else:
                                self.ask_restart = True
                                self.show_dialog(self.restart_message, -1)

                    elif self.mode_timer:
                        
                        if event.key == pygame.K_SPACE:
                            self.pause = not self.pause
                            self.finish = False
                        
                        if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                            self.pause = not self.pause

                        if event.key == pygame.K_c:                            
                            self.show_dialog(self.switch_crono_message, -1)
                            
                        if event.key == pygame.K_e:
                            self.mode_editor = True
                            self.pause = True

                        if event.key == pygame.K_r:

                            if self.time == self.timer_start:
                                continue
                            else:
                                self.ask_restart = True
                                self.show_dialog(self.restart_message, -1)
            self.update()
            self.render()

        pygame.quit()

    def update(self):
        self.clock.tick(self.fps)

        # Up or down
        mode = 1 if self.mode_crono else -1

        if not self.pause:
            self.time = max(0, self.time + mode * self.clock.get_time())
            
        # Text color
        if self.mode_crono:
            self.text_color = self.green
            
            if self.pause:
                self.text_color = self.gray
            
            if self.finish and self.time != 0:
                self.text_color = self.blue

        elif self.mode_timer:
            self.text_color = self.yellow
            
            if self.pause:
                self.text_color = self.gray

            if self.time <= 0:
                self.text_color = self.red

        if self.message_time:
            self.message_time = max(0, self.message_time - 1)

            if not self.dialog_wait and self.message_time <= 0:
                self.mode_dialog = False


    def render(self):

        self.screen.fill(self.bg_color)

        self.milliseconds = self.time % 1000 // 10
        self.seconds = (self.time // 1000) % 60
        self.minutes = (self.time // 60000) % 60
        self.hours = (self.time // 3600000)

        if self.mode_dialog:
            self.screen.blit(self.dialog, self.center_pos(self.dialog))
        
        elif self.mode_editor:
            if self.time_input == "":
                text = self.type_message
            else:
                text = self.get_text(self.time_input, self.font_size, self.white)
            self.screen.blit(text, self.center_pos(text))
        
        else:
            # cronometer or timer
            text = f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}.{self.milliseconds:02}"
            self.render_time(text)

        pygame.display.flip()

    def render_time(self, text):

        if self.hours > 999:
            self.font_size = 42
            self.font_size_mini = 30
        elif self.hours > 99:
            self.font_size = 46
            self.font_size_mini = 34
        else:
            self.font_size = 48
            self.font_size_mini = 36

        self.number_w , self.number_h = self.get_text("0", self.font_size).get_size()
        self.number_mini_w , self.number_mini_h = self.get_text("0", self.font_size_mini+1).get_size()
        self.colon_w, self.colon_h = self.get_text(":", self.font_size).get_size()


        c = 0
        left_zero = 0
        first_non_zero = False
        for char in text:
            if char in "0:." and not first_non_zero:
                left_zero += 1
            else:
                first_non_zero = True
            c += 1
        show = max(4, c - left_zero)

        offset = 0
        count = 1
        for char in reversed(text):

            if count > 2:
                char_surface = self.get_text(char)
                char_w, char_h = char_surface.get_size()
                pos = (self.w - self.number_w // 2 - char_w // 2 - offset, (self.h - self.number_h) // 2)
            else:
                char_surface = self.get_text(char, self.font_size_mini)
                char_w, char_h = char_surface.get_size()
                pos = (self.w - self.number_mini_w // 2 - char_w // 2 - offset, (self.h // 2 + self.number_h // 2 - self.number_mini_h))

            if char in ":.":
                char_w, char_h = self.colon_w, self.colon_h
                pos = (self.w - offset - char_w, (self.h - char_h) // 2)
                offset += self.colon_w
            elif count > 2:
                offset += self.number_w
            else:
                offset += self.number_mini_w

            if not self.milliseconds_allowed:
                pos = (pos[0] + self.number_mini_w * 2 + self.colon_w, pos[1])

            if show:
                self.screen.blit(char_surface, pos)
            show = max(0, show-1)

            count += 1

    def check_text(self, text):

        result = True

        dots = text.count(".")
        colons = text.count(":")

        if colons > 2 or dots > 1:
            result = False
            return result

        if colons == 0:
            seconds = text.split(".")[0].split(":")[0]
            minutes = "00"
            hours = "00"

        if colons == 1:
            seconds = text.split(".")[0].split(":")[1]
            minutes = text.split(":")[0]
            hours = "00"

        if colons == 2:
            seconds = text.split(".")[0].split(":")[2]
            minutes = text.split(":")[1]
            hours = text.split(":")[0]

        if dots == 1:
            miliseconds = text.split(".")[1]
        else:
            miliseconds = "00"

        if not hours.isnumeric():
            result = False

        elif not minutes.isnumeric() or int(minutes) > 59:
            result = False

        elif not seconds.isnumeric() or int(seconds) > 59:
            result = False

        elif not miliseconds.isnumeric() or int(miliseconds) > 99:
            result = False

        return result
    
    def make_time(self, text=""):
        
        if not text:
            return 0

        dots = text.count(".")
        colons = text.count(":")

        if colons == 0:
            seconds = text.split(".")[0].split(":")[0]
            minutes = "00"
            hours = "00"

        if colons == 1:
            seconds = text.split(".")[0].split(":")[1]
            minutes = text.split(":")[0]
            hours = "00"

        if colons == 2:
            seconds = text.split(".")[0].split(":")[2]
            minutes = text.split(":")[1]
            hours = text.split(":")[0]

        if dots == 1:
            miliseconds = text.split(".")[1]
        else:
            miliseconds = "00"

        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        milliseconds = int(miliseconds)

        total_time = (hours * 3600000) + (minutes * 60000) + (seconds * 1000) + (milliseconds * 10)

        return total_time

if __name__ == "__main__":

    config_dir = Path(user_config_dir("crono", roaming=True))
    config_dir.mkdir(parents=True, exist_ok=True)

    save_path = config_dir / "save.txt"

    with open(save_path, "+a") as f:
        f.seek(0)
        last_time = clean_newline(f.readline())
        last_mode = clean_newline(f.readline())
        last_timer_start = clean_newline(f.readline())
        
    App(config_dir, last_time, last_mode, last_timer_start).run()
