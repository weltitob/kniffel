"""
kniffel
main.py

created on 06.04.22
by Tobias Welti, Luca Kaiser, Joshua Miller, Danny Seidel
"""

import pickle
import os
import sys
import uuid
from enum import Enum
import game


def error_handler(error):
    """handles all errors for the program

    Args:
        error (String): the error that python throws
    """

    match error:
        case "unsupported input":
            print("Error: Input not supported.")
        case "already set":
            print("Error: This value is already set. Enter a different number.")
        case "number not found":
            print("Error: The given number was not found.")
        case "file not found":
            print("Error: File 'games.json' was not found. Please make sure this file exists in /src. ")
        case "permission error":
            print("Error: This programme does not have the necessary permissions to access the file 'games.json'."
                  "Please make sure that the programme has full access to the file.")
        case "game not found":
            print("Error: There is no saved game.")
        case _:
            print("Error: A unknown error occurred.")


class Color(str, Enum):
    """contains data for coloring the output"""

    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class Terminal:
    """handles terminal data"""

    def __init__(self):
        self.current_game = None
        self.clear_console()
        self.print_menu()
        self.menu_input()

    @staticmethod
    def clear_console():
        """clears console based on operating system"""

        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def print_menu():
        """prints main menu after program start"""

        print(f"{Color.BOLD + Color.YELLOW}Welcome to kniffel!{Color.END}")
        print("Start new game (s)")
        print("Load game (l)")
        print("Quit (q)")

    def menu_input(self):
        """handles inputs for main menu"""

        action = input("\nEnter action: ")

        if action == "s":
            self.create_new_game()
            self.play_game()
        elif action == "l":
            self.load_game()
            self.play_game()
        elif action == "q":
            sys.exit(0)
        else:
            error_handler("unsupported input")
            self.menu_input()

    def create_new_game(self):
        """creates a new game object"""

        game_id = uuid.uuid4()
        self.current_game = game.Game(game_id)

    def play_game(self):
        """looping through game turns and printing the winner"""

        turn = self.current_game.get_current_turn()

        while turn < 13:
            print(f"\n\n{Color.BOLD + Color.PURPLE}Turn {turn + 1}{Color.END}")
            self.player_action(1)
            self.player_action(2)
            self.save_game()
            turn += 1

        self.show_results(self.current_game.player_1)
        print(self.current_game.player_1.get_total_score)
        self.show_results(self.current_game.player_2)
        print(self.current_game.player_2.get_total_score)

        winner_id = self.current_game.get_winner()

        if winner_id == 1:
            print("Player 1 has won!")
        elif winner_id == 2:
            print("Player 2 has won!")
        else:
            print("It's a draw!")

    def player_action(self, player_id):
        """handling the actions for one player turn

        Args:
            player_id (int): current player id (player 1 or 2)
        """

        if player_id == 1:
            player = self.current_game.player_1
        else:
            player = self.current_game.player_2

        attempt = 1
        player.dice_put_aside = []

        print(f"\n{Color.BOLD + Color.DARKCYAN}Player {player_id}{Color.END} is on:")

        while attempt <= 3 and len(player.dice_put_aside) != 5:
            player.throw_dice()
            if attempt < 3:
                print(f"Your thrown {Color.BOLD + Color.GREEN + str(player.dice_used)[1:-1] + Color.END}.")
                if len(player.dice_put_aside) > 0:
                    print(f"Your have {Color.BOLD + Color.BLUE + str(player.dice_put_aside)[1:-1] + Color.END} put aside.")
                    player.reuse_dice()
                for value in player.dice_used:
                    print(f"Do you want rethrow the dice with current value {Color.BOLD + Color.YELLOW + str(value) + Color.END}?")
                    action = input(f"Enter 'n' to {Color.BOLD + Color.RED + 'not' + Color.END} rethrow: ")
                    if action == "n":
                        player.put_dice_aside(value)
                attempt += 1
            else:
                for value in player.dice_used:
                    player.put_dice_aside(value)
            player.dice_put_aside.sort()

        self.show_results(player)

    def show_results(self, player):
        """shows results for one player

        Args:
            player (dynamic): player object of player 1 or 2
        """

        scores = player.get_all_possible_scores()
        upper = player.upper_section_score
        lower = player.lower_section_score

        print(f"You have thrown {Color.BOLD + Color.GREEN + str(player.dice_put_aside)[1:-1] + Color.END}.")
        print("Your scores are:")
        print("  Upper Section:")
        print(f"""  1) Ones:               {Color.BOLD + str(upper['ones']) + Color.END if scores[0] is None
        else Color.RED + str(scores[0]) + Color.END}""")
        print(f"""  2) Twos:               {Color.BOLD + str(upper['twos']) + Color.END if scores[1] is None
        else Color.RED + str(scores[1]) + Color.END}""")
        print(f"""  3) Threes:             {Color.BOLD + str(upper['threes']) + Color.END if scores[2] is None
        else Color.RED + str(scores[2]) + Color.END}""")
        print(f"""  4) Fours:              {Color.BOLD + str(upper['fours']) + Color.END if scores[3] is None
        else Color.RED + str(scores[3]) + Color.END}""")
        print(f"""  5) Fives:              {Color.BOLD + str(upper['fives']) + Color.END if scores[4] is None
        else Color.RED + str(scores[4]) + Color.END}""")
        print(f"""  6) Sixes:              {Color.BOLD + str(upper['sixes']) + Color.END if scores[5] is None
        else Color.RED + str(scores[5]) + Color.END}""")
        print("  Lower Section:")
        print(f"""  7) Three of a Kind:    {Color.BOLD + str(lower['three_of_a_kind']) + Color.END if scores[6] is None
        else Color.RED + str(scores[6]) + Color.END}""")
        print(f"""  8) Four of a Kind:     {Color.BOLD + str(lower['four_of_a_kind']) + Color.END if scores[7] is None
        else Color.RED + str(scores[7]) + Color.END}""")
        print(f"""  9) Full House:         {Color.BOLD + str(lower['full_house']) + Color.END if scores[8] is None
        else Color.RED + str(scores[8]) + Color.END}""")
        print(f"""  10) Small Straight:    {Color.BOLD + str(lower['small_straight']) + Color.END if scores[9] is None
        else Color.RED + str(scores[9]) + Color.END}""")
        print(f"""  11) Large Straight:    {Color.BOLD + str(lower['large_straight']) + Color.END if scores[10] is None
        else Color.RED + str(scores[10]) + Color.END}""")
        print(f"""  12) Yahtzee:           {Color.BOLD + str(lower['yahtzee']) + Color.END if scores[11] is None
        else Color.RED + str(scores[11]) + Color.END}""")
        print(f"""  13) Chance:            {Color.BOLD + str(lower['chance']) + Color.END if scores[12] is None
        else Color.RED + str(scores[12]) + Color.END}""")

        self.save_round_score(scores, upper, lower)

    def save_round_score(self, scores, upper, lower):
        """saves score of current round to dict

        Args:
            scores (_type_): _description_
            upper (_type_): _description_
            lower (_type_): _description_
        """

        score_number = input("Enter the matching number to save the score: ")

        match score_number:
            case "1":
                upper["ones"] = str(scores[0]) if upper["ones"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "2":
                upper["twos"] = scores[1] if upper["twos"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "3":
                upper["threes"] = scores[2] if upper["threes"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "4":
                upper["fours"] = scores[3] if upper["fours"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "5":
                upper["fives"] = scores[4] if upper["fives"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "6":
                upper["sixes"] = scores[5] if upper["sixes"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "7":
                lower["three_of_a_kind"] = scores[6] if lower["three_of_a_kind"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "8":
                lower["four_of_a_kind"] = scores[7] if lower["four_of_a_kind"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "9":
                lower["full_house"] = scores[8] if lower["full_house"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "10":
                lower["small_straight"] = scores[9] if lower["small_straight"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "11":
                lower["large_straight"] = scores[10] if lower["large_straight"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "12":
                lower["yahtzee"] = scores[11] if lower["yahtzee"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case "13":
                lower["chance"] = scores[12] if lower["chance"] is None else (
                    error_handler("already set"), self.save_round_score(scores, upper, lower))
            case _:
                error_handler("number not found")
                self.save_round_score(scores, upper, lower)

    def save_game(self):
        """saves game data to json file"""

        try:
            with open("games.json", "wb") as file:
                pickle.dump(self.current_game, file)
        except PermissionError:
            error_handler("permission error")

    def load_game(self):
        """loads game data from json file"""

        try:
            with open("games.json", "rb") as file:
                data = pickle.load(file)
            if data is not None:
                self.current_game = data
            else:
                error_handler("game not found")
        except FileNotFoundError:
            error_handler("file not found")
        except PermissionError:
            error_handler("permission error")


if __name__ == "__main__":
    Terminal()
