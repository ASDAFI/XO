import sys
import os
import multiprocessing
import time
import psutil
import json
import random
import easygui


class system:
    ram = psutil.virtual_memory().total * 1e-6

    def get_memory_usage(pid : int) -> float:
        for proc in psutil.process_iter():
            if(proc.pid == pid):
                memory = proc.memory_percent() * system.ram
                return memory
        return -1.0

class flags:
    run_check = -493644956
    int_check = -3483045

class limits:
    preprocess = {"time" : 3, "memory" : 500}
    action = {"time" : 0.5, "memory" : 200}

class visualize:
    
    def runIn(function, inputs : tuple, output : multiprocessing.Value):
        result = function(*inputs)

        if(type(result) == int):
            output.value = result
        else:
            output.value = flags.int_check
    
    def runFunction(function, inputs : tuple, time_limit : int, memory_limit : int) -> dict:
        func_output = multiprocessing.Value('i',flags.run_check)
        output = {"error" : None, "output" : None, "time" : None, "details" : None}

        task = multiprocessing.Process(target = visualize.runIn, args = (function, inputs, func_output))
        task.start()

        pid = task.pid

        start_time = time.time()
        memory = system.get_memory_usage(pid)
        
        while((time.time() - start_time < time_limit) and (func_output.value == flags.run_check)):
            memory_usage = system.get_memory_usage(pid)  - memory
            if(memory_usage > memory_limit):
                task.terminate()

                output["error"] = "memory_limit"
                return output

        if(func_output.value == flags.run_check):
            task.terminate()
            
            output["error"] = "time_limit"
            return output
        
        time_exc = time.time() - start_time
        
        output["output"] = func_output.value
        output["time"] = time_exc
        
        return output

class player:
    def __init__(self, id : int, preprocess, action):
        self.id = id
        self.preprocess = preprocess
        self.action = action

        
class game:
    def win_check(grid : list) -> str:
        ### horizontal check
        for i in range(0, 9, 3):
            if(grid[i] == grid[i + 1] == grid[i + 2] != '-'):
                return grid[i]
        
        ### Vertical check
        for i in range(3):
            if(grid[i] == grid[i + 3] == grid[i + 6] != '-'):
                return grid[i]
        
        ### Diagonal check
        if(grid[0] == grid[4] == grid[8] != '-'):
            return grid[0]
        if(grid[2] == grid[4] == grid[6] != '-'):
            return grid[2]
        
        return '-'
    
    def draw_check(grid : list) -> bool:
        ### horizontal check
        for i in range(0, 9, 3):
            part = grid[i : i + 3]
            if('X' not in part or 'O' not in part):
                return False
        
        ### Vertical check
        for i in range(3):
            part = grid[i : i + 7 : 3]
            if('X' not in part or 'O' not in part):
                return False
        
        ### Diagonal check
        part = grid[0:9:4]
        if('X' not in part or 'O' not in part):
            return False
        part = grid[2 : 7 : 2]
        if('X' not in part or 'O' not in part):
            return False
        
        return True

    #play one game
    def play(players : list, symbols : list, path : str) -> dict:
        log = {
              "symbols" : {
                          "player1" : symbols[0],
                          "player2" : symbols[1]
                          },
              "preprocess" : {
                             "player1" : {
                                         "time" : None,
                                         "error" : None,
                                         "details" : None
                                         },
                             "player2" : {
                                         "time" : None,
                                         "error" : None,
                                         "details" : None
                                         }
                             },
              "turns" : [],
              "winner" : {
                         "player_num" : -1,
                         "symbol" : "-"
                         }
              }
        
        turn_log = {
                   "turn" : 0,
                   "grid" : [],
                   "action" : {
                              "player_num" : 0,
                              "choice" : -1,
                              "time" : None,
                              "error" : None,
                              "details" : None
                              }
                   }
        
        grid = ['-'] * 9
        turn = 1

        ### Preprocess

        for i in range(2):
            try:
                result = visualize.runFunction(
                                            function = players[i].preprocess,
                                            inputs = (symbols[i], ), 
                                            time_limit = limits.preprocess["time"],
                                            memory_limit = limits.preprocess["memory"])
                result.pop("output")

            except Exception as error:
                result = {
                        "time" : -1,
                        "error" : str(type(error)), 
                        "details" : str(error)
                        }
            
            log["preprocess"][f"player{i+1}"] = result
        
        ###

        ### Turns
        while((game.win_check(grid) == '-') and (game.draw_check(grid) == False) and (turn < 19)):
            current_turn = turn_log.copy()
            
            player_id = symbols.index(["O", "X"][turn % 2])
            player_symbol = symbols[player_id]

            action_log = {
                        "player_num" : player_id + 1,
                        "choice" : -1,
                        "time" : None,
                        "error" : None, 
                        "details" : None
                        }
            try:
                result = visualize.runFunction(
                                     function = players[player_id].action,
                                     inputs = (grid[:], player_symbol[:]),
                                     time_limit = limits.action["time"],
                                     memory_limit = limits.action["memory"]
                                     )
                

                if(result['error'] == None):
                    action_log["time"] = result["time"]

                    if(result["output"] == flags.int_check):
                        action_log["error"] = "wrong_type"
                        action_log["details"] = "action function should return an integer number."
                    
                    elif(result["output"] > 8 or result["output"] < 0):
                        action_log["error"] = "wrong_cell"
                        action_log["details"] = "cell number should be in [0,8]."
                        action_log["choice"] = result["output"]
                    
                    elif(grid[result["output"]] != "-"):
                        action_log["error"] = "chosen_cell"
                        action_log["details"] = "the cell is already taken."
                        action_log["choice"] = result["output"]
                    
                    else:
                        action_log["choice"] = result["output"]
                        grid[result["output"]] = player_symbol
                else:
                    action_log["error"] = result["error"]
                

            except Exception as error:
                result = {
                        "player_num" : player_id + 1,
                        "choice" : -1,
                        "time" : None,
                        "error" : str(type(error)), 
                        "details" : str(error)
                        }
            
            current_turn["turn"] = turn
            current_turn["grid"] = grid[:]
            current_turn["action"] = action_log
            log["turns"].append(current_turn)

            turn += 1
        
        ###

        ### Winner
        winner_symbol = game.win_check(grid)

        if(winner_symbol != '-'):
            log['winner']['player_num'] = symbols.index(winner_symbol) + 1
            log['winner']['symbol'] = winner_symbol
        ###

        ### Save log file
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=4)
        ###

        ### return Winner
        return log['winner']
        ###

    #play few games        
    def play_games(players : list, count : int, dir : str) -> dict:
        final_result = [0, 0, 0]
        
        rounds = [1, 2][:] * (count // 2) 
        if(count % 2 != 0):
            rounds.append(1)
        
        random.shuffle(rounds)
        
        for i in range(1, count + 1):
            
            if(rounds[i - 1] == 1):
                symbols = ["X", "O"]
            else:
                symbols = ["O", "X"]
            
            game_result = game.play(
                                   players = players,
                                   symbols = symbols,
                                   path = f"{dir}/{i}.json"
                                   )
            winner = game_result["player_num"]
            
            if(winner == -1):
                final_result[2] += 1
            elif(winner == 1):
                final_result[0] += 1
            else:
                final_result[1] += 1
        
        return final_result


class tools:
    def terminal_input() -> dict:
        if("--o" in sys.argv):
            sys.argv.insert(sys.argv.index("--o") + 1, 1)

        if("--ds" in sys.argv):
            sys.argv.insert(sys.argv.index("--ds") + 1, 1)

        keys = sys.argv[1 : : 2]
        values = sys.argv[2 : : 2] 

        inputs = dict(zip(keys, values))
        return inputs
    
    def setup_dir() -> dict:

        logs_dir = f"{os.path.dirname(os.path.abspath(__file__))}/logs".replace("\\", "/")
        result = {"game_id" : None, "dir" : None}

        n = 1

        if((not os.path.exists(logs_dir)) or (not os.path.isdir(logs_dir))):
            path = f"{logs_dir}/{1}"
            os.mkdir(logs_dir)
            
            
            
        
        else:
            
            while True:
                path = f"{logs_dir}/{n}"
                if((not os.path.exists(path)) or (not os.path.isdir(path))):
                    break

                n += 1
            
        os.mkdir(path)
        
        result["game_id"] = n
        result["dir"] = path

        return result

    def load_player(path : str, id : int) -> player:
        result : player = [0]

        path = path.replace("\\", "/")

        path = path.split("/")
        module = path[-1].split('.')[0]

        dir = "".join(map(lambda x: x + "/", path[:-1]))[: -1]

        if(dir not in ["", "/"]):
            sys.path.append(dir)
        
        exec(f'from {module} import preprocess as ps{id}')
        exec(f'from {module} import action as ac{id}')
        exec(f'result[0] = player({id}, ps{id}, ac{id})')

        return result[0]
    

def main():
    players = [None, None]

    ### Load Inputs
    try:
        inputs = tools.terminal_input()
    except:
        print("[-] Error:\nWrong input format!\n\nPress Enter to Exit...")
        input()
        exit()

    ### Loading Clients
    for i in range(2):

        if(f"-p{i+1}" in inputs.keys()):
            path = inputs[f"-p{i+1}"]
        else:
            path = easygui.fileopenbox(f"Client {i+1}")

        try:
            players[i] = tools.load_player(path, id = i + 1)
        except:
    
            print(f"[-] Error:\nServer cant load player{i + 1}!\n\nPress Enter to Exit...")
            input()
            exit()
    
    ### Output path
    if("--o" in inputs.keys()):
        dir = easygui.diropenbox("Output")
    
    elif("-o" in inputs.keys()):
        dir = inputs["-o"]
        if((not os.path.exists(dir)) or (not os.path.isdir(dir))):
            print(f"[-] Error:\nOutput dir does not exist.\n\nPress Enter to Exit...")
            input()
            exit()
    
    else:
        dir = tools.setup_dir()["dir"]
    
    counts = 1
    if("-c" in inputs.keys()):
        try:
            counts = int(inputs["-c"])
        except:
            print(f"[-] Error:\ngame counts should be a number\n\nPress Enter to Exit...")
            input()
            exit()

    game_result = game.play_games(players, counts, dir)
    if("--ds" not in inputs.keys()):
        print("Scores")
        print("---Player1 :", game_result[0])
        print("---Player2 :", game_result[1])
        print("---Draw    :", game_result[2])
    print(f"\nOutput: {dir}")

    input("\n\nPress Enter to exit...")


if(__name__ == "__main__"):
    main()
        
        






