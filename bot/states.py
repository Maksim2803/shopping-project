class StateManager:
    def __init__(self):
        self.user_state={}
    def give_state(self,user_id,state):
        self.user_state[user_id]=state
    def get_state(self,user_id):
        return self.user_state[user_id]
    def clear_state(self,user_id):
        self.user_state.pop(user_id,None)