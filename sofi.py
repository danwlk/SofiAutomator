import pyautogui
import time
import re
import random
from PIL import ImageGrab
import cv2
import numpy as np
import json
import os
import pytesseract
import sys
import threading

# Configure Tesseract OCR path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class SofiBot:
    def __init__(self):
        self.running = False
        self.config_file = "sofi_config.json"
        
        print()
        print("="*25)
        print("| SOFI DISCORD CARD BOT |")
        print("="*25)
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                saved_config = json.load(f)
            
            self.delays = saved_config.get('delays', {})
            if not self.delays:
                print("⚠️ No delays configuration found in JSON file")
                return False
            
            self.chat_area = saved_config.get('chat_area')
            self.input_area = saved_config.get('input_area')
            self.username = saved_config.get('username')
            
            if self.chat_area and self.input_area and self.username:
                print("✅ Loaded saved configuration!")
                print(f"Delays config: {self.delays}")
                print(f"Chat area: {self.chat_area}")
                print(f"Input area: {self.input_area}")
                print(f"Username: {self.username}")
                return True
            else:
                print("\n❌ No configuration found!")
                print("You need to run the configuration first.")
                return False
        else:
            default_config = {
                'delays': {
                    'check_interval': 2,
                    'click_delay': [1, 5]
                },
                'chat_area': None,
                'input_area': None,
                'username': None
            }
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print("\n✅ Created default configuration file!")
            self.delays = default_config['delays']
            return False
    
    def save_config(self):
        try:
            config_data = {
                'delays': self.delays,
                'chat_area': self.chat_area,
                'input_area': self.input_area,
                'username': self.username
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            print("✅ Configuration saved!")
            
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def run_configuration(self):
        print("\n" + "="*17)
        print("| CONFIGURATION |")
        print("="*17)
        print("\nInstructions:")
        print("1. Make sure Discord is open")
        print("2. Navigate to the chat where the card game happens")
        print("3. Follow the prompts to capture coordinates")
        print("4. Press Ctrl+C to stop at any time")
        
        input("\nPress Enter when Discord is ready...")
        
        try:
            print("\n1. CHAT AREA COORDINATES")
            print("Move your mouse to the TOP-LEFT corner of the chat area (where messages appear)")
            input("Press Enter when ready...")
            chat_x1, chat_y1 = pyautogui.position()
            print(f"Top-left: ({chat_x1}, {chat_y1})")
            
            print("\nNow move your mouse to the BOTTOM-RIGHT corner of the chat area")
            input("Press Enter when ready...")
            chat_x2, chat_y2 = pyautogui.position()
            print(f"Bottom-right: ({chat_x2}, {chat_y2})")
            
            chat_width = chat_x2 - chat_x1
            chat_height = chat_y2 - chat_y1
            self.chat_area = (chat_x1, chat_y1, chat_width, chat_height)
            
            print("\n2. INPUT AREA COORDINATES")
            print("Move your mouse to where you type messages (the input box)")
            input("Press Enter when ready...")
            input_x, input_y = pyautogui.position()
            self.input_area = (input_x, input_y)
            print(f"Input area: ({input_x}, {input_y})")
            
            print("\n3. USERNAME CONFIGURATION")
            print("Enter your Discord username (without the @ symbol)")
            print("This ensures the bot only responds when Nori pings you specifically.")
            
            while True:
                username = input("Username: ").strip()
                if username:
                    self.username = username
                    print(f"Username set to: {username}")
                    break
                else:
                    print("Username cannot be empty. Please enter a valid username.")

            self.save_config()
            print("Your coordinates have been saved and will be loaded automatically next time.\n")
        except KeyboardInterrupt:
            print("\nConfiguration stopped by user.")
            exit(1)
    
    def take_screenshot(self, region=None):
        try:
            if region:
                x, y, w, h = region
                if w <= 0 or h <= 0:
                    print(f"Warning: Invalid region dimensions: {w}x{h}")
                    return None
                screenshot = ImageGrab.grab(bbox=(x, y, x+w, y+h), all_screens=True)
            else:
                screenshot = ImageGrab.grab(all_screens=True)
            return screenshot
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None
    
    def extract_text_from_image(self, image):
        try:
            print(f"🔧 Processing image: {image.size} pixels")
            
            text = pytesseract.image_to_string(image, config='--psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,!?@#$%^&*()_+-=[]{}|;:,.<>?•')
            return text.strip()
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def detect_buttons(self):
        print("🔍 Detecting button positions from screenshot...")

        screenshot = self.take_screenshot(region=self.chat_area)
        img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        button_positions = []
        chat_x, chat_y = self.chat_area[0], self.chat_area[1]
        templates = []
        for i in range(1, 4):
            template_path = f'images/button{i}.png'
            template = cv2.imread(template_path)
            if template is not None:
                templates.append((i, template))
            else:
                print(f"❌ Failed to load template for button {i}")

        for button_num, template in templates:
            result = cv2.matchTemplate(img_cv, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            h, w = template.shape[:2]
            center_x = max_loc[0] + w//2 + chat_x
            center_y = max_loc[1] + h//2 + chat_y
            print(f"Found button {button_num} at ({center_x}, {center_y}) with confidence {max_val:.3f}")
            if max_val > 0.5: 
                button_positions.append((button_num, center_x, center_y, max_val))
            else:
                print(f"❌ Button {button_num} confidence too low: {max_val:.3f}")
        button_positions.sort(key=lambda x: x[0])
        coordinates = [(x, y) for _, x, y, _ in button_positions]
        
        if len(coordinates) == 3:
            print(f"✅ Found all 3 buttons: {coordinates}\n")
            print("🔍 Checking for shell buttons...")
            shell_index, updated_coordinates = self.detect_shell_button(coordinates)
            if shell_index is not None:
                print(f"✅ Updated button coordinates: {updated_coordinates}\n")
            else:
                print("✅ No shell buttons found\n")
            return updated_coordinates, shell_index
        else:
            print(f"❌ Found {len(coordinates)} buttons, expected 3")
            return []
            
    def validate_button_spacing(self, button_positions):
        if len(button_positions) != 3:
            return False
        
        x_positions = [pos[0] for pos in button_positions]
        spacing1 = x_positions[1] - x_positions[0]
        spacing2 = x_positions[2] - x_positions[1]
        
        spacing_tolerance = 50
        if abs(spacing1 - spacing2) > spacing_tolerance:
            print(f"Button spacing inconsistent: {spacing1} vs {spacing2}")
            return False
        
        y_positions = [pos[1] for pos in button_positions]
        y_variance = max(y_positions) - min(y_positions)
        if y_variance > 50:
            print(f"Button Y positions too varied: {y_variance}")
            return False
        
        return True
    
    def coordinates_similar(self, pos1, pos2, tolerance=5):
        return abs(pos1[0] - pos2[0]) <= tolerance
    
    def detect_shell_button(self, button_positions):
        if self.coordinates_similar(button_positions[1], button_positions[2]):
            shell_index = 2
            spacing = abs(button_positions[1][0] - button_positions[0][0])
            missing_x = button_positions[1][0] + spacing
            missing_y = button_positions[1][1]
            missing_button = (missing_x, missing_y)
            print(f"Shell button detected at position 3 (index {shell_index})")
            return shell_index, [button_positions[0], button_positions[1], missing_button]
        
        elif self.coordinates_similar(button_positions[0], button_positions[1]):
            shell_index = 0
            spacing = abs(button_positions[2][0] - button_positions[1][0])
            missing_x = button_positions[1][0] - spacing
            missing_y = button_positions[1][1]
            missing_button = (missing_x, missing_y)
            print(f"Shell button detected at position 1 (index {shell_index})")
            return shell_index, [missing_button, button_positions[1], button_positions[2]]
        
        return None, button_positions
    
    def wait_for_nori_ping(self):
        print(f"Waiting for Nori's ping @{self.username}...")

        while self.running:
            screenshot = self.loading_animation("Taking screenshot...", "Screenshot taken successfully", lambda: self.take_screenshot(region=self.chat_area))
            if not screenshot:
                print("❌ Failed to take screenshot")
                continue
            text = self.extract_text_from_image(screenshot)
            
            patterns = [
                f"@{self.username}.*you can now drop",
                f"@{self.username}.*you can now drop!",
                f"@{self.username}.*youcannowdrop",
                f"@{self.username}.*youcannowdrop!",
            ]
            for pattern in patterns:
                if re.search(pattern, text.lower()):
                    print(f"✅ Nori's ping detected!")
                    return True
            print(f"❌ Nori has not pinged...\n")
            
            time.sleep(self.delays['check_interval'])
        
        return False
    
    def send_chat(self, message):
        def send_operation():
            input_x, input_y = self.input_area
            pyautogui.click(input_x, input_y)
            time.sleep(0.5)
            
            pyautogui.typewrite(message, interval=0.1)
            time.sleep(0.5)
            
            pyautogui.press('enter')
        self.loading_animation(f"Sending '{message}'...", f"'{message}' command sent!", send_operation)
    
    def pause_10_seconds(self):
        self.loading_animation("Pausing for 10 seconds...", "10-second pause completed", lambda: time.sleep(10))
    
    def loading_animation(self, loading_text, completed_text, operation_func):
        animation_chars = ['-', '\\', '|', '/']
        current_char = 0
        stop_animation = threading.Event()
        
        def animate():
            nonlocal current_char
            while not stop_animation.is_set():
                sys.stdout.write(f'\r{animation_chars[current_char]} {loading_text}')
                sys.stdout.flush()
                current_char = (current_char + 1) % len(animation_chars)
                time.sleep(0.1)
        animation_thread = threading.Thread(target=animate)
        animation_thread.start()
        try:
            result = operation_func()
        except Exception as e:
            stop_animation.set()
            animation_thread.join()
            sys.stdout.write('\r' + ' ' * (len(loading_text) + 2) + '\r')
            print(f"❌ Error: {e}")
            return None

        stop_animation.set()
        animation_thread.join()
        sys.stdout.write('\r' + ' ' * (len(loading_text) + 2) + '\r')
        print(f"✅ {completed_text}")
        
        return result
    
    def get_heart_counts(self):
        print("Reading heart counts...")
        
        screenshot = self.take_screenshot(region=self.chat_area)
        if not screenshot:
            return []
        
        text = self.extract_text_from_image(screenshot)
        lines = text.split('\n')
        card_lines = []
        for line_num in [1, 2, 3]:
            found_line = None
            for line in lines:
                if re.match(f'^{line_num}[1\\]]', line.strip()):
                    found_line = line
                    break
            if found_line is None:
                print(f"Could not find line {line_num}1 or {line_num}]")
                return []
            card_lines.append(found_line)
                    
        heart_patterns = [
            r'@o',  # Handle OCR misreading 0 as o
            r'@0',  # Handle @0 pattern
            r'@\)o',  # Handle OCR misreading @)0 as @)o
            r'@(\d+)',  # @number pattern (when OCR works correctly)
            r'@\)(\d+)',  # @)number pattern
            r'@[^_](\d+)',  # @(any character)number pattern
        ]
        
        heart_counts = []
        for line in card_lines:
            line_heart_count = None
            for i, pattern in enumerate(heart_patterns):
                matches = re.findall(pattern, line, re.IGNORECASE)
                if matches:
                    print(f"{line} matched pattern {i+1}: {matches}")
                    if i == 0:  # @o pattern
                        line_heart_count = 0
                    elif i == 1:  # @0 pattern
                        line_heart_count = 0
                    elif i == 2:  # @)o pattern
                        line_heart_count = 0
                    else:
                        if isinstance(matches[0], tuple):
                            line_heart_count = int(matches[0][0])
                        else:
                            line_heart_count = int(matches[0])
                    break
            
            if line_heart_count is not None:
                heart_counts.append(line_heart_count)
            else:
                print(f"{line} NO PATTERN MATCHED")
                heart_counts.append(0)
        
        print(f"\n\033[92mFinal heart array: {heart_counts}\033[0m\n")
        return heart_counts
    
    def click_best_card(self, heart_counts):
        if not heart_counts:
            print("No heart counts found, skipping card selection.")
            return
        
        buttons, shell_index = self.detect_buttons()
        
        if len(buttons) == 0:
            print("❌ Could not find all buttons, skipping cycle.")
            return
        
        if shell_index is None:
            best_index = heart_counts.index(max(heart_counts))
            best_count = heart_counts[best_index]
            print(f"\033[92mBest card: #{best_index + 1} with {best_count} hearts\033[0m\n")

            delay = random.uniform(*self.delays['click_delay'])
            time.sleep(delay)
            
            button_coords = buttons[best_index]
            pyautogui.click(button_coords[0], button_coords[1])
            print(f"✅ Clicked button {best_index + 1} at ({button_coords[0]}, {button_coords[1]})")
            self.pause_10_seconds()
            self.send_chat('sv')
            self.pause_10_seconds()
        else:
            non_shell_heart_counts = [count for i, count in enumerate(heart_counts) if i != shell_index]
            non_shell_indices = [i for i in range(len(heart_counts)) if i != shell_index]
            best_non_shell_index = non_shell_heart_counts.index(max(non_shell_heart_counts))
            best_count = non_shell_heart_counts[best_non_shell_index]
            actual_best_index = non_shell_indices[best_non_shell_index]
            print(f"\033[92mBest non-shell card: #{actual_best_index + 1} with {best_count} hearts\033[0m\n")
            delay = random.uniform(*self.delays['click_delay'])
            time.sleep(delay)
            button_coords = buttons[actual_best_index]
            pyautogui.click(button_coords[0], button_coords[1])
            print(f"✅ Clicked best non-shell button {actual_best_index + 1} at ({button_coords[0]}, {button_coords[1]})")
            
            time.sleep(1)
            shell_coords = buttons[shell_index]
            pyautogui.click(shell_coords[0], shell_coords[1])
            print(f"✅ Clicked shell button {shell_index + 1} at ({shell_coords[0]}, {shell_coords[1]})")
            
            self.pause_10_seconds()
            self.send_chat('sv')
            self.pause_10_seconds()
    
    def run_automation_cycle(self):
        print("\n" + "="*34)
        print("| Starting SOFI automation cycle |")
        print("="*34)
        
        if not self.wait_for_nori_ping():
            return False
        
        self.send_chat('sd')
        self.loading_animation("Waiting for SOFI and Nori responses...", "Responses received\n", lambda: time.sleep(2))
        
        heart_counts = self.get_heart_counts()
        self.click_best_card(heart_counts)
        
        print("\nCycle completed!")
        return True
    
    def start(self):
        print("Starting SOFI Discord Card Bot...")
        print("Press Ctrl+C to stop")
        
        self.running = True
        
        try:
            while self.running:
                self.run_automation_cycle()
                print("Waiting for next cycle...")
                
        except KeyboardInterrupt:
            print("\nBot stopped by user.")
            self.running = False
    
    def stop(self):
        self.running = False
        print("Bot stopped.")

if __name__ == "__main__":
    bot = SofiBot()
    
    if bot.load_config():
        print("\nOptions:")
        print("1. Start automation")
        print("2. Run configuration")
        
        while True:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            
            if choice == "1":
                bot.start()
                break
            elif choice == "2":
                bot.run_configuration()
                bot.start()
                break
            else:
                print("Invalid choice. Please enter 1 or 2.\n")
    else:
        print("\nOptions:")
        print("1. Run configuration (required)")
        print("2. Exit")
        
        while True:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            
            if choice == "1":
                bot.run_configuration()
                bot.start()
                break
            elif choice == "2":
                print("Run the script again when ready to configure.")
                bot.stop()
                break
            else:
                print("Invalid choice. Please enter 1 or 2.\n")
