import os
import sys
import urllib
import pydub
import speech_recognition as sr
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import random
import time
from datetime import datetime
import json
import stem.process
from stem import Signal
from stem.control import Controller
import stat
import urllib.request
import zipfile
from sys import platform
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC



class ChromedriverDownloader:
    __instance = None

    def __init__(self):
        if not ChromedriverDownloader.__instance:
            self.url = 'https://chromedriver.chromium.org/downloads'
            self.base_driver_url = 'https://chromedriver.storage.googleapis.com'
            self.file_name = 'chromedriver_' + self.get_platform_filename()
            self.pattern = r'https://.*?path=(\d+\.\d+\.\d+\.\d+)'
            self.webdriver_folder_name = 'webdriver'

            try:
                os.mkdir(self.webdriver_folder_name)
            except FileExistsError:
                pass

            self.all_match = None
            self.stream = None
            self.content = None
            self.app_path = None
            self.chromedriver_path = None
            self.file_path = None
        else:
            print("Instance already created:", self.getInstance())

    @classmethod
    def getInstance(cls):
        if not cls.__instance:
            cls.__instance = ChromedriverDownloader()
        return cls.__instance

    @staticmethod
    def get_platform_filename():
        filename = ''
        is_64bits = sys.maxsize > 2 ** 32
        if platform == 'linux' or platform == 'linux2':
            filename += 'linux'
            filename += '64' if is_64bits else '32'
        elif platform == 'darwin':
            filename += 'mac64'
        elif platform == 'win32':
            filename += 'win32'
        filename += '.zip'
        return filename

    def get_driver(self):
        self.parse()
        if self.all_match:
            version = self.all_match[1]
            self.driver_url = '/'.join((self.base_driver_url,
                                       version, self.file_name))
            self.file_download()
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.normpath(os.path.join(
                    self.app_path, self.webdriver_folder_name)))
            st = os.stat(self.chromedriver_path)
            os.chmod(self.chromedriver_path, st.st_mode | stat.S_IEXEC)
            os.remove(self.file_path)
            return True

    def parse(self):
        self.stream = urllib.request.urlopen(self.url)
        self.content = self.stream.read().decode('utf8')
        self.all_match = re.findall(self.pattern, self.content)

    def file_download(self):
        self.app_path = os.path.dirname(os.path.realpath(__file__))
        self.chromedriver_path = os.path.normpath(os.path.join(
            self.app_path, self.webdriver_folder_name, 'chromedriver.exe'))
        self.file_path = os.path.normpath(os.path.join(
            self.app_path, self.webdriver_folder_name, self.file_name))
        urllib.request.urlretrieve(self.driver_url, self.file_path)


class ReCaptchaSolver:
    __instance = None
    USER_AGENT_LIST = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    ]

    def __init__(self):
        if not ReCaptchaSolver.__instance:
            # downloader = ChromedriverDownloader().get_driver()
            chrome_options = webdriver.ChromeOptions()
            path_to_chromedriver = os.path.normpath(
                os.path.join(
                    os.getcwd(), ChromedriverDownloader().webdriver_folder_name, "chromedriver.exe"
                )
            )
            user_agent = random.choice(ReCaptchaSolver.USER_AGENT_LIST)
            chrome_options.add_argument(f"user-agent={user_agent}")
            self.driver = webdriver.Chrome(executable_path=path_to_chromedriver,options=chrome_options)
            self.recaptcha_challenge_frame = None

            self.solve()
        else:
            print("Instance already created:", self.getInstance())

    @classmethod
    def getInstance(cls):
        if not cls.__instance:
            cls.__instance = ReCaptchaSolver()
        return cls.__instance

    def delay(self, waiting_time=4):
        self.driver.implicitly_wait(waiting_time)

    def solve(self, url="https://www.google.com/recaptcha/api2/demo"):
        self.driver.get(url)
        self.find_ReCaptcha()
        self.audio_challenge_start()
        self.get_wav()
        self.recognition()
        self.enter_key_and_pass()

    def find_ReCaptcha(self):
        time.sleep(3)
        frames = self.driver.find_elements_by_tag_name("iframe")
        recaptcha_control_frame = None
        self.recaptcha_challenge_frame = None
        for index, frame in enumerate(frames):
            if re.search('reCAPTCHA', frame.get_attribute("title")):
                recaptcha_control_frame = frame
                
            if re.search('recaptcha challenge', frame.get_attribute("title")) or re.search('текущую проверку reCAPTCHA можно пройти в течение ещё двух минут', frame.get_attribute("title")):
                self.recaptcha_challenge_frame = frame
                
        if not (recaptcha_control_frame and self.recaptcha_challenge_frame):
            print("[ERR] Unable to find recaptcha. Abort solver.")
            sys.exit()
        self.delay()
        self.switch_and_click(recaptcha_control_frame)

    def switch_and_click(self, recaptcha_control_frame):
        WebDriverWait(self.driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[src^='https://www.google.com/recaptcha/api2/anchor']")))
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.recaptcha-checkbox-border"))).click()
        self.delay()
    
    def audio_challenge_start(self):
        self.driver.switch_to.default_content()
        frames = self.driver.find_elements_by_tag_name("iframe")
        self.driver.switch_to.frame(self.recaptcha_challenge_frame)
        time.sleep(10)
        self.driver.find_element_by_id("recaptcha-audio-button").click()
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(self.recaptcha_challenge_frame)
        self.delay()
    
    def get_wav(self):
        src = self.driver.find_element_by_id("audio-source").get_attribute("src")
        print(f"[INFO] Audio src: {src}")
    
        path_to_mp3 = os.path.normpath(os.path.join(os.getcwd(), "sample.mp3"))
        path_to_wav = os.path.normpath(os.path.join(os.getcwd(), "sample.wav"))
  
        urllib.request.urlretrieve(src, path_to_mp3)
        sound = pydub.AudioSegment.from_mp3(path_to_mp3)
        sound.export(path_to_wav, format="wav")
        self.sample_audio = sr.AudioFile(path_to_wav)
    
    def recognition(self):
        r = sr.Recognizer()
        with self.sample_audio as source:
            audio = r.record(source)
        self.key = r.recognize_google(audio)


    def enter_key_and_pass(self):
        self.driver.find_element_by_id("audio-response").send_keys(self.key.lower())
        self.driver.find_element_by_id("audio-response").send_keys(Keys.ENTER)
        time.sleep(5)
        self.driver.switch_to.default_content()
        time.sleep(5)
        self.driver.find_element_by_id("recaptcha-demo-submit").click()