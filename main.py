import os
import sys
import arcade
import pieces

class MyGameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.set_location(200,100)

        # variables for coordinate calculation relative to the board and relative to the screen
        self.board_pieces_location = [[0 for i in range(9)] for j in range (9)]
        self.white_captured_location = [[0 for i in range(3)] for j in range (3)]
        self.black_captured_location = [[0 for i in range(3)] for j in range (3)]
        self.coordinates_map = [[[x,y] for x in range(170, 845, 75)] for y in range(700, 25, -75)]
        self.white_coordinates = [[[x,y] for x in range(975, 1275, 75)] for y in range(275, -25, -75)]
        self.black_coordinates = [[[x,y] for x in range(975, 1275, 75)] for y in range(675, 375, -75)]

        # initialize variables
        self.mouse_x = 0
        self.mouse_y = 0
        self.selected_piece = 0 #stores selected piece object

        # booleans and somewhat boolean
        self.pieces_selected = False
        self.turn = "white"
        self.promotion_prompt = False
        self.king_checked = False
        self.king_checkmated = False

        # lists
        self.prev_position = [[0, 0], [0, 0], [0, 0]] #not the prev pos of last turn, but prev pos of last click (which could be from either this or last turn)
        self.possible_moves = []
        self.checking_pieces = []
        self.covered_squares = ["test"]
        self.check_possible_responses = [None]

        # sound files
        self.place_sound = arcade.Sound(os.path.join(sys.path[0], "sound", "clack.wav"))
        self.disgrace_sound = arcade.Sound(os.path.join(sys.path[0], "sound", "disgrace.wav"))

        # sprite files
        self.sprites = os.path.join(sys.path[0], "sprites")
        self.all_pieces = arcade.SpriteList()
        self.highlight = arcade.ShapeElementList()

        # places pieces on their correct locations
        self.initialize_pieces()
        
    def on_draw(self):
        # starts render
        arcade.start_render()

        # draws the board
        self.draw_board()
        self.highlight.draw()
        self.all_pieces.draw()

        # numbers your captured pieces
        self.captured_pieces_count()

        # promotion prompt
        if self.promotion_prompt:
            self.draw_prompt()

        # draws game over
        if self.king_checkmated:
            self.draw_checkmate()

        #draws selected piece
        try:
            self.selected_piece.sprite.draw()
        except:
            pass

    def on_update(self, delta_time):
        # makes selected piece follow your mouse
        if self.pieces_selected:
            self.selected_piece.sprite.set_position(self.mouse_x, self.mouse_y)
            self.selected_piece.pos = [self.mouse_x, self.mouse_y]
            self.selected_piece.sprite.update()

    def on_mouse_motion(self, x, y, dx, dy):
        # re-calculates mouse position, so selected piece can follow your mouse
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        # calculates the square on the board you've pressed
        square_location = [int((x - 132.5)//75), int(8-((y-62.5)//75))] #[board_x, board_y]
        white_small_board = [int((x - 937.5)//75), int(2-((y-87.5)//75))]
        black_small_board = [int((x - 937.5)//75), int(2-((y-487.7)//75))]

        if not self.promotion_prompt: #if there's no prompt

            #if clicking on the main board
            if 0 <= square_location[0] <= 8 and 0 <= square_location[1] <= 8:

                #if there is a piece on tile
                if self.board_pieces_location[square_location[1]][square_location[0]] != 0:

                    #if you already have a piece selected
                    if self.pieces_selected:
                        if square_location in self.possible_moves[0]:
                            #enemy piece removed from board and put into your dictionary
                            taken_piece = self.board_pieces_location[square_location[1]][square_location[0]]
                            if taken_piece.promoted:
                                self.all_pieces.remove(taken_piece.sprite)
                                taken_piece = taken_piece.demote()
                                self.all_pieces.append(taken_piece.sprite)

                            #enemy piece put outside the board
                            taken_piece.taken(self.white_captured_location, self.black_captured_location)

                            #adding the enemy piece to your captives dictionary
                            if self.turn == "white":
                                self.white_captives[taken_piece.piece_type].append(taken_piece)
                            else:
                                self.black_captives[taken_piece.piece_type].append(taken_piece)
                            
                            #reset the tile
                            self.board_pieces_location[square_location[1]][square_location[0]] = 0

                            #placing the piece
                            self.place_and_check_promotion(square_location)

                    #if you don't have a piece selected
                    else:
                        #checks if you're using the right pieces
                        self.select_piece(square_location)
                
                #if tile is empty
                else:
                    #if you have a piece selected
                    if self.pieces_selected and square_location in self.possible_moves[0]:
                        if self.selected_piece.captured:
                            self.selected_piece.just_placed = True
                            self.selected_piece.captured = False
                            if self.turn == "white":
                                self.white_captives[self.selected_piece.piece_type].pop()
                            else:
                                self.black_captives[self.selected_piece.piece_type].pop()

                        self.place_and_check_promotion(square_location)
                        self.selected_piece.just_placed = False
            
            #clicking on the smaller board
            else:
                if not self.pieces_selected:
                    if self.turn == "white":
                        if 0 <= white_small_board[0] <= 2 and 0 <= white_small_board[1] <= 2:
                            if self.white_captured_location[white_small_board[1]][white_small_board[0]] != 0:
                                self.selected_piece = self.white_captured_location[white_small_board[1]][white_small_board[0]].pop()
                                if len(self.white_captured_location[white_small_board[1]]) == 0:
                                    self.white_captured_location[white_small_board[1]][white_small_board[0]] = 0
                                self.possible_moves = self.selected_piece.highlight_moves(self.highlight, self.board_pieces_location, self.covered_squares, self.king_checked, self.checking_pieces)
                                self.prev_position[1] = white_small_board
                                self.pieces_selected = True
                    else:
                        if 0 <= black_small_board[0] <= 2 and 0 <= black_small_board[1] <= 2:
                            if self.black_captured_location[black_small_board[1]][black_small_board[0]] != 0:
                                self.selected_piece = self.black_captured_location[black_small_board[1]][black_small_board[0]].pop()
                                if len(self.black_captured_location[black_small_board[1]]) == 0:
                                    self.black_captured_location[black_small_board[1]][black_small_board[0]] = 0
                                self.possible_moves = self.selected_piece.highlight_moves(self.highlight, self.board_pieces_location, self.covered_squares, self.king_checked, self.checking_pieces)
                                self.prev_position[2] = black_small_board
                                self.pieces_selected = True

                #if you have a piece selected
                else: 
                    if self.turn == "white":
                        if white_small_board == self.prev_position[1]:
                            self.white_captured_location[white_small_board[1]][white_small_board[0]].append(self.selected_piece)
                            self.selected_piece.sprite.set_position(self.white_coordinates[white_small_board[1]][white_small_board[0]][0], self.white_coordinates[white_small_board[1]][white_small_board[0]][1])
                            self.selected_piece.pos = self.white_coordinates[white_small_board[1]][white_small_board[0]]
                            self.pieces_selected = False

                        #if you're putting it back into place, don't switch turns
                            if white_small_board != self.prev_position[1]:
                                self.switch_turns()

                            self.highlight = arcade.ShapeElementList()
                    else:
                        if black_small_board == self.prev_position[2]:
                            self.black_captured_location[black_small_board[1]][black_small_board[0]].append(self.selected_piece)
                            self.selected_piece.sprite.set_position(self.black_coordinates[black_small_board[1]][black_small_board[0]][0], self.black_coordinates[black_small_board[1]][black_small_board[0]][1])
                            self.selected_piece.pos = self.black_coordinates[black_small_board[1]][black_small_board[0]]
                            self.pieces_selected = False

                            #if you're putting it back into place, don't switch turns
                            if black_small_board != self.prev_position[2]:
                                self.switch_turns()

                            self.highlight = arcade.ShapeElementList()

        else: #if there is a prompt
            if 385 <= x <= 455 and 345 <= y <= 375: #yes is picked
                #promote
                self.promote()

                self.highlight = arcade.ShapeElementList()
                self.promotion_prompt = False
                self.switch_turns()

            elif 485 <= x <= 555 and 345 <= y <= 375: #no is picked
                self.place(self.prev_position[0])
                self.highlight = arcade.ShapeElementList()
                self.promotion_prompt = False
                self.switch_turns()

    def draw_board(self):
        """ Draws the board and turn indicator """
        #Board and squares
        arcade.draw_rectangle_filled(470, 400, 700, 700, arcade.color.WOOD_BROWN)
        for x in range(170, 845, 75):
            for y in range(100, 775, 75):
                arcade.draw_rectangle_outline(x, y, 75, 75,arcade.color.BLACK)

        #Captured pieces board
        arcade.draw_rectangle_filled(1050, 200, 250, 250, arcade.color.WOOD_BROWN)
        arcade.draw_rectangle_filled(1050, 600, 250, 250, arcade.color.WOOD_BROWN)
        for x in range(975, 1200, 75):
            for y in range(125, 350, 75):
                arcade.draw_rectangle_outline(x, y, 75, 75,arcade.color.BLACK)
            for y in range(525, 750, 75):
                arcade.draw_rectangle_outline(x, y, 75, 75,arcade.color.BLACK)

        # The 4 points
        arcade.draw_point(470-112.5, 400+112.5, arcade.color.BLACK, 5)
        arcade.draw_point(470-112.5, 400-112.5, arcade.color.BLACK, 5)
        arcade.draw_point(470+112.5, 400+112.5, arcade.color.BLACK, 5)
        arcade.draw_point(470+112.5, 400-112.5, arcade.color.BLACK, 5)

        #turn indicator
        arcade.draw_text(self.turn.upper()+"'s turn", 1050, 400, arcade.color.WHITE, 30, align="center", anchor_x="center", anchor_y="center")

    def draw_prompt(self):
        """ Draws the promotion prompt """
        # dark rectangle with "promote?" question
        arcade.draw_rectangle_filled(470, 400, 200, 150, (30, 25, 19))
        arcade.draw_text("Promote?", 470, 420, arcade.color.WHITE, 20, align="center", anchor_x="center", anchor_y="center")

        def draw_button(x, y, text):
            """ Draws button at x, y with the string parameter text """
            arcade.draw_rectangle_filled(x, y, 70, 30, (266, 217, 188))
            arcade.draw_text(text, x, y, arcade.color.BLACK, 14, align="center", anchor_x="center", anchor_y="center")

        # draws yes and no button
        draw_button(420, 360, "Yes")
        draw_button(520, 360, "No")

    def captured_pieces_count(self):
        """counts and displays how much of every type of captured piece you have, if any"""
        for values in self.white_captives.values():
            if len(values) > 0:
                arcade.draw_text(str(len(values)), values[0].pos[0] + 25, values[0].pos[1] - 25, arcade.color.BLACK, 14, align="center", anchor_x="center", anchor_y="center")
        for values in self.black_captives.values():
            if len(values) > 0:
                arcade.draw_text(str(len(values)), values[0].pos[0] + 25, values[0].pos[1] - 25, arcade.color.BLACK, 14, align="center", anchor_x="center", anchor_y="center")

    def initialize_pieces(self):
        """ Initializes pieces on the right locations on the right teams """
        self.white_pieces = {
            "P": [pieces.Pawn("white",self.coordinates_map[6][x]) for x in range(9)],
            "B": [pieces.Bishop("white",self.coordinates_map[7][1])],
            "R": [pieces.Rook("white",self.coordinates_map[7][7])],
            "L": [pieces.Lance("white",self.coordinates_map[8][0]), pieces.Lance("white",self.coordinates_map[8][8])],
            "N": [pieces.Knight("white",self.coordinates_map[8][1]), pieces.Knight("white",self.coordinates_map[8][7])],
            "S": [pieces.Silver("white",self.coordinates_map[8][2]), pieces.Silver("white",self.coordinates_map[8][6])],
            "G": [pieces.Gold("white",self.coordinates_map[8][3]), pieces.Gold("white",self.coordinates_map[8][5])],
            "K": [pieces.King("white",self.coordinates_map[8][4])]
            }
        self.white_captives = {"P": [], "L": [], "N": [], "S": [], "G": [], "B": [], "R": []}
        self.black_pieces = {
            "P": [pieces.Pawn("black",self.coordinates_map[2][x]) for x in range(9)],
            "B": [pieces.Bishop("black",self.coordinates_map[1][7])],
            "R": [pieces.Rook("black",self.coordinates_map[1][1])],
            "L": [pieces.Lance("black",self.coordinates_map[0][0]), pieces.Lance("black",self.coordinates_map[0][8])],
            "N": [pieces.Knight("black",self.coordinates_map[0][1]), pieces.Knight("black",self.coordinates_map[0][7])],
            "S": [pieces.Silver("black",self.coordinates_map[0][2]), pieces.Silver("black",self.coordinates_map[0][6])],
            "G": [pieces.Gold("black",self.coordinates_map[0][3]), pieces.Gold("black",self.coordinates_map[0][5])],
            "K": [pieces.King("black",self.coordinates_map[0][4])]
            }
        self.black_captives = {"P": [], "L": [], "N": [], "S": [], "G": [], "B": [], "R": []}

        # places the pieces on the board
        for key in self.white_pieces:
            for value in self.white_pieces[key]:
                self.board_pieces_location[int(8-((value.pos[1]-62.5)//75))][int((value.pos[0] - 132.5)//75)] = value
                self.all_pieces.append(value.sprite)
            for value in self.black_pieces[key]:
                value.sprite.angle = 180
                self.board_pieces_location[int(8-((value.pos[1]-62.5)//75))][int((value.pos[0] - 132.5)//75)] = value
                self.all_pieces.append(value.sprite)

    def switch_turns(self):
        """ switches turns and does calculations"""
        # resets some variables
        self.checking_pieces = []
        king_is_checked = False
        self.covered_squares.clear()

        # check for checks
        for x in range(9):
            for y in range(9):
                if self.board_pieces_location[y][x] != 0:
                    if self.board_pieces_location[y][x].team == self.turn:
                        is_checking = self.board_pieces_location[y][x].calculate_protecting(self.board_pieces_location, self.covered_squares)
                        if is_checking:
                            self.checking_pieces.append(self.board_pieces_location[y][x])
                            king_is_checked = True
        
        #if king is checked, check for checkmate
        if king_is_checked:
            self.king_checked = True
            self.check_for_checkmate()
        else:
            self.king_checked = False

        #switches turns
        if self.turn == "white":
            self.turn = "black"
        else:
            self.turn = "white"

        # resets previous position of last clicks
        self.prev_position = [[],[],[]]

    def promote(self):
        """removes current piece and place promoted version"""
        self.all_pieces.remove(self.selected_piece.sprite)
        if self.selected_piece.piece_type in "PNLS":
            self.selected_piece = pieces.PromotedPiece(self.turn, self.coordinates_map[self.prev_position[0][1]][self.prev_position[0][0]], self.selected_piece.piece_type)
        elif self.selected_piece.piece_type == "R":
            self.selected_piece = pieces.PromotedRook(self.turn, self.coordinates_map[self.prev_position[0][1]][self.prev_position[0][0]])
        elif self.selected_piece.piece_type == "B":
            self.selected_piece = pieces.PromotedBishop(self.turn, self.coordinates_map[self.prev_position[0][1]][self.prev_position[0][0]])
        
        #puts piece on the board
        self.board_pieces_location[self.prev_position[0][1]][self.prev_position[0][0]] = self.selected_piece
        if self.turn == "black":
            self.selected_piece.sprite.angle = 180
        self.all_pieces.append(self.selected_piece.sprite)

    def check_auto_promote(self, square_location):
        """ checks if piece in position for automatic promotion and promotes them """
        if self.selected_piece.piece_type == "N":
            if (square_location[1] <= 1 and self.turn == "white") or (square_location[1] >= 7 and self.turn == "black"):
                self.pieces_selected = False
                self.prev_position[0] = square_location
                self.promote(1)
                self.highlight = arcade.ShapeElementList()
                self.switch_turns()
                return True
        elif self.selected_piece.piece_type in "PL":
            if (square_location[1] <= 0 and self.turn == "white") or (square_location[1] >= 8 and self.turn == "black"):
                self.pieces_selected = False
                self.prev_position[0] = square_location
                self.promote(1)
                self.highlight = arcade.ShapeElementList()
                self.switch_turns()
                return True

    def place(self, square_location):
        """ places selected piece on given tile """
        self.board_pieces_location[square_location[1]][square_location[0]] = self.selected_piece
        self.selected_piece.sprite.set_position(self.coordinates_map[square_location[1]][square_location[0]][0], self.coordinates_map[square_location[1]][square_location[0]][1])
        self.selected_piece.pos = self.coordinates_map[square_location[1]][square_location[0]]
        self.selected_piece.coords = square_location

        #resets some variables
        self.pieces_selected = False
        self.highlight = arcade.ShapeElementList()

        #plays clack sound effect
        self.place_sound.play()

        #switch turns
        if square_location != self.prev_position[0]:
            self.switch_turns()

    def place_and_check_promotion(self, square_location):
        """ checks for promotion and places piece down """
        #so captured pieces don't promote when you've just placed them down
        if square_location == self.prev_position[0]:
            self.selected_piece.just_placed = True

        if self.turn == "white":
            # checks if piece at promotion range
            if 3 <= square_location[1] <= 8 or self.selected_piece.promoted:
                self.place(square_location)

            else:
                # checks if pieces qualify for auto promotion
                auto_promote = self.check_auto_promote(square_location)
                if not auto_promote:
                    if self.selected_piece.piece_type in "BRSLNKP":
                        if not self.selected_piece.just_placed:
                            # displays the prompt
                            self.pieces_selected = False
                            self.prev_position[0] = square_location
                            self.promotion_prompt = True
                        else:
                            self.place(square_location)
                    else:
                        self.place(square_location)

        else:
            if 0 <= square_location[1] <= 5 or self.selected_piece.promoted:
                self.place(square_location)

            else:
                auto_promote = self.check_auto_promote(square_location)
                if not auto_promote:
                    if self.selected_piece.piece_type in "BRSLNKP":
                        if not self.selected_piece.just_placed:
                            self.pieces_selected = False
                            self.prev_position[0] = square_location
                            self.promotion_prompt = True
                        else:
                            self.place(square_location)
                    else:
                        self.place(square_location)

    def select_piece(self, square_location):
        """ selects a piece given the right team and location """
        if self.turn == self.board_pieces_location[square_location[1]][square_location[0]].team:
            self.selected_piece = self.board_pieces_location[square_location[1]][square_location[0]]
            self.possible_moves = self.selected_piece.highlight_moves(self.highlight, self.board_pieces_location, self.covered_squares, self.king_checked, self.checking_pieces)
            self.board_pieces_location[square_location[1]][square_location[0]] = 0
            self.prev_position[0] = square_location
            self.pieces_selected = True

    def check_for_checkmate(self):
        #check for checkmate here
        self.covered_squares.append("hello")
        placeholder_highlight = arcade.ShapeElementList()

        #calculate every piece's possible move
        for x in range(9):
            for y in range(9):
                if self.check_possible_responses[-1] is None:
                    if self.board_pieces_location[y][x] != 0:
                        if self.board_pieces_location[y][x].team != self.turn:
                            self.check_possible_responses.append(self.board_pieces_location[y][x].highlight_moves(placeholder_highlight, self.board_pieces_location, self.covered_squares, self.king_checked, self.checking_pieces))

        #if there are no possible moves by any piece
        if self.check_possible_responses[-1] is None:
            self.king_checkmated = True
            self.disgrace_sound.play()

        # resets variables after checking
        self.check_possible_responses = [None]
        placeholder_highlight = arcade.ShapeElementList()
        self.covered_squares.pop()

    def draw_checkmate(self):
        """ Alerts the winner """
        self.turn = self.checking_pieces[0].team
        arcade.draw_rectangle_filled(470, 400, 200, 150, (30, 25, 19))
        arcade.draw_text(self.turn.upper()+" wins!", 470, 420, arcade.color.WHITE, 20, align="center", anchor_x="center", anchor_y="center")


MyGameWindow(1280, 800, "Shogi Sim v1.1")
arcade.run()