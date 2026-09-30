# ==================== KILL FEED ====================
class KillEntry:
    def __init__(self, killer, victim, weapon):
        self.killer=killer
        self.victim=victim
        self.weapon=weapon
        self.life=self.max_life=255
