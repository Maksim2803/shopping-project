class MenuManager:
    def __init__(self):
        self.admin_buttons={"start":[["Очистить список","Полный список"],["Добавить кнопку","Удалить кнопку"]],"categories":[["Назад"]]}

    def creation_button(self,board):
        new_keyboard = [[]]
        board=list(board.keys())
        board.append("Стоп")
        for i in board:
            for row in new_keyboard:
                if len(row) < 4:
                    row.append(i)
                    break
            else:
                new_keyboard.append([i])
        return new_keyboard

    def add_button_part1(self,button,category,board):
        if not category:
            return "category not selected"
        button=self.name_check(button,category,board)
        if button=="name is taken" or button=="name name unavailable":
            return button
        board_spisok=self.unpacking(board[category])
        admin_spisok=self.unpacking(self.admin_buttons)
        new_board=[]
        for i in range(len(board_spisok)):
            if board_spisok[i] in admin_spisok:
                continue
            else:
                new_board.append(board_spisok[i])
        new_board.append(button)
        return self.add_button_part2(new_board,button,category,board)

    def add_button_part2(self,new_board,button,category,board):
        custom_buttons=[[]]
        for i in new_board:
            for row in custom_buttons:
                if len(row)<3:
                    row.append(i)
                    break
            else:
                custom_buttons.append([i])
        if category=="Главное меню":
            custom_buttons.extend(self.admin_buttons["start"])
            board[button]=[["Назад"]]
        else:
            custom_buttons.extend(self.admin_buttons["categories"])
        board[category]=custom_buttons
        return category

    def delete_buttons(self,button,category,board):
        try:
            board_spisok=board[category]
        except KeyError:
            return "KeyError"
        if self.check_delete_buttons(button)=="prohibited for removal":
            return "prohibited for removal"
        for i in board_spisok:
            for b in i:
                if b==button:
                    i.remove(b)
                    board.pop(b,None)
        board[category]=board_spisok
        return category

    def check_delete_buttons(self,button):
        admin_spisok = self.unpacking(self.admin_buttons)
        if button in admin_spisok:
            return "prohibited for removal"
        return button


    def check_isdigit(self,quantity):
        if quantity.isdigit():
            return quantity
        else:
            return None

    def unpacking(self,spisok):
        if isinstance(spisok,dict):
            result=[]
            for key,values in spisok.items():
                result.extend(self.unpacking(values))
            return result
        if isinstance(spisok,list):
            result=[]
            for i in spisok:
                result.extend(self.unpacking(i))
            return result
        else:
            return [spisok]

    def name_check(self,name,category,board):
        board_spisok=self.unpacking(board[category])
        admin_spisok=self.unpacking(self.admin_buttons)
        if name in board_spisok:
            return "name is taken"
        elif name in admin_spisok:
            return "name unavailable"
        else:
            return name










