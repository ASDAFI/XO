import random



### App INFO
__version__ = "1.0"



def preprocess(player : str):
    """
    This function will run once before the game's start
    you can do any kind of process here and this function has not any outputs

    inputs:
        player : string
            player is "X" or "O" it depends on your side in game


    usage:
        you can load models or calculate any thing you want here
        if this function has not any kind of usage for you, you can let it be empty
    
    sample:
        preprocess sample function is an empty function
    
    Limits:
        20 Mb Memory
        3 seconds
    """
    
    return

def action(grid : list, player : str) -> int:
    """
    in this function you should choose a empty place in grid

    inputs:
        grid : list
            the game grid will be in grid variable
            
            example:
            game grid:
                X - O
                O X -
                X - O    
            grid = ["X", "-", "O", "O", "X", "-", "X", "-", "O"]

        player : string
            player is "X" or "O" it depends on your side in game
    
    output:
        a number(int) n and it shows that where you choose
        
        grid:
            0 1 2
            3 4 5
            6 7 8
        
        you should return a number between 0-8 that shows where you choose
        if this place is already taken, you will lose your choice!
    

    Limits:
        10 Mb Memory
        0.5 second
        
    Sample:
        Here is a random player function which choose random cell from the grid

    """

    ### Find empty cells in the grid
    empty_cells = []
    for i in range(9):
        if(grid[i] == "-"):
            empty_cells.append(i)
    
    ### Choose random cell from empty cells
    chosen_cell = random.choice(empty_cells)

    ### Return chosen cell
    return chosen_cell

