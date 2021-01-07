import arcade
import os
import sys
import copy

class Pieces:
    def __init__(self, team: str, pos: list):
        self.team = team
        self.pos = pos #[screen_x, screen_y]
        self.coords = [int((pos[0] - 132.5)//75), int(8-((pos[1]-62.5)//75))] #[board_x, board_y]
        self.coords1 = [int((pos[0] - 937.5)//75), int(2-((pos[1]-87.5)//75))] #[white_board_x, white_board_y]
        self.coords2 = [int((pos[0] - 937.5)//75), int(2-((pos[1]-487.7)//75))] #[black_board_x, black_board_y]
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", "Shogi_empty1.png"), center_x=self.pos[0], center_y=self.pos[1])
        self.captured = False
        self.just_placed = False
        self.promoted = False
        self.checking = False
        self.pinned_by = []

    def highlight_moves(self):
        self.coords = [int((self.pos[0] - 132.5)//75), int(8-((self.pos[1]-62.5)//75))]
        self.coords1 = [int((self.pos[0] - 937.5)//75), int(2-((self.pos[1]-87.5)//75))]
        self.coords2 = [int((self.pos[0] - 937.5)//75), int(2-((self.pos[1]-487.7)//75))]
        possible_squares = [[],[],[]] #[[board_x, board_y]] [big board, white captured, black captured]
        return possible_squares

    def add_current_square(self, possible_squares, shapelist):
        current_square = arcade.create_rectangle_filled(self.pos[0], self.pos[1], 73, 73, (166, 139, 90))
        shapelist.append(current_square)
        if not self.captured:
            possible_squares[0].append(self.coords)
        else:
            if self.team == "white":
                possible_squares[1].append(self.coords1)
            else:
                possible_squares[2].append(self.coords2)        

    def add_squares(self, x, y, possible_squares, shapelist):
        # x and y are board coordinates
        possible_squares[0].append([x, y])
        square = arcade.create_rectangle_filled(board_map[y][x][0], board_map[y][x][1], 73, 73, (255, 236, 201))
        shapelist.append(square)

    def taken(self, x, y1, y2):
        self.captured = True
        if self.team == "white":
            self.team = "black"
            self.sprite.angle = 180
            self.sprite.set_position(x, y1)
            self.pos = [x, y1]
        else:
            self.team = "white"
            self.sprite.angle = 0
            self.sprite.set_position(x, y2)
            self.pos = [x, y2]

    def check_if_checking(self, board, king_in_range, king_location):
        if king_in_range:
            board[king_location[0]][king_location[1]].checked = True
            self.checking = True
            print("Check!")
            return True
        else:
            self.checking = False
            return False

    def evaluate_movement(self, x, y, board, covered_squares, enemy_piece, possible_squares, shapelist):
        """checks if moving to [x, y] does not expose the king and adds it to possible moves"""
        temp_board, temp_covered_squares = copy.deepcopy(board), copy.deepcopy(covered_squares)
        if not self.captured:
            temp_board[self.coords[1]][self.coords[0]], temp_board[y][x] = 0, temp_board[self.coords[1]][self.coords[0]]
        else:
            temp_board[y][x] = self
        if not enemy_piece.calculate_protecting(temp_board, temp_covered_squares):
            self.add_squares(x, y, possible_squares, shapelist)


class Pawn(Pieces):
    def __init__(self,team: str,pos: list):
        super().__init__(team, pos)
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", "pawn.png"), center_x=self.pos[0], center_y=self.pos[1])
        self.piece_type = "P"

    def highlight_moves(self, shapelist, board, covered_squares, king_checked, checking_pieces):
        possible_squares = super().highlight_moves()

        #since different team pawns moves in opposite direction, check for which team your pawn is in
        if len(checking_pieces) <= 1:
            if not self.captured:
                if self.team == "white":
                    #checks whether there is a piece in front
                    if board[self.coords[1] - 1][self.coords[0]] != 0:
                        if king_checked:
                            if len(self.pinned_by) == 0:
                                if board[self.coords[1] - 1][self.coords[0]] == checking_pieces[0]:
                                    super().add_squares(self.coords[0], self.coords[1] - 1, possible_squares, shapelist)
                        else:
                            if board[self.coords[1] - 1][self.coords[0]].team != self.team:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0], self.coords[1] - 1, possible_squares, shapelist)
                                else:
                                    #test if taking this piece will expose the king
                                    super().evaluate_movement(self.coords[0], self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(self.coords[0], self.coords[1] - 1, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(self.coords[0], self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(self.coords[0], self.coords[1] - 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                else:
                    if board[self.coords[1] + 1][self.coords[0]] != 0:
                        if king_checked:
                            if len(self.pinned_by) == 0:
                                if board[self.coords[1] + 1][self.coords[0]] == checking_pieces[0]:
                                    super().add_squares(self.coords[0], self.coords[1] + 1, possible_squares, shapelist)
                        else:
                            if board[self.coords[1] + 1][self.coords[0]].team != self.team:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0], self.coords[1] + 1, possible_squares, shapelist)
                                else:
                                    super().evaluate_movement(self.coords[0], self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(self.coords[0], self.coords[1] + 1, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(self.coords[0], self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(self.coords[0], self.coords[1] + 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
            else:
                if self.team == "white":
                    for x in range(0,9):
                        column_is_possible = True
                        for y in range(1,9):
                            if board[y][x] != 0:
                                if board[y][x].piece_type == self.piece_type and board[y][x].team == self.team:
                                    column_is_possible = False
                                    break
                        if column_is_possible:
                            for y in range(1,9):
                                if board[y][x] == 0:
                                    if not king_checked:
                                        super().add_squares(x, y, possible_squares, shapelist)
                                    elif king_checked and checking_pieces[0].piece_type in "BRL":
                                        super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                        
                else:
                    for x in range(0, 9):
                        column_is_possible = True
                        for y in range(0,8):
                            if board[y][x] != 0:
                                if board[y][x].piece_type == self.piece_type and board[y][x].team == self.team:
                                    column_is_possible = False
                                    break
                        if column_is_possible:
                            for y in range(0,8):
                                if board[y][x] == 0:
                                    if not king_checked:
                                        super().add_squares(x, y, possible_squares, shapelist)
                                    elif king_checked and checking_pieces[0].piece_type in "BRL":
                                        super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

        if covered_squares[-1] != "hello": #prevents adding current square as a possible square if checking for checkmate
            super().add_current_square(possible_squares, shapelist)
            
        if len(possible_squares[0]) != 0:
            return possible_squares

    def taken(self, white_board, black_board, itself):
        # reset both protecting of yourself and protected_by of others if you have to
        # and also your own protected_by
        super().taken(975, 525, 275)
        if self.team == "white":
            if white_board[0][0] != 0:
                white_board[0][0].append(itself)
            else:
                white_board[0][0] = [itself]
        else:
            if black_board[2][0] != 0:
                black_board[2][0].append(itself)
            else:
                black_board[2][0] = [itself]

    def calculate_protecting(self, board, covered_squares):
        # update both self.protecting list
        # and the other pieces' protected_by list
        # and then you loop this function for every single piece on your team before it switches turns
        # reset BOTH protected and protected_by at the start of your turn
        king_in_range = False
        king_location = [0, 0]
        if not self.captured:
            if self.team == "white":
                #checks whether there is a piece in front
                if board[self.coords[1] - 1][self.coords[0]] != 0:
                    #if there is a piece in front from the same team, it is not possible to move there
                    if board[self.coords[1] - 1][self.coords[0]].team == self.team:
                        covered_squares.append([self.coords[0], self.coords[1] - 1])
                    elif board[self.coords[1] - 1][self.coords[0]].team != self.team and board[self.coords[1] - 1][self.coords[0]].piece_type == "K":
                        king_location = [self.coords[1] - 1, self.coords[0]]
                        king_in_range = True
                else:
                    covered_squares.append([self.coords[0], self.coords[1] - 1])
            else:
                if board[self.coords[1] + 1][self.coords[0]] != 0:
                    if board[self.coords[1] + 1][self.coords[0]].team != self.team:
                        covered_squares.append([self.coords[0], self.coords[1] + 1])
                    elif board[self.coords[1] + 1][self.coords[0]].team != self.team and board[self.coords[1] + 1][self.coords[0]].piece_type == "K":
                        king_location = [self.coords[1] + 1, self.coords[0]]
                        king_in_range = True
                else:
                    covered_squares.append([self.coords[0], self.coords[1] + 1])
        
        return super().check_if_checking(board, king_in_range, king_location)

class Bishop(Pieces):
    def __init__(self,team: str,pos: list):
        super().__init__(team, pos)
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", "bishop.png"), center_x=self.pos[0], center_y=self.pos[1])
        self.piece_type = "B"

    def highlight_moves(self, shapelist, board, covered_squares, king_checked, checking_pieces):
        possible_squares = super().highlight_moves()

        #up-right diagonal
        if len(checking_pieces) <= 1:
            if not self.captured:
                for x, y in zip(range(self.coords[0] + 1, 9), range(self.coords[1] - 1, -1, -1)):
                    if board[y][x] != 0:
                        if board[y][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][x] == checking_pieces[0]:
                                        super().add_squares(x, y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #up-left diagonal
                for x, y in zip(range(self.coords[0] - 1, -1, -1), range(self.coords[1] - 1, -1, -1)):
                    if board[y][x] != 0:
                        if board[y][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][x] == checking_pieces[0]:
                                        super().add_squares(x, y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #down-right diagonal
                for x, y in zip(range(self.coords[0] + 1, 9), range(self.coords[1] + 1, 9)):
                    if board[y][x] != 0:
                        if board[y][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][x] == checking_pieces[0]:
                                        super().add_squares(x, y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #down-left diagonal
                for x, y in zip(range(self.coords[0] - 1, -1, -1), range(self.coords[1] + 1, 9,)):
                    if board[y][x] != 0:
                        if board[y][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][x] == checking_pieces[0]:
                                        super().add_squares(x, y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                        
            else:
                for x in range(0,9):
                    for y in range(0,9):
                        if board[y][x] == 0:
                            if not king_checked:
                                super().add_squares(x, y, possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

        if covered_squares[-1] != "hello":
            super().add_current_square(possible_squares, shapelist)

        if len(possible_squares[0]) != 0:
            return possible_squares

    def taken(self, white_board, black_board, itself):
        super().taken(975, 675, 125)
        if self.team == "white":
            if white_board[2][0] != 0:
                white_board[2][0].append(itself)
            else:
                white_board[2][0] = [itself]
        else:
            if black_board[0][0] != 0:
                black_board[0][0].append(itself)
            else:
                black_board[0][0] = [itself]

    def calculate_protecting(self, board, covered_squares):
        king_in_range = False
        king_location = [0, 0]
        if not self.captured:
            #up-right diagonal
            pieces_encountered = 0
            for x, y in zip(range(self.coords[0] + 1, 9), range(self.coords[1] - 1, -1, -1)):
                if board[y][x] != 0:
                    if board[y][x].team == self.team:
                        covered_squares.append([x, y])
                        break
                    elif board[y][x].team != self.team and board[y][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, y])

            #up-left diagonal
            for x, y in zip(range(self.coords[0] - 1, -1, -1), range(self.coords[1] - 1, -1, -1)):
                if board[y][x] != 0:
                    if board[y][x].team == self.team:
                        covered_squares.append([x, y])
                        break
                    elif board[y][x].team != self.team and board[y][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, y])

            #down-right diagonal
            for x, y in zip(range(self.coords[0] + 1, 9), range(self.coords[1] + 1, 9)):
                if board[y][x] != 0:
                    if board[y][x].team == self.team:
                        covered_squares.append([x, y])
                        break
                    elif board[y][x].team != self.team and board[y][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, y])

            #down-left diagonal
            for x, y in zip(range(self.coords[0] - 1, -1, -1), range(self.coords[1] + 1, 9,)):
                if board[y][x] != 0:
                    if board[y][x].team == self.team:
                        covered_squares.append([x, y])
                        break
                    elif board[y][x].team != self.team and board[y][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, y])
            
            return super().check_if_checking(board, king_in_range, king_location)

class Rook(Pieces):
    def __init__(self,team: str,pos: list):
        super().__init__(team, pos)
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", "rook.png"), center_x=self.pos[0], center_y=self.pos[1])
        self.piece_type = "R"
    
    def highlight_moves(self, shapelist, board, covered_squares, king_checked, checking_pieces):
        possible_squares = super().highlight_moves()

        if len(checking_pieces) <= 1:
            if not self.captured:
                #up
                for y in range(self.coords[1] - 1, -1, -1):
                    if board[y][self.coords[0]] != 0:
                        if board[y][self.coords[0]].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][self.coords[0]] == checking_pieces[0]:
                                        super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(self.coords[0], y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(self.coords[0], y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #down
                for y in range(self.coords[1] + 1, 9):
                    if board[y][self.coords[0]] != 0:
                        if board[y][self.coords[0]].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][self.coords[0]] == checking_pieces[0]:
                                        super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(self.coords[0], y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(self.coords[0], y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                
                #right
                for x in range(self.coords[0] + 1, 9):
                    if board[self.coords[1]][x] != 0:
                        if board[self.coords[1]][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[self.coords[1]][x] == checking_pieces[0]:
                                        super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, self.coords[1], possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, self.coords[1], board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #left
                for x in range(self.coords[0] - 1, -1, -1):
                    if board[self.coords[1]][x] != 0:
                        if board[self.coords[1]][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[self.coords[1]][x] == checking_pieces[0]:
                                        super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, self.coords[1], possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, self.coords[1], board, covered_squares, checking_pieces[0], possible_squares, shapelist)
            else:
                for x in range(0,9):
                    for y in range(0,9):
                        if board[y][x] == 0:
                            if not king_checked:
                                super().add_squares(x, y, possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

        if covered_squares[-1] != "hello":
            super().add_current_square(possible_squares, shapelist)

        if len(possible_squares[0]) != 0:
            return possible_squares

    def taken(self, white_board, black_board, itself):
        super().taken(1125, 675, 125)
        if self.team == "white":
            if white_board[2][2] != 0:
                white_board[2][2].append(itself)
            else:
                white_board[2][2] = [itself]
        else:
            if black_board[0][2] != 0:
                black_board[0][2].append(itself)
            else:
                black_board[0][2] = [itself]

    def calculate_protecting(self, board, covered_squares):
        pieces_encountered = 0
        king_in_range = False
        king_location = [0, 0]
        if not self.captured:
            #up
            pieces_encountered = 0
            for y in range(self.coords[1] - 1, -1, -1):
                if board[y][self.coords[0]] != 0:
                    if board[y][self.coords[0]].team == self.team:
                        covered_squares.append([self.coords[0], y])
                        break
                    elif board[y][self.coords[0]].team != self.team and board[y][self.coords[0]].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, self.coords[0]]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][self.coords[0]]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([self.coords[0], y])

            #down
            pieces_encountered = 0
            for y in range(self.coords[1] + 1, 9):
                if board[y][self.coords[0]] != 0:
                    if board[y][self.coords[0]].team == self.team:
                        covered_squares.append([self.coords[0], y])
                        break
                    elif board[y][self.coords[0]].team != self.team and board[y][self.coords[0]].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, self.coords[0]]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][self.coords[0]]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([self.coords[0], y])
            
            #right
            pieces_encountered = 0
            for x in range(self.coords[0] + 1, 9):
                if board[self.coords[1]][x] != 0:
                    if board[self.coords[1]][x].team == self.team:
                        covered_squares.append([x, self.coords[1]])
                        break
                    elif board[self.coords[1]][x].team != self.team and board[self.coords[1]][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [self.coords[1], x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[self.coords[1]][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, self.coords[1]])

            #left
            pieces_encountered = 0
            for x in range(self.coords[0] - 1, -1, -1):
                if board[self.coords[1]][x] != 0:
                    if board[self.coords[1]][x].team == self.team:
                        covered_squares.append([x, self.coords[1]])
                        break
                    elif board[self.coords[1]][x].team != self.team and board[self.coords[1]][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [self.coords[1], x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[self.coords[1]][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, self.coords[1]])

            return super().check_if_checking(board, king_in_range, king_location)

class Lance(Pieces):
    def __init__(self,team: str,pos: list):
        super().__init__(team, pos)
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", "lance.png"), center_x=self.pos[0], center_y=self.pos[1])
        self.piece_type = "L"

    def highlight_moves(self, shapelist, board, covered_squares, king_checked, checking_pieces):
        possible_squares = super().highlight_moves()

        if len(checking_pieces) <= 1:
            if not self.captured:
                if self.team == "white":
                    for y in range(self.coords[1] - 1, -1, -1):
                        if board[y][self.coords[0]] != 0:
                            if board[y][self.coords[0]].team != self.team:
                                if king_checked:
                                    if len(self.pinned_by) == 0:
                                        if board[y][self.coords[0]] == checking_pieces[0]:
                                            super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                            break
                                else:
                                    if len(self.pinned_by) == 0:
                                        super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                        break
                                    else:
                                        super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                            else:
                                break
                        else:
                            if not king_checked:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                else:
                                    super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(self.coords[0], y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                else:
                    for y in range(self.coords[1] + 1, 9):
                        if board[y][self.coords[0]] != 0:
                            if board[y][self.coords[0]].team != self.team:
                                if king_checked:
                                    if len(self.pinned_by) == 0:
                                        if board[y][self.coords[0]] == checking_pieces[0]:
                                            super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                            break
                                else:
                                    if len(self.pinned_by) == 0:
                                        super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                        break
                                    else:
                                        super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                            else:
                                break
                        else:
                            if not king_checked:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                else:
                                    super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(self.coords[0], y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
            else:
                if self.team == "white":
                    for x in range(0,9):
                        for y in range(1,9):
                            if board[y][x] == 0:
                                if not king_checked:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                elif king_checked and checking_pieces[0].piece_type in "BRL":
                                    temp_board, temp_covered_squares = copy.deepcopy(board), copy.deepcopy(covered_squares)
                                    temp_board[y][x] = copy.deepcopy(self)
                                    if not checking_pieces[0].calculate_protecting(temp_board, temp_covered_squares):
                                        super().add_squares(x, y, possible_squares, shapelist)
                else:
                    for x in range(0,9):
                        for y in range(0,8):
                            if board[y][x] == 0:
                                if not king_checked:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                elif king_checked and checking_pieces[0].piece_type in "BRL":
                                    super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

        if covered_squares[-1] != "hello":
            super().add_current_square(possible_squares, shapelist)

        if len(possible_squares[0]) != 0:
            return possible_squares
    
    def taken(self, white_board, black_board, itself):
        super().taken(1050, 525, 275)
        if self.team == "white":
            if white_board[0][1] != 0:
                white_board[0][1].append(itself)
            else:
                white_board[0][1] = [itself]
        else:
            if black_board[2][1] != 0:
                black_board[2][1].append(itself)
            else:
                black_board[2][1] = [itself]

    def calculate_protecting(self, board, covered_squares):
        pieces_encountered = 0
        king_in_range = False
        king_location = [0, 0]
        if not self.captured:
            if self.team == "white":
                for y in range(self.coords[1] - 1, -1, -1):
                    if board[y][self.coords[0]] != 0:
                        if board[y][self.coords[0]].team == self.team:
                            covered_squares.append([self.coords[0], y])
                            break
                        elif board[y][self.coords[0]].team != self.team and board[y][self.coords[0]].piece_type == "K":
                            if pieces_encountered == 0:
                                king_location = [y, self.coords[0]]
                                king_in_range = True
                            elif pieces_encountered == 1:
                                potentially_pinned.pinned_by.append(self)
                        else:
                            pieces_encountered += 1
                            potentially_pinned = board[y][self.coords[0]]
                            if pieces_encountered == 2:
                                break
                    else:
                        if pieces_encountered == 0:
                            covered_squares.append([self.coords[0], y])
            else:
                for y in range(self.coords[1] + 1, 9):
                    if board[y][self.coords[0]] != 0:
                        if board[y][self.coords[0]].team == self.team:
                            covered_squares.append([self.coords[0], y])
                            break
                        elif board[y][self.coords[0]].team != self.team and board[y][self.coords[0]].piece_type == "K":
                            if pieces_encountered == 0:
                                king_location = [y, self.coords[0]]
                                king_in_range = True
                            elif pieces_encountered == 1:
                                potentially_pinned.pinned_by.append(self)
                        else:
                            pieces_encountered += 1
                            potentially_pinned = board[y][self.coords[0]]
                            if pieces_encountered == 2:
                                break
                    else:
                        if pieces_encountered == 0:
                            covered_squares.append([self.coords[0], y])

            return super().check_if_checking(board, king_in_range, king_location)

class Knight(Pieces):
    def __init__(self,team: str,pos: list):
        super().__init__(team, pos)
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", "knight.png"), center_x=self.pos[0], center_y=self.pos[1])
        self.piece_type = "N"

    def highlight_moves(self, shapelist, board, covered_squares, king_checked, checking_pieces):
        possible_squares = super().highlight_moves()

        if len(checking_pieces) <= 1:
            if not self.captured:
                if self.team == "white":
                    #left
                    if self.coords[0] - 1 != -1:
                        if board[self.coords[1]-2][self.coords[0]-1] != 0: #if square not empty
                            if board[self.coords[1]-2][self.coords[0]-1].team != self.team:
                                if king_checked:
                                    if len(self.pinned_by) == 0:
                                        if board[self.coords[1]-2][self.coords[0]-1] == checking_pieces[0]:
                                            super().add_squares(self.coords[0]-1, self.coords[1]-2, possible_squares, shapelist)
                                else:
                                    if len(self.pinned_by) == 0:
                                        super().add_squares(self.coords[0]-1, self.coords[1]-2, possible_squares, shapelist)
                                    else:
                                        super().evaluate_movement(self.coords[0]-1, self.coords[1]-2, covered_squares, pinned_by[0], possible_squares, shapelist)
                        else: #if square empty
                            if not king_checked:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0]-1, self.coords[1]-2, possible_squares, shapelist)
                                else:
                                    super().evaluate_movement(self.coords[0]-1, self.coords[1]-2, covered_squares, pinned_by[0], possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(self.coords[0]-1, self.coords[1]-2, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                    #right
                    if self.coords[0] + 1 != 9:
                        if board[self.coords[1]-2][self.coords[0]+1] != 0: #if square not empty
                            if board[self.coords[1]-2][self.coords[0]+1].team != self.team:
                                if king_checked:
                                    if len(self.pinned_by) == 0:
                                        if board[self.coords[1]-2][self.coords[0]+1] == checking_pieces[0]:
                                            super().add_squares(self.coords[0]+1, self.coords[1]-2, possible_squares, shapelist)
                                else:
                                    if len(self.pinned_by) == 0:
                                        super().add_squares(self.coords[0]+1, self.coords[1]-2, possible_squares, shapelist)
                                    else:
                                        super().evaluate_movement(self.coords[0]+1, self.coords[1]-2, covered_squares, pinned_by[0], possible_squares, shapelist)
                        else: #if square empty
                            if not king_checked:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0]+1, self.coords[1]-2, possible_squares, shapelist)
                                else:
                                    super().evaluate_movement(self.coords[0]+1, self.coords[1]-2, covered_squares, pinned_by[0], possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(self.coords[0]+1, self.coords[1]-2, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                else:
                    #left
                    if self.coords[0] - 1 != -1:
                        if board[self.coords[1]+2][self.coords[0]-1] != 0: #if square not empty
                            if board[self.coords[1]+2][self.coords[0]-1].team != self.team:
                                if king_checked:
                                    if len(self.pinned_by) == 0:
                                        if board[self.coords[1]+2][self.coords[0]-1] == checking_pieces[0]:
                                            super().add_squares(self.coords[0]-1, self.coords[1]+2, possible_squares, shapelist)
                                else:
                                    if len(self.pinned_by) == 0:
                                        super().add_squares(self.coords[0]-1, self.coords[1]+2, possible_squares, shapelist)
                                    else:
                                        super().evaluate_movement(self.coords[0]-1, self.coords[1]+2, covered_squares, pinned_by[0], possible_squares, shapelist)
                        else: #if square empty
                            if not king_checked:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0]-1, self.coords[1]+2, possible_squares, shapelist)
                                else:
                                    super().evaluate_movement(self.coords[0]-1, self.coords[1]+2, covered_squares, pinned_by[0], possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(self.coords[0]-1, self.coords[1]+2, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                    #right
                    if self.coords[0] + 1 != 9:
                        if board[self.coords[1]+2][self.coords[0]+1] != 0: #if square not empty
                            if board[self.coords[1]+2][self.coords[0]+1].team != self.team:
                                if king_checked:
                                    if len(self.pinned_by) == 0:
                                        if board[self.coords[1]+2][self.coords[0]+1] == checking_pieces[0]:
                                            super().add_squares(self.coords[0]+1, self.coords[1]+2, possible_squares, shapelist)
                                else:
                                    if len(self.pinned_by) == 0:
                                        super().add_squares(self.coords[0]+1, self.coords[1]+2, possible_squares, shapelist)
                                    else:
                                        super().evaluate_movement(self.coords[0]+1, self.coords[1]+2, covered_squares, pinned_by[0], possible_squares, shapelist)
                        else: #if square empty
                            if not king_checked:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0]+1, self.coords[1]+2, possible_squares, shapelist)
                                else:
                                    super().evaluate_movement(self.coords[0]+1, self.coords[1]+2, covered_squares, pinned_by[0], possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(self.coords[0]+1, self.coords[1]+2, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
            else:
                if self.team == "white":
                    for x in range(0,9):
                        for y in range(2,9):
                            if board[y][x] == 0:
                                if not king_checked:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                elif king_checked and checking_pieces[0].piece_type in "BRL":
                                    temp_board, temp_covered_squares = copy.deepcopy(board), copy.deepcopy(covered_squares)
                                    temp_board[y][x] = copy.deepcopy(self)
                                    if not checking_pieces[0].calculate_protecting(temp_board, temp_covered_squares):
                                        super().add_squares(x, y, possible_squares, shapelist)
                else:
                    for x in range(0,9):
                        for y in range(0,7):
                            if board[y][x] == 0:
                                if not king_checked:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                elif king_checked and checking_pieces[0].piece_type in "BRL":
                                    super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

        if covered_squares[-1] != "hello":
            super().add_current_square(possible_squares, shapelist)

        if len(possible_squares[0]) != 0:
            return possible_squares

    def taken(self, white_board, black_board, itself):
        super().taken(1125, 525, 275)
        if self.team == "white":
            if white_board[0][2] != 0:
                white_board[0][2].append(itself)
            else:
                white_board[0][2] = [itself]
        else:
            if black_board[2][2] != 0:
                black_board[2][2].append(itself)
            else:
                black_board[2][2] = [itself]

    def calculate_protecting(self, board, covered_squares):
        king_in_range = False
        king_location = [0, 0]
        if not self.captured:
            if self.team == "white":
                #left
                if self.coords[0] - 1 != -1:
                    if board[self.coords[1]-2][self.coords[0]-1] != 0: #if square not empty
                        if board[self.coords[1]-2][self.coords[0]-1].team == self.team:
                            covered_squares.append([self.coords[0]-1, self.coords[1]-2])
                        elif board[self.coords[1]-2][self.coords[0]-1].team != self.team and board[self.coords[1]-2][self.coords[0]-1].piece_type == "K":
                            king_location = [self.coords[1]-2, self.coords[0]-1]
                            king_in_range = True
                    else:
                        covered_squares.append([self.coords[0]-1, self.coords[1]-2])
                #right
                if self.coords[0] + 1 != 9:
                    if board[self.coords[1]-2][self.coords[0]+1] != 0: #if square not empty
                        if board[self.coords[1]-2][self.coords[0]+1].team == self.team:
                            covered_squares.append([self.coords[0]+1, self.coords[1]-2])
                        elif board[self.coords[1]-2][self.coords[0]+1].team != self.team and board[self.coords[1]-2][self.coords[0]+1].piece_type == "K":
                            king_location = [self.coords[1]-2, self.coords[0]+1]
                            king_in_range = True
                    else:
                        covered_squares.append([self.coords[0]+1, self.coords[1]-2])
            else:
                #left
                if self.coords[0] - 1 != -1:
                    if board[self.coords[1]+2][self.coords[0]-1] != 0: #if square not empty
                        if board[self.coords[1]+2][self.coords[0]-1].team == self.team:
                            covered_squares.append([self.coords[0]-1, self.coords[1]+2])
                        elif board[self.coords[1]+2][self.coords[0]-1].team != self.team and board[self.coords[1]+2][self.coords[0]-1].piece_type == "K":
                            king_location = [self.coords[1]+2, self.coords[0]-1]
                            king_in_range = True
                    else:
                        covered_squares.append([self.coords[0]-1, self.coords[1]+2])
                #right
                if self.coords[0] + 1 != 9:
                    if board[self.coords[1]+2][self.coords[0]+1] != 0: #if square not empty
                        if board[self.coords[1]+2][self.coords[0]+1].team == self.team:
                            covered_squares.append([self.coords[0]+1, self.coords[1]+2])
                        elif board[self.coords[1]+2][self.coords[0]+1].team != self.team and board[self.coords[1]+2][self.coords[0]+1].piece_type == "K":
                            king_location = [self.coords[1]+2, self.coords[0]+1]
                            king_in_range = True
                    else:
                        covered_squares.append([self.coords[0]+1, self.coords[1]+2])
            
            return super().check_if_checking(board, king_in_range, king_location)

class Silver(Pieces):
    def __init__(self,team: str,pos: list):
        super().__init__(team, pos)
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", "silver.png"), center_x=self.pos[0], center_y=self.pos[1])
        self.piece_type = "S"

    def highlight_moves(self, shapelist, board, covered_squares, king_checked, checking_pieces):
        possible_squares = super().highlight_moves()

        if len(checking_pieces) <= 1:
            if not self.captured:
                if self.team == "white":
                    for x in range(self.coords[0] - 1, self.coords[0] + 2):
                        #top 3
                        if x != -1:
                            try:
                                if self.coords[1] >= 1:
                                    if board[self.coords[1] - 1][x] != 0:
                                        if board[self.coords[1] - 1][x].team != self.team:
                                            if king_checked:
                                                if len(self.pinned_by) == 0:
                                                    if board[self.coords[1] - 1][x] == checking_pieces[0]:
                                                        super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                            else:
                                                if len(self.pinned_by) == 0:
                                                    super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                                else:
                                                    super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    else:
                                        if not king_checked:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                                            super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass
                            
                            #bottom 2 corners
                            try:
                                if self.coords[1] <= 7 and x != self.coords[0]:
                                    if board[self.coords[1] + 1][x] != 0:
                                        if board[self.coords[1] + 1][x].team != self.team:
                                            if king_checked:
                                                if len(self.pinned_by) == 0:
                                                    if board[self.coords[1] + 1][x] == checking_pieces[0]:
                                                        super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                            else:
                                                if len(self.pinned_by) == 0:
                                                    super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                                else:
                                                    super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    else:
                                        if not king_checked:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                                            super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass
                else:
                    for x in range(self.coords[0] - 1, self.coords[0] + 2):
                        #top 3
                        if x != -1:
                            try:
                                if board[self.coords[1] + 1][x] != 0:
                                    if board[self.coords[1] + 1][x].team != self.team:
                                        if king_checked:
                                            if len(self.pinned_by) == 0:
                                                if board[self.coords[1] + 1][x] == checking_pieces[0]:
                                                    super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                        else:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                else:
                                    if not king_checked:
                                        if len(self.pinned_by) == 0:
                                            super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                        else:
                                            super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    elif king_checked and checking_pieces[0].piece_type in "BRL":
                                        super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass
                            
                            #bottom 2 corners
                            try:
                                if self.coords[1] >= 1 and x != self.coords[0]:
                                    if board[self.coords[1] - 1][x] != 0:
                                        if board[self.coords[1] - 1][x].team != self.team:
                                            if king_checked:
                                                if len(self.pinned_by) == 0:
                                                    if board[self.coords[1] - 1][x] == checking_pieces[0]:
                                                        super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                            else:
                                                if len(self.pinned_by) == 0:
                                                    super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                                else:
                                                    super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    else:
                                        if not king_checked:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                                            super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass
            else:
                for x in range(0,9):
                    for y in range(0,9):
                        if board[y][x] == 0:
                            if not king_checked:
                                super().add_squares(x, y, possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

        if covered_squares[-1] != "hello":
            super().add_current_square(possible_squares, shapelist)

        if len(possible_squares[0]) != 0:
            return possible_squares

    def taken(self, white_board, black_board, itself):
        super().taken(975, 600, 200)
        if self.team == "white":
            if white_board[1][0] != 0:
                white_board[1][0].append(itself)
            else:
                white_board[1][0] = [itself]
        else:
            if black_board[1][0] != 0:
                black_board[1][0].append(itself)
            else:
                black_board[1][0] = [itself]
    
    def calculate_protecting(self, board, covered_squares):
        king_in_range = False
        king_location = [0, 0]
        if not self.captured:
            if self.team == "white":
                for x in range(self.coords[0] - 1, self.coords[0] + 2):
                    #top 3
                    if x != -1:
                        try:
                            if self.coords[1] >= 1:
                                if board[self.coords[1] - 1][x] != 0:
                                    if board[self.coords[1] - 1][x].team == self.team:
                                        covered_squares.append([x, self.coords[1]-1])
                                    elif board[self.coords[1] - 1][x].team != self.team and board[self.coords[1] - 1][x].piece_type == "K":
                                        king_location = [self.coords[1] - 1, x]
                                        king_in_range = True
                                else:
                                    covered_squares.append([x, self.coords[1]-1])
                        except:
                            pass
                        
                        #bottom 2 corners
                        try:
                            if self.coords[1] <= 7 and x != self.coords[0]:
                                if board[self.coords[1] + 1][x] != 0:
                                    if board[self.coords[1] + 1][x].team == self.team:
                                        covered_squares.append([x, self.coords[1]+1])
                                    elif board[self.coords[1] + 1][x].team != self.team and board[self.coords[1] + 1][x].piece_type == "K":
                                        king_location = [self.coords[1] + 1, x]
                                        king_in_range = True
                                else:
                                    covered_squares.append([x, self.coords[1]+1])
                        except:
                            pass
            else:
                for x in range(self.coords[0] - 1, self.coords[0] + 2):
                    #top 3
                    if x != -1:
                        try:
                            if board[self.coords[1] + 1][x] != 0:
                                if board[self.coords[1] + 1][x].team == self.team:
                                    covered_squares.append([x, self.coords[1]+1])
                                elif board[self.coords[1] + 1][x].team != self.team and board[self.coords[1] + 1][x].piece_type == "K":
                                        king_location = [self.coords[1] + 1, x]
                                        king_in_range = True
                            else:
                                covered_squares.append([x, self.coords[1]+1])
                        except:
                            pass
                        
                        #bottom 2 corners
                        try:
                            if self.coords[1] >= 1 and x != self.coords[0]:
                                if board[self.coords[1] - 1][x] != 0:
                                    if board[self.coords[1] - 1][x].team == self.team:
                                        covered_squares.append([x, self.coords[1]-1])
                                    elif board[self.coords[1] - 1][x].team != self.team and board[self.coords[1] - 1][x].piece_type == "K":
                                        king_location = [self.coords[1] - 1, x]
                                        king_in_range = True
                                else:
                                    covered_squares.append([x, self.coords[1]-1])
                        except:
                            pass
            
            return super().check_if_checking(board, king_in_range, king_location)

class Gold(Pieces):
    def __init__(self,team: str,pos: list):
        super().__init__(team, pos)
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", "gold.png"), center_x=self.pos[0], center_y=self.pos[1])
        self.piece_type = "G"

    def highlight_moves(self, shapelist, board, covered_squares, king_checked, checking_pieces):
        possible_squares = super().highlight_moves()

        if len(checking_pieces) <= 1:
            if not self.captured:
                if self.team == "white":
                    for x in range(self.coords[0] - 1, self.coords[0] + 2):
                        if x != -1:
                            #top 3
                            try:
                                if self.coords[1] >= 1:
                                    if board[self.coords[1] - 1][x] != 0:
                                        if board[self.coords[1] - 1][x].team != self.team:
                                            if king_checked:
                                                if len(self.pinned_by) == 0:
                                                    if board[self.coords[1] - 1][x] == checking_pieces[0]:
                                                        super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                            else:
                                                if len(self.pinned_by) == 0:
                                                    super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                                else:
                                                    super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    else:
                                        if not king_checked:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                                            super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass

                            #left and right
                            try:
                                if x != self.coords[0]:
                                    if board[self.coords[1]][x] != 0:
                                        if board[self.coords[1]][x].team != self.team:
                                            if king_checked:
                                                if len(self.pinned_by) == 0:
                                                    if board[self.coords[1]][x] == checking_pieces[0]:
                                                        super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                            else:
                                                if len(self.pinned_by) == 0:
                                                    super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                                else:
                                                    super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    else:
                                        if not king_checked:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                                            super().evaluate_movement(x, self.coords[1], board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass

                            # bottom
                            if self.coords[1] <= 7 and x == self.coords[0]:
                                if board[self.coords[1] + 1][x] != 0:
                                    if board[self.coords[1] + 1][x].team != self.team:
                                        if king_checked:
                                            if len(self.pinned_by) == 0:
                                                if board[self.coords[1] + 1][x] == checking_pieces[0]:
                                                    super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                        else:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                else:
                                    if not king_checked:
                                        if len(self.pinned_by) == 0:
                                            super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                        else:
                                            super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    elif king_checked and checking_pieces[0].piece_type in "BRL":
                                        super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                else:
                    for x in range(self.coords[0] - 1, self.coords[0] + 2):
                        #top 3
                        if x != -1:
                            try:
                                if board[self.coords[1] + 1][x] != 0:
                                    if board[self.coords[1] + 1][x].team != self.team:
                                        if king_checked:
                                            if len(self.pinned_by) == 0:
                                                if board[self.coords[1] + 1][x] == checking_pieces[0]:
                                                    super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                        else:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                else:
                                    if not king_checked:
                                        if len(self.pinned_by) == 0:
                                            super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                        else:
                                            super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    elif king_checked and checking_pieces[0].piece_type in "BRL":
                                        super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass

                            #left and right
                            try:
                                if x != self.coords[0]:
                                    if board[self.coords[1]][x] != 0:
                                        if board[self.coords[1]][x].team != self.team:
                                            if king_checked:
                                                if len(self.pinned_by) == 0:
                                                    if board[self.coords[1]][x] == checking_pieces[0]:
                                                        super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                            else:
                                                if len(self.pinned_by) == 0:
                                                    super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                                else:
                                                    super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    else:
                                        if not king_checked:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                                            super().evaluate_movement(x, self.coords[1], board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass

                            # bottom
                            if self.coords[1] >= 1 and x == self.coords[0]:
                                if board[self.coords[1] - 1][x] != 0:
                                    if board[self.coords[1] - 1][x].team != self.team:
                                        if king_checked:
                                            if len(self.pinned_by) == 0:
                                                if board[self.coords[1] - 1][x] == checking_pieces[0]:
                                                    super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                        else:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                else:
                                    if not king_checked:
                                        if len(self.pinned_by) == 0:
                                            super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                        else:
                                            super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    elif king_checked and checking_pieces[0].piece_type in "BRL":
                                        super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
            else:
                for x in range(0,9):
                    for y in range(0,9):
                        if board[y][x] == 0:
                            if not king_checked:
                                super().add_squares(x, y, possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
        
        if covered_squares[-1] != "hello":
            super().add_current_square(possible_squares, shapelist)

        if len(possible_squares[0]) != 0:
            return possible_squares

    def taken(self, white_board, black_board, itself):
        super().taken(1125, 600, 200)
        if self.team == "white":
            if white_board[1][2] != 0:
                white_board[1][2].append(itself)
            else:
                white_board[1][2] = [itself]
        else:
            if black_board[1][2] != 0:
                black_board[1][2].append(itself)
            else:
                black_board[1][2] = [itself]

    def calculate_protecting(self, board, covered_squares):
        king_in_range = False
        king_location = [0, 0]
        if not self.captured:
            if self.team == "white":
                for x in range(self.coords[0] - 1, self.coords[0] + 2):
                    if x != -1:
                        #top 3
                        try:
                            if self.coords[1] >= 1:
                                if board[self.coords[1] - 1][x] != 0:
                                    if board[self.coords[1] - 1][x].team == self.team:
                                        covered_squares.append([x, self.coords[1]-1])
                                    elif board[self.coords[1] - 1][x].team != self.team and board[self.coords[1] - 1][x].piece_type == "K":
                                        king_location = [self.coords[1] - 1, x]
                                        king_in_range = True
                                else:
                                    covered_squares.append([x, self.coords[1]-1])
                        except:
                            pass

                        #left and right
                        try:
                            if x != self.coords[0]:
                                if board[self.coords[1]][x] != 0:
                                    if board[self.coords[1]][x].team == self.team:
                                        covered_squares.append([x, self.coords[1]])
                                    elif board[self.coords[1]][x].team != self.team and board[self.coords[1]][x].piece_type == "K":
                                        king_location = [self.coords[1], x]
                                        king_in_range = True
                                else:
                                    covered_squares.append([x, self.coords[1]])
                        except:
                            pass

                        # bottom
                        if self.coords[1] <= 7 and x == self.coords[0]:
                            if board[self.coords[1] + 1][x] != 0:
                                if board[self.coords[1] + 1][x].team == self.team:
                                    covered_squares.append([x, self.coords[1]+1])
                                elif board[self.coords[1] + 1][x].team != self.team and board[self.coords[1] + 1][x].piece_type == "K":
                                    king_location = [self.coords[1] + 1, x]
                                    king_in_range = True
                            else:
                                covered_squares.append([x, self.coords[1]+1])

            else:
                for x in range(self.coords[0] - 1, self.coords[0] + 2):
                    #top 3
                    if x != -1:
                        try:
                            if board[self.coords[1] + 1][x] != 0:
                                if board[self.coords[1] + 1][x].team == self.team:
                                    covered_squares.append([x, self.coords[1]+1])
                                elif board[self.coords[1] + 1][x].team != self.team and board[self.coords[1] + 1][x].piece_type == "K":
                                    king_location = [self.coords[1] + 1, x]
                                    king_in_range = True
                            else:
                                covered_squares.append([x, self.coords[1]+1])
                        except:
                            pass

                        #left and right
                        try:
                            if x != self.coords[0]:
                                if board[self.coords[1]][x] != 0:
                                    if board[self.coords[1]][x].team == self.team:
                                        covered_squares.append([x, self.coords[1]+1])
                                    elif board[self.coords[1]][x].team != self.team and board[self.coords[1]][x].piece_type == "K":
                                        king_location = [self.coords[1], x]
                                        king_in_range = True
                                else:
                                    covered_squares.append([x, self.coords[1]])
                        except:
                            pass

                        # bottom
                        if self.coords[1] >= 1 and x == self.coords[0]:
                            if board[self.coords[1] - 1][x] != 0:
                                if board[self.coords[1] - 1][x].team == self.team:
                                    covered_squares.append([x, self.coords[1]-1])
                                elif board[self.coords[1] - 1][x].team != self.team and board[self.coords[1] - 1][x].piece_type == "K":
                                    king_location = [self.coords[1] - 1, x]
                                    king_in_range = True
                            else:
                                covered_squares.append([x, self.coords[1]-1])
            
            return super().check_if_checking(board, king_in_range, king_location)

class King(Pieces):
    def __init__(self,team: str,pos: list):
        super().__init__(team, pos)
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", "king.png"), center_x=self.pos[0], center_y=self.pos[1])
        self.piece_type = "K"
        self.checked = False

    def highlight_moves(self, shapelist, board, covered_squares, king_checked, checking_pieces):
        possible_squares = super().highlight_moves()

        for x in range(self.coords[0] - 1, self.coords[0] + 2):
            #top 3
            if x != -1:
                try:
                    if self.coords[1] >= 1:
                        if [x, self.coords[1] - 1] not in covered_squares:
                            if board[self.coords[1] - 1][x] != 0:
                                if board[self.coords[1] - 1][x].team != self.team:
                                    super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                            else:
                                super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                except:
                    pass

                #left and right
                try:
                    if x != self.coords[0]:
                        if [x, self.coords[1]] not in covered_squares:
                            if board[self.coords[1]][x] != 0:
                                if board[self.coords[1]][x].team != self.team:
                                    super().add_squares(x, self.coords[1], possible_squares, shapelist)
                            else:
                                super().add_squares(x, self.coords[1], possible_squares, shapelist)
                except:
                    pass

                # bottom
                try:
                    if [x, self.coords[1] + 1] not in covered_squares:
                        if board[self.coords[1] + 1][x] != 0:
                            if board[self.coords[1] + 1][x].team != self.team:
                                super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                        else:
                            super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                except:
                    pass

        if covered_squares[-1] != "hello": #prevents adding current square as a possible square if checking for checkmate
            super().add_current_square(possible_squares, shapelist)
            
        if len(possible_squares[0]) != 0:
            return possible_squares

    def calculate_protecting(self, board, covered_squares):
        for x in range(self.coords[0] - 1, self.coords[0] + 2):
            #top 3
            if x != -1:
                try:
                    if self.coords[1] >= 1:
                        if board[self.coords[1] - 1][x] != 0:
                            if board[self.coords[1] - 1][x].team == self.team:
                                covered_squares.append([x, self.coords[1]-1])
                        else:
                            covered_squares.append([x, self.coords[1]-1])
                except:
                    pass

                #left and right
                try:
                    if x != self.coords[0]:
                        if board[self.coords[1]][x] != 0:
                            if board[self.coords[1]][x].team == self.team:
                                covered_squares.append([x, self.coords[1]])
                        else:
                            covered_squares.append([x, self.coords[1]])
                except:
                    pass

                # bottom
                try:
                    if board[self.coords[1] + 1][x] != 0:
                        if board[self.coords[1] + 1][x].team == self.team:
                            covered_squares.append([x, self.coords[1]+1])
                    else:
                        covered_squares.append([x, self.coords[1]-1])
                except:
                    pass

class Promoted_Piece(Pieces):
    def __init__(self,team: str,pos: list, piece_type: str):
        super().__init__(team, pos)
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", piece_type+".png"), center_x=self.pos[0], center_y=self.pos[1])
        self.piece_type = piece_type
        self.promoted = True
    
    def highlight_moves(self, shapelist, board, covered_squares, king_checked, checking_pieces):
        possible_squares = super().highlight_moves()

        if len(checking_pieces) <= 1:
            if not self.captured:
                if self.team == "white":
                    for x in range(self.coords[0] - 1, self.coords[0] + 2):
                        if x != -1:
                            #top 3
                            try:
                                if self.coords[1] >= 1:
                                    if board[self.coords[1] - 1][x] != 0:
                                        if board[self.coords[1] - 1][x].team != self.team:
                                            if king_checked:
                                                if len(self.pinned_by) == 0:
                                                    if board[self.coords[1] - 1][x] == checking_pieces[0]:
                                                        super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                            else:
                                                if len(self.pinned_by) == 0:
                                                    super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                                else:
                                                    super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    else:
                                        if not king_checked:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                                            super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass

                            #left and right
                            try:
                                if x != self.coords[0]:
                                    if board[self.coords[1]][x] != 0:
                                        if board[self.coords[1]][x].team != self.team:
                                            if king_checked:
                                                if len(self.pinned_by) == 0:
                                                    if board[self.coords[1]][x] == checking_pieces[0]:
                                                        super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                            else:
                                                if len(self.pinned_by) == 0:
                                                    super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                                else:
                                                    super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    else:
                                        if not king_checked:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                                            super().evaluate_movement(x, self.coords[1], board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass

                            # bottom
                            if self.coords[1] <= 7 and x == self.coords[0]:
                                if board[self.coords[1] + 1][x] != 0:
                                    if board[self.coords[1] + 1][x].team != self.team:
                                        if king_checked:
                                            if len(self.pinned_by) == 0:
                                                if board[self.coords[1] + 1][x] == checking_pieces[0]:
                                                    super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                        else:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                else:
                                    if not king_checked:
                                        if len(self.pinned_by) == 0:
                                            super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                        else:
                                            super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    elif king_checked and checking_pieces[0].piece_type in "BRL":
                                        super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                else:
                    for x in range(self.coords[0] - 1, self.coords[0] + 2):
                        #top 3
                        if x != -1:
                            try:
                                if board[self.coords[1] + 1][x] != 0:
                                    if board[self.coords[1] + 1][x].team != self.team:
                                        if king_checked:
                                            if len(self.pinned_by) == 0:
                                                if board[self.coords[1] + 1][x] == checking_pieces[0]:
                                                    super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                        else:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                else:
                                    if not king_checked:
                                        if len(self.pinned_by) == 0:
                                            super().add_squares(x, self.coords[1] + 1, possible_squares, shapelist)
                                        else:
                                            super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    elif king_checked and checking_pieces[0].piece_type in "BRL":
                                        super().evaluate_movement(x, self.coords[1] + 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass

                            #left and right
                            try:
                                if x != self.coords[0]:
                                    if board[self.coords[1]][x] != 0:
                                        if board[self.coords[1]][x].team != self.team:
                                            if king_checked:
                                                if len(self.pinned_by) == 0:
                                                    if board[self.coords[1]][x] == checking_pieces[0]:
                                                        super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                            else:
                                                if len(self.pinned_by) == 0:
                                                    super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                                else:
                                                    super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    else:
                                        if not king_checked:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                                            super().evaluate_movement(x, self.coords[1], board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                            except:
                                pass

                            # bottom
                            if self.coords[1] >= 1 and x == self.coords[0]:
                                if board[self.coords[1] - 1][x] != 0:
                                    if board[self.coords[1] - 1][x].team != self.team:
                                        if king_checked:
                                            if len(self.pinned_by) == 0:
                                                if board[self.coords[1] - 1][x] == checking_pieces[0]:
                                                    super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                        else:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                else:
                                    if not king_checked:
                                        if len(self.pinned_by) == 0:
                                            super().add_squares(x, self.coords[1] - 1, possible_squares, shapelist)
                                        else:
                                            super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    elif king_checked and checking_pieces[0].piece_type in "BRL":
                                        super().evaluate_movement(x, self.coords[1] - 1, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                        
        if covered_squares[-1] != "hello":
            super().add_current_square(possible_squares, shapelist)

        if len(possible_squares[0]) != 0:
            return possible_squares

    def taken(self, white_board, black_board, itself):
        super().taken(1125, 600, 200)
        if self.team == "white":
            if white_board[1][2] != 0:
                white_board[1][2].append(itself)
            else:
                white_board[1][2] = [itself]
        else:
            if black_board[1][2] != 0:
                black_board[1][2].append(itself)
            else:
                black_board[1][2] = [itself]

    def demote(self):
        if self.piece_type == "P":
            return Pawn(self.team, self.pos)
        elif self.piece_type == "N":
            return Knight(self.team, self.pos)
        elif self.piece_type == "L":
            return Lance(self.team, self.pos)
        elif self.piece_type == "S":
            return Silver(self.team, self.pos)

    def calculate_protecting(self, board, covered_squares):
        king_in_range = False
        king_location = [0, 0]
        if not self.captured:
            if self.team == "white":
                for x in range(self.coords[0] - 1, self.coords[0] + 2):
                    if x != -1:
                        #top 3
                        try:
                            if self.coords[1] >= 1:
                                if board[self.coords[1] - 1][x] != 0:
                                    if board[self.coords[1] - 1][x].team == self.team:
                                        covered_squares.append([x, self.coords[1]-1])
                                    elif board[self.coords[1] - 1][x].team != self.team and board[self.coords[1] - 1][x].piece_type == "K":
                                        king_location = [self.coords[1] - 1, x]
                                        king_in_range = True
                                else:
                                    covered_squares.append([x, self.coords[1]-1])
                        except:
                            pass

                        #left and right
                        try:
                            if x != self.coords[0]:
                                if board[self.coords[1]][x] != 0:
                                    if board[self.coords[1]][x].team == self.team:
                                        covered_squares.append([x, self.coords[1]])
                                    elif board[self.coords[1]][x].team != self.team and board[self.coords[1]][x].piece_type == "K":
                                        king_location = [self.coords[1], x]
                                        king_in_range = True
                                else:
                                    covered_squares.append([x, self.coords[1]])
                        except:
                            pass

                        # bottom
                        if self.coords[1] <= 7 and x == self.coords[0]:
                            if board[self.coords[1] + 1][x] != 0:
                                if board[self.coords[1] + 1][x].team == self.team:
                                    covered_squares.append([x, self.coords[1]+1])
                                elif board[self.coords[1] + 1][x].team != self.team and board[self.coords[1] + 1][x].piece_type == "K":
                                    king_location = [self.coords[1] + 1, x]
                                    king_in_range = True
                            else:
                                covered_squares.append([x, self.coords[1]+1])

            else:
                for x in range(self.coords[0] - 1, self.coords[0] + 2):
                    #top 3
                    if x != -1:
                        try:
                            if board[self.coords[1] + 1][x] != 0:
                                if board[self.coords[1] + 1][x].team == self.team:
                                    covered_squares.append([x, self.coords[1]+1])
                                elif board[self.coords[1] + 1][x].team != self.team and board[self.coords[1] + 1][x].piece_type == "K":
                                    king_location = [self.coords[1] + 1, x]
                                    king_in_range = True
                            else:
                                covered_squares.append([x, self.coords[1]+1])
                        except:
                            pass

                        #left and right
                        try:
                            if x != self.coords[0]:
                                if board[self.coords[1]][x] != 0:
                                    if board[self.coords[1]][x].team == self.team:
                                        covered_squares.append([x, self.coords[1]+1])
                                    elif board[self.coords[1]][x].team != self.team and board[self.coords[1]][x].piece_type == "K":
                                        king_location = [self.coords[1], x]
                                        king_in_range = True
                                else:
                                    covered_squares.append([x, self.coords[1]])
                        except:
                            pass

                        # bottom
                        if self.coords[1] >= 1 and x == self.coords[0]:
                            if board[self.coords[1] - 1][x] != 0:
                                if board[self.coords[1] - 1][x].team == self.team:
                                    covered_squares.append([x, self.coords[1]-1])
                                elif board[self.coords[1] - 1][x].team != self.team and board[self.coords[1] - 1][x].piece_type == "K":
                                    king_location = [self.coords[1] - 1, x]
                                    king_in_range = True
                            else:
                                covered_squares.append([x, self.coords[1]-1])
            
            return super().check_if_checking(board, king_in_range, king_location)

class Promoted_Rook(Pieces):
    def __init__(self,team: str,pos: list):
        super().__init__(team, pos)
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", "R.png"), center_x=self.pos[0], center_y=self.pos[1])
        self.piece_type = "R"
        self.promoted = True

    def highlight_moves(self, shapelist, board, covered_squares, king_checked, checking_pieces):
        possible_squares = super().highlight_moves()

        if len(checking_pieces) <= 1:
            if not self.captured:
                for y in range(self.coords[1] - 1, -1, -1):
                    if board[y][self.coords[0]] != 0:
                        if board[y][self.coords[0]].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][self.coords[0]] == checking_pieces[0]:
                                        super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(self.coords[0], y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(self.coords[0], y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #down
                for y in range(self.coords[1] + 1, 9):
                    if board[y][self.coords[0]] != 0:
                        if board[y][self.coords[0]].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][self.coords[0]] == checking_pieces[0]:
                                        super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(self.coords[0], y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(self.coords[0], y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                
                #right
                for x in range(self.coords[0] + 1, 9):
                    if board[self.coords[1]][x] != 0:
                        if board[self.coords[1]][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[self.coords[1]][x] == checking_pieces[0]:
                                        super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, self.coords[1], possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, self.coords[1], board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #left
                for x in range(self.coords[0] - 1, -1, -1):
                    if board[self.coords[1]][x] != 0:
                        if board[self.coords[1]][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[self.coords[1]][x] == checking_pieces[0]:
                                        super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, self.coords[1], possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, self.coords[1], board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #diagonals
                for x in range(self.coords[0]-1, self.coords[0]+2, 2):
                    if x != -1 and x != 9:
                        for y in range(self.coords[1]-1, self.coords[1]+2, 2):
                            if y != -1 and y != 9:
                                if board[y][x] != 0:
                                    if board[y][x].team != self.team:
                                        if king_checked:
                                            if len(self.pinned_by) == 0:
                                                if board[y][x] == checking_pieces[0]:
                                                    super().add_squares(x, y, possible_squares, shapelist)
                                        else:
                                            if len(self.pinned_by) == 0:
                                                super().add_squares(x, y, possible_squares, shapelist)
                                            else:
                                                super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                else:
                                    if not king_checked:
                                        if len(self.pinned_by) == 0:
                                            super().add_squares(x, y, possible_squares, shapelist)
                                        else:
                                            super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    elif king_checked and checking_pieces[0].piece_type in "BRL":
                                        super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

        if covered_squares[-1] != "hello":
            super().add_current_square(possible_squares, shapelist)

        if len(possible_squares[0]) != 0:
            return possible_squares

    def taken(self, white_board, black_board, itself):
        super().taken(1125, 675, 125)
        if self.team == "white":
            if white_board[2][2] != 0:
                white_board[2][2].append(itself)
            else:
                white_board[2][2] = [itself]
        else:
            if black_board[0][2] != 0:
                black_board[0][2].append(itself)
            else:
                black_board[0][2] = [itself]

    def demote(self):
        return Rook(self.team, self.pos)

    def calculate_protecting(self, board, covered_squares):
        king_in_range = False
        king_location = [0, 0]
        if not self.captured:
            #up
            pieces_encountered = 0
            for y in range(self.coords[1] - 1, -1, -1):
                if board[y][self.coords[0]] != 0:
                    if board[y][self.coords[0]].team == self.team:
                        covered_squares.append([self.coords[0], y])
                        break
                    elif board[y][self.coords[0]].team != self.team and board[y][self.coords[0]].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, self.coords[0]]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][self.coords[0]]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([self.coords[0], y])

            #down
            pieces_encountered = 0
            for y in range(self.coords[1] + 1, 9):
                if board[y][self.coords[0]] != 0:
                    if board[y][self.coords[0]].team == self.team:
                        covered_squares.append([self.coords[0], y])
                        break
                    elif board[y][self.coords[0]].team != self.team and board[y][self.coords[0]].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, self.coords[0]]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][self.coords[0]]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([self.coords[0], y])
            
            #right
            pieces_encountered = 0
            for x in range(self.coords[0] + 1, 9):
                if board[self.coords[1]][x] != 0:
                    if board[self.coords[1]][x].team == self.team:
                        covered_squares.append([x, self.coords[1]])
                        break
                    elif board[self.coords[1]][x].team != self.team and board[self.coords[1]][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [self.coords[1], x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[self.coords[1]][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, self.coords[1]])

            #left
            pieces_encountered = 0
            for x in range(self.coords[0] - 1, -1, -1):
                if board[self.coords[1]][x] != 0:
                    if board[self.coords[1]][x].team == self.team:
                        covered_squares.append([x, self.coords[1]])
                        break
                    elif board[self.coords[1]][x].team != self.team and board[self.coords[1]][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [self.coords[1], x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[self.coords[1]][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, self.coords[1]])

            #diagonals
            for x in range(self.coords[0]-1, self.coords[0]+2, 2):
                if x != -1 and x != 9:
                    for y in range(self.coords[1]-1, self.coords[1]+2, 2):
                        if y != -1 and y != 9:
                            if board[y][x] != 0:
                                if board[y][x].team == self.team:
                                    covered_squares.append([x, y])
                                elif board[y][x].team != self.team and board[y][x].piece_type == "K":
                                    king_location = [y, x]
                                    king_in_range = True
                            else:
                                covered_squares.append([x, y])

            return super().check_if_checking(board, king_in_range, king_location)

class Promoted_Bishop(Pieces):
    def __init__(self,team: str,pos: list):
        super().__init__(team, pos)
        self.sprite = arcade.Sprite(os.path.join(sys.path[0], "sprites", "B.png"), center_x=self.pos[0], center_y=self.pos[1])
        self.piece_type = "B"
        self.promoted = True

    def highlight_moves(self, shapelist, board, covered_squares, king_checked, checking_pieces):
        possible_squares = super().highlight_moves()

        if len(checking_pieces) <= 1:
            if not self.captured:
                #up-right diagonal
                for x, y in zip(range(self.coords[0] + 1, 9), range(self.coords[1] - 1, -1, -1)):
                    if board[y][x] != 0:
                        if board[y][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][x] == checking_pieces[0]:
                                        super().add_squares(x, y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #up-left diagonal
                for x, y in zip(range(self.coords[0] - 1, -1, -1), range(self.coords[1] - 1, -1, -1)):
                    if board[y][x] != 0:
                        if board[y][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][x] == checking_pieces[0]:
                                        super().add_squares(x, y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #down-right diagonal
                for x, y in zip(range(self.coords[0] + 1, 9), range(self.coords[1] + 1, 9)):
                    if board[y][x] != 0:
                        if board[y][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][x] == checking_pieces[0]:
                                        super().add_squares(x, y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #down-left diagonal
                for x, y in zip(range(self.coords[0] - 1, -1, -1), range(self.coords[1] + 1, 9,)):
                    if board[y][x] != 0:
                        if board[y][x].team != self.team:
                            if king_checked:
                                if len(self.pinned_by) == 0:
                                    if board[y][x] == checking_pieces[0]:
                                        super().add_squares(x, y, possible_squares, shapelist)
                                        break
                            else:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, y, possible_squares, shapelist)
                                    break
                                else:
                                    super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                                    break
                        else:
                            break
                    else:
                        if not king_checked:
                            if len(self.pinned_by) == 0:
                                super().add_squares(x, y, possible_squares, shapelist)
                            else:
                                super().evaluate_movement(x, y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        elif king_checked and checking_pieces[0].piece_type in "BRL":
                            super().evaluate_movement(x, y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

                #cross
                for x in range(self.coords[0]-1, self.coords[0]+2, 2):
                    if x != -1 and x != 9:
                        if board[self.coords[1]][x] != 0:
                            if board[self.coords[1]][x].team != self.team:
                                if king_checked:
                                    if len(self.pinned_by) == 0:
                                        if board[self.coords[1]][x] == checking_pieces[0]:
                                            super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                else:
                                    if len(self.pinned_by) == 0:
                                        super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                    else:
                                        super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        else:
                            if not king_checked:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(x, self.coords[1], possible_squares, shapelist)
                                else:
                                    super().evaluate_movement(x, self.coords[1], board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(x, self.coords[1], board, covered_squares, checking_pieces[0], possible_squares, shapelist)
                for y in range(self.coords[1]-1, self.coords[1]+2, 2):
                    if y != -1 and y != 9:
                        if board[y][self.coords[0]] != 0:
                            if board[y][self.coords[0]].team != self.team:
                                if king_checked:
                                    if len(self.pinned_by) == 0:
                                        if board[y][self.coords[0]] == checking_pieces[0]:
                                            super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                else:
                                    if len(self.pinned_by) == 0:
                                        super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                    else:
                                        super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                        else:
                            if not king_checked:
                                if len(self.pinned_by) == 0:
                                    super().add_squares(self.coords[0], y, possible_squares, shapelist)
                                else:
                                    super().evaluate_movement(self.coords[0], y, board, covered_squares, self.pinned_by[0], possible_squares, shapelist)
                            elif king_checked and checking_pieces[0].piece_type in "BRL":
                                super().evaluate_movement(self.coords[0], y, board, covered_squares, checking_pieces[0], possible_squares, shapelist)

        if covered_squares[-1] != "hello":
            super().add_current_square(possible_squares, shapelist)

        if len(possible_squares[0]) != 0:
            return possible_squares

    def taken(self, white_board, black_board, itself):
        super().taken(975, 675, 125)
        if self.team == "white":
            if white_board[2][0] != 0:
                white_board[2][0].append(itself)
            else:
                white_board[2][0] = [itself]
        else:
            if black_board[0][0] != 0:
                black_board[0][0].append(itself)
            else:
                black_board[0][0] = [itself]

    def demote(self):
        return Bishop(self.team, self.pos)

    def calculate_protecting(self, board, covered_squares):
        king_in_range = False
        king_location = [0, 0]
        if not self.captured:

            #up-right diagonal
            pieces_encountered = 0
            for x, y in zip(range(self.coords[0] + 1, 9), range(self.coords[1] - 1, -1, -1)):
                if board[y][x] != 0:
                    if board[y][x].team == self.team:
                        covered_squares.append([x, y])
                        break
                    elif board[y][x].team != self.team and board[y][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, y])
            
            #up-left diagonal
            pieces_encountered = 0
            for x, y in zip(range(self.coords[0] - 1, -1, -1), range(self.coords[1] - 1, -1, -1)):
                if board[y][x] != 0:
                    if board[y][x].team == self.team:
                        covered_squares.append([x, y])
                        break
                    elif board[y][x].team != self.team and board[y][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, y])

            #down-right diagonal
            for x, y in zip(range(self.coords[0] + 1, 9), range(self.coords[1] + 1, 9)):
                if board[y][x] != 0:
                    if board[y][x].team == self.team:
                        covered_squares.append([x, y])
                        break
                    elif board[y][x].team != self.team and board[y][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, y])

            #down-left diagonal
            for x, y in zip(range(self.coords[0] - 1, -1, -1), range(self.coords[1] + 1, 9,)):
                if board[y][x] != 0:
                    if board[y][x].team == self.team:
                        covered_squares.append([x, y])
                        break
                    elif board[y][x].team != self.team and board[y][x].piece_type == "K":
                        if pieces_encountered == 0:
                            king_location = [y, x]
                            king_in_range = True
                        elif pieces_encountered == 1:
                            potentially_pinned.pinned_by.append(self)
                    else:
                        pieces_encountered += 1
                        potentially_pinned = board[y][x]
                        if pieces_encountered == 2:
                            break
                else:
                    if pieces_encountered == 0:
                        covered_squares.append([x, y])

            #cross
            for x in range(self.coords[0]-1, self.coords[0]+2, 2):
                if x != -1 and x != 9:
                    if board[self.coords[1]][x] != 0:
                        if board[self.coords[1]][x].team == self.team:
                            covered_squares.append([x, self.coords[1]])
                        elif board[self.coords[1]][x].team != self.team and board[self.coords[1]][x].piece_type == "K":
                            king_location = [y, x]
                            king_in_range = True
                    else:
                        covered_squares.append([x, self.coords[1]])
            for y in range(self.coords[1]-1, self.coords[1]+2, 2):
                if y != -1 and y != 9:
                    if board[y][self.coords[0]] != 0:
                        if board[y][self.coords[0]].team == self.team:
                            covered_squares.append([self.coords[0], y])
                        elif board[y][self.coords[0]].team != self.team and board[y][self.coords[0]].piece_type == "K":
                            king_location = [y, self.coords[0]]
                            king_in_range = True
                    else:
                        covered_squares.append([self.coords[0], y])

            return super().check_if_checking(board, king_in_range, king_location)

board_map = [[[x,y] for x in range(170, 845, 75)] for y in range(700, 25, -75)]
