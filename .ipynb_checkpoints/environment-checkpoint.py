from mss import mss
import time
from PIL import Image
from collections import deque
from logger import Logger

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from action_space import ActionSpace

# Helper libraries
import numpy as np
import datetime


class Environment:
    def __init__(self):
        self.url = 'http://www.trex-game.skipser.com/'
        self.capture_width = 500
        self.capture_height = 325

        self.sct = mss()
        self.bbox = {'top': 345, 'left': 120, 'width': 580, 'height': 65}
        self.terminal_bbox = {'top': 325, 'left': 310, 'width': 1, 'height': 1}
        self.game_over_sprite = Image.open('assets/G_game_over.png')

        self.action_space = ActionSpace()
        self.actions = self.action_space.actions

        self.state = None
        self.frame_history = deque(maxlen=4)

        self.logger = Logger()

    def render(self):
        opts = Options()
        opts.add_argument(f"--width={self.capture_width+300}")
        opts.add_argument(f"--height={(self.capture_height+500)}")

        driver = webdriver.Firefox(executable_path='C:/Users/ryano/Downloads/geckodriver-v0.27.0-win64/geckodriver',
                                   options=opts)
        driver.get(self.url)

    def step(self, action):

        self.actions[action].act()
        self.frame_history.append(self._grab_sct())
        next_state = self._update_state()
        terminal = self._is_terminal()

        if not terminal:
            reward = 0.01
        else:
            reward = -1

        return next_state, reward, terminal

    def reset(self):
        time.sleep(1)
        self.action_space.space.act()
        self.reset_frame_history()
        self.state = self._update_state()
        time.sleep(2.5)

    def reset_frame_history(self):
        for i in range(4):
            self.frame_history.append(self._grab_sct())

    def _update_state(self):
        return np.stack(self.frame_history).reshape(1, 32, 290, 4)

    def _grab_sct(self):
        sct_img = self.sct.grab(self.bbox)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX").convert('L')

        (width, height) = (img.width // 4, img.height // 4)
        img = img.resize((width, height))
        img_np = np.array(img) / 255.0
        return np.expand_dims(img_np, axis=0)

    def _is_terminal(self):
        sct_img = self.sct.grab(self.terminal_bbox)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX").convert('L')
        return (np.array(self.game_over_sprite) == np.array(img)).all()

    def init_game(self):
        resp = input('enter "y" to start training: ')
        if resp == 'y':
            self.render()
        else:
            exit()

    def run(self, e, agent, batch_size, log_fn):

        self.reset()
        batch_loader = []

        for step in range(10000000):

            action = agent.choose_action(self.state)
            next_state, reward, terminal = self.step(action)
            batch_loader.append([self.state, action, reward, next_state, terminal])
            self.state = next_state

            if terminal:

                agent.batch_store(batch_loader)
                if (agent.memory.length > agent.pretraining_steps) or (agent.memory.memory_size == agent.memory.length):
                    agent.replay(batch_size, epoch_steps=step)

                if e % 20 == 0:
                    agent.save_memory(agent.save_memory_fp)

                run_time = datetime.datetime.now() - agent.start_time
                self.logger.log(log_fn, e, step, agent.total_steps, run_time, agent.epsilon, verbose=True)

                break

    def demo(self, agent):

        agent.epsilon = 0
        agent.epsilon_min = 0

        self.reset()
        for step in range(10000000):
            action = agent.choose_action(self.state)
            next_state, reward, terminal = self.step(action)
            self.state = next_state
            if terminal:
                break
