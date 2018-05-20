class Transition:
    """Represents a transition between two states"""
    def __init__(self, start, joint_action, end):
        """Create a new transition"""
        self.start = start
        self.joint_action = tuple(joint_action)
        self.end = end
    def __getitem__(self, index):
        """Get the action of a certain player"""
        return self.joint_action[index]
    def __repr__(self):
        return str(self)
    def __str__(self):
        return str(self.start) + " --" + str(self.joint_action) + "-> " + str(self.end)
        
    def label(self):
        """Return the string representation of the joint action"""
        if len(self.joint_action) > 1:
            return "(" + ", ".join(self.joint_action) + ")"
        else:
            return str(self.joint_action[0])
