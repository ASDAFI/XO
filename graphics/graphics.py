import numpy as np
import matplotlib.image as img
import matplotlib.pyplot as plt
import os
import glob
import random
import json
import cv2
import sys
import moviepy.video.io.ImageSequenceClip
import easygui


class paths:
    current_path = os.path.dirname(os.path.abspath(__file__)) 
    x = f"{current_path}\\assets\\logos\\X.png"
    o = f"{current_path}\\assets\\logos\\O.png"
    table = f"{current_path}\\assets\\logos\\grid.png"
    wallpaper = f"{current_path}\\assets\\wallpapers"

class assets:
    def load(path : str) -> np.array:
        photo = np.array(img.imread(path))
        return photo
    
    def load_config(path : str) -> dict:
        with open(path) as f:
            data = json.load(f)
        return data

    def random_wallpaper(path : str) -> list:
        items = glob.glob(f"{paths.wallpaper}\\*.jpg")

        item = random.choice(items)
        item_name = item.split('\\')[-1].split('.')[0]

        photo = assets.load(item)
        config = assets.load_config(f"{paths.wallpaper}\\{item_name}.json")

        result = [photo, config]
        
        return result

class tools:
    def terminal_input() -> dict:
        
        keys = sys.argv[1 : : 2]
        values = sys.argv[2 : : 2] 

        inputs = dict(zip(keys, values))
        return inputs
    
    def setup_dir() -> str:

        out_dir = f"{paths.current_path}\\out"

        n = 1

        if((not os.path.exists(out_dir)) or (not os.path.isdir(out_dir))):
            path = f"{out_dir}\\{1}"
            os.mkdir(out_dir)
            
            
            
        
        else:
            
            while True:
                path = f"{out_dir}\\{n}"
                if((not os.path.exists(path)) or (not os.path.isdir(path))):
                    break

                n += 1
            
        os.mkdir(path)
        
        return path

    def clear_cache(dir : str) -> None:
        for file in glob.glob(f"{dir}/cache/*"):
            os.remove(file)
        
        os.rmdir(f"{dir}/cache")

class images:
    def put_image(bg, image, position):
        bg = bg.copy()

        a = image.shape[0] // 2
        b = image.shape[1] // 2

        for i in range(-a,  a):
            for j in range(-b, b):

                x = a + i
                y = b + j

                if(image[x][y][3] != 0):
                    bg[x + position[0]][y + position[1]] = image[x][y][:-1]
    
        return bg
    
    def create_template(wallpaper : np.array, table : np.array, players : dict, config : dict) -> np.array:
        template = images.put_image(wallpaper, table, config["table"])

        template = cv2.line(np.copy(template), config["line1"][0], config["line1"][1], config["line_color"], config["thickness"])
        template = cv2.line(np.copy(template), config["line2"][0], config["line2"][1], config["line_color"], config["thickness"])

        template = cv2.putText(img = np.copy(template), text=f"X : {players['X']}", org=config["X"],fontFace=config["L_font"][0], fontScale=config["L_font"][1], color=config["X_color"], thickness=config["thickness"])
        template = cv2.putText(img = np.copy(template), text=f"O : {players['O']}", org=config["O"],fontFace=config["L_font"][0], fontScale=config["L_font"][1], color=config["O_color"], thickness=config["thickness"])
        
        return template

    def add_state(template : np.array, state : dict, config : dict) -> np.array:
        result = cv2.putText(img = np.copy(template), text=f"Turn : {state['turn']}", org=config["turn"],fontFace=config["R_font"][0], fontScale=config["R_font"][1], color=config["R_color"], thickness=config["thickness"])
        if(state["turn"] != 0):

            result = cv2.putText(img = np.copy(result), text=f"Player: {state['player']}", org=config["player"],fontFace=config["R_font"][0], fontScale=config["R_font"][1], color=config["R_color"], thickness=config["thickness"])
            result = cv2.putText(img = np.copy(result), text=f"Choice: {state['choice']}", org=config["choice"],fontFace=config["R_font"][0], fontScale=config["R_font"][1], color=config["R_color"], thickness=config["thickness"])
        
        return result

    def add_winner(template : np.array, result : int, config : dict) -> np.array:
        if(result == 0):
            color = config["X_color"]
        elif(result == 1):
            color = config["O_color"]
        else:
            color = config["draw_color"]

        text = ["X Wins!", "O Wins!", "Draw!"][result]
        result = cv2.putText(img = np.copy(template), text=text, org=config["result"],fontFace=config["result_font"][0], fontScale=config["result_font"][1], color=color, thickness=config["thickness"])
        return result

    def save(photo : np.array, path : str) -> None:
        fig = plt.imshow(photo)
        plt.axis('off')
        plt.savefig(path, bbox_inches='tight',pad_inches = 0)
    
    def create_movie(dir : str, path : str):
        image_files = [file for file in glob.glob(f"{dir}/*.jpg")]
        image_files = image_files + [image_files[-1]] * 3
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=0.4)
        clip.write_videofile(path)
        os.system("cls")

class game:
    def play(game_config : dict, dir : str) -> None:
        x = assets.load(paths.x)
        o = assets.load(paths.o)
        table = assets.load(paths.table)

        wallpaper, config = assets.random_wallpaper(paths.wallpaper)
        
        symbols = [game_config["symbols"]["player1"], game_config["symbols"]["player2"]]
        names = ["player1", "player2"]
        players = dict(zip(symbols, names))


        template = images.create_template(wallpaper, table, players, config)
        view = images.add_state(template, {"turn" : 0}, config)
        
        try:
            os.mkdir(f"{dir}/cache")
        except:
            pass

        num = 0
        
        images.save(view, f"{dir}/cache/{num}.jpg")
        
        
        for turn in game_config["turns"]:
            num += 1

            state = {"turn" : turn["turn"], "player" : symbols[turn["action"]["player_num"] - 1], "choice" : None}

            if(state["player"] == "X"):
                logo = x
            else:
                logo = o

            if(turn["action"]["error"] == None):
                choice = str(turn["action"]["choice"])

                template = images.put_image(template, logo, config[str(choice)])
            else:
                choice = "Error"
            
            state["choice"] = choice
            view = images.add_state(template, state, config)

            images.save(view, f"{dir}/cache/{num}.jpg")
       
        num += 1
        view = images.add_winner(view, ["X" ,"O", "-"].index(game_config["winner"]["symbol"]), config)
        images.save(view, f"{dir}/cache/{num}.jpg")

        images.create_movie(f"{dir}/cache", f"{dir}/out.mp4")
        tools.clear_cache(dir)
         





def main():
    path = easygui.fileopenbox("Log file")
    game_config = assets.load_config(path)
    path = tools.setup_dir() 
    game.play(game_config, path)
    print("Output: ", f"{path}/out.mp4")
    input("\n\nPress Enter to exit...")
if(__name__ == "__main__"):
    main()
