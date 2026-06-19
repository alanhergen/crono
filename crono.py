#!/usr/bin/env python3

import pygame, os, sys
from pathlib import Path
from platformdirs import user_config_dir

def resource_path(relative_path):
    return os.path.join(os.path.abspath("."), relative_path)

class App:
    def __init__(self, config_path="", last_sesion=""):
        
        pygame.init()
        self.title = "Crono"
        pygame.display.set_caption(self.title)

        self.path_icon = resource_path("data/images/icon.png")
        self.icon = pygame.image.load(self.path_icon)
        pygame.display.set_icon(self.icon)

        self.config_path = config_path

        self.save_path = self.config_path / "save.txt"

        self.w, self.h = 35 * 8 + 15 * 3 + 5, 50
        self.screen = pygame.display.set_mode((self.w, self.h))

        self.clock = pygame.time.Clock()
        self.running = True

        self.bg_color = "black"
        self.green = "#26a269"
        self.blue = "#12488b"
        self.gray = "#808080"
        self.white = "#ffffff"
        self.text_color = self.gray

        self.fonts = {}
        self.path_font = resource_path("data/fonts/lemonmilk.otf")
        self.font = self.select_font(48)
        self.font_mini = self.select_font(36)

        self.type_message = self.select_font(36).render("Type here", True, self.white)
        self.error_message = self.select_font(36).render("Invalid format", True, self.white)
        self.sure_message = self.select_font(20).render("Are you sure to restart?", True, self.white)

        self.error_time = 0
        self.error_time_total = 60

        self.sure_restart = False
        self.sure_restart_timeout_total = 5
        self.sure_restart_timeout = self.sure_restart_timeout_total

        self.time_input = ""
        self.time = int(last_sesion) if last_sesion != "" else 0

        self.pause = True
        self.finish = False
        self.editor = False

        self.milliseconds_allowed = True

    def select_font(self, size):

        if not size in self.fonts.keys():     
            self.fonts[size] = pygame.font.Font(self.path_font, size)

        return self.fonts[size]

    def run(self):

        while self.running:
            for event in pygame.event.get():

                # clicked the close button
                if event.type == pygame.QUIT:
                    
                    with open(self.save_path, 'w') as f:
                        f.write(str(self.time))
                    self.running = False

                # keyboard events
                if event.type == pygame.KEYDOWN:
                    
                    # escape - exit
                    if event.key == pygame.K_ESCAPE:
                        # self.running = False
                        pass

                    # m - show miliseconds
                    if event.key == pygame.K_m:
                        self.milliseconds_allowed = not self.milliseconds_allowed 

                    # enter - start/finish
                    if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:

                        if not (self.sure_restart or self.editor):
                            
                            if not self.pause:
                                self.finish = True
                                self.pause = True

                            elif self.pause and not self.finish:
                                self.pause = False

                    # space - pause/unpause
                    if event.key == pygame.K_SPACE and not self.sure_restart:
                        self.pause = not self.pause
                        self.finish = False
                        self.editor = False

                        if self.pause:
                            self.text_color = self.gray
                        else:
                            self.text_color = self.green

                    # r - reset
                    if event.key == pygame.K_r and not self.editor:
                        self.sure_restart = True
                        self.pause = True
                        self.finish = False

                    # e - edit
                    if event.key == pygame.K_e:
                        self.time_before_edit = self.time
                        self.editor = not self.editor
                        self.pause = True
                        self.finish = False

                    # handle time editing
                    if self.editor:

                        # escape - return to previous state
                        if event.key == pygame.K_ESCAPE:
                            self.time = self.time_before_edit
                            self.editor = False

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
                                self.time = self.make_time(self.time_input)
                                self.editor = False
                                self.time_input = ""

                            else:
                                self.error_time = self.error_time_total

                    # are you sure to restart?
                    if self.sure_restart:

                        # r again - restart
                        if event.key == pygame.K_r and not self.sure_restart_timeout:
                            self.time = 0
                            self.sure_restart = False
                            self.sure_restart_timeout = self.sure_restart_timeout_total

                        # [enter, space, r] - restart
                        if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER]:
                            self.time = 0
                            self.sure_restart = False
                            self.sure_restart_timeout = self.sure_restart_timeout_total

                        # escape - cancel restart
                        if event.key == pygame.K_ESCAPE:
                            self.sure_restart = False

            self.update()
            self.render()

        pygame.quit()

    def update(self):
        self.screen.fill(self.green)
        self.clock.tick(60)

        if not self.pause:
            self.time += self.clock.get_time()

        if self.pause:
            self.text_color = self.gray
        else:
            self.text_color = self.green

        if self.finish:
            self.text_color = self.blue

        if self.error_time:
            self.error_time = max(0, self.error_time - 1)
            if self.error_time <= 0:
                self.error_time = 0
        
        if self.sure_restart:
            self.sure_restart_timeout = max(0, self.sure_restart_timeout - 1)

    def render(self):

        self.screen.fill(self.bg_color)

        self.hours = (self.time // 3600000)
        self.minutes = (self.time // 60000) % 60
        self.seconds = (self.time // 1000) % 60
        self.milliseconds = self.time % 1000 // 10

        if self.editor:
            
            if self.error_time:
                self.screen.blit(self.error_message, ((self.w - self.error_message.get_width()) // 2, (self.h - self.error_message.get_height()) // 2))

            elif self.time_input == "":
                self.screen.blit(self.type_message, ((self.w - self.type_message.get_width()) // 2, (self.h - self.type_message.get_height()) // 2))
            
            else:
                text_input = self.font.render(self.time_input, True, self.white)
                self.screen.blit(text_input, ((self.w - text_input.get_width()) // 2, (self.h - text_input.get_height()) // 2))
                
        elif self.sure_restart:
                self.screen.blit(self.sure_message, ((self.w - self.sure_message.get_width()) // 2, (self.h - self.sure_message.get_height()) // 2))
        else:
            
            text = f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}.{self.milliseconds:02}"
            self.render_time(text)

        pygame.display.flip()

    def render_time(self, text):

        if self.hours > 999:
            self.font = self.select_font(40)
        elif self.hours > 99:
            self.font = self.select_font(44)
        else:
            self.font = self.select_font(48)

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

        zero_surface = self.font.render("0", True, self.text_color)
        zero_mini_surface = self.font_mini.render("0", True, self.text_color)
        one_surface = self.font.render("1", True, self.text_color)
        one_mini_surface = self.font_mini.render("1", True, self.text_color)
        colon_surface = self.font.render(":", True, self.text_color)

        zero_offset, char_big_h = zero_surface.get_size()
        zero_mini_offset, char_mini_h = zero_mini_surface.get_size()
        char_mini_h += 2
        one_offset = one_surface.get_width()
        one_mini_offset = one_mini_surface.get_width()
        colon_offset = colon_surface.get_width()

        hide_miliseconds = zero_mini_offset * 2 + colon_offset

        offset = 0
        idx = 0
        for char in reversed(text):

            if char == ':':
                char_w = colon_offset
            elif char == '.':
                char_w = colon_offset + 4
            else:
                char_w = zero_offset

            if idx >= 2:
                char_surface = self.font.render(char, True, self.text_color)
                char_h = char_big_h
            else:
                char_w, char_h = zero_mini_offset, char_mini_h
                char_surface = self.font_mini.render(char, True, self.text_color)

            pos = (self.w - char_w - offset, (self.h + char_big_h) // 2 - char_h)

            if char == '1':
                if idx > 2:
                    pos = (pos[0] + one_offset // 2, pos[1])
                else: 
                    pos = (pos[0] + one_mini_offset // 2, pos[1])

            if not self.milliseconds_allowed:
                pos = (pos[0] + hide_miliseconds, pos[1])

            offset += char_w

            if show:
                self.screen.blit(char_surface, pos)
            show = max(0, show-1)

            idx += 1

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
        data = f.read()

    App(config_dir, data).run()
