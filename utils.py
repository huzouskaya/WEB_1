from constants import BOARD_LENGTH, SCREEN_HEIGHT, SCREEN_WIDTH

coordinate_builder = lambda row, col: ((SCREEN_WIDTH-BOARD_LENGTH)/2 + col*(BOARD_LENGTH/8), (SCREEN_HEIGHT-BOARD_LENGTH)/2 + row*(BOARD_LENGTH/8))