# ==================== CAMERA ====================
class Camera:
    def __init__(self, screen_w, screen_h, map_size):
        self.x=0.0; self.y=0.0
        self.screen_w=screen_w; self.screen_h=screen_h
        self.map_size=map_size
        self.speed=18.0
        self.following=None
    def center_on(self, tx, ty, smooth=False):
        ttx=tx-self.screen_w/2; tty=ty-self.screen_h/2
        if smooth:
            self.x+=(ttx-self.x)*0.1; self.y+=(tty-self.y)*0.1
        else:
            self.x=ttx; self.y=tty
        self._clamp()
    def move(self,dx,dy):
        self.x+=dx*self.speed; self.y+=dy*self.speed
        self.following=None; self._clamp()
    def _clamp(self):
        self.x=max(0,min(self.x,self.map_size-self.screen_w))
        self.y=max(0,min(self.y,self.map_size-self.screen_h))
    def world_to_screen(self,wx,wy):
        return int(wx-self.x), int(wy-self.y)
    def is_visible(self,wx,wy,margin=65):
        return (-margin<wx-self.x<self.screen_w+margin and
                -margin<wy-self.y<self.screen_h+margin)
    def is_rect_visible(self,rx,ry,rw,rh,margin=65):
        return not (rx+rw<self.x-margin or rx>self.x+self.screen_w+margin or
                    ry+rh<self.y-margin or ry>self.y+self.screen_h+margin)
