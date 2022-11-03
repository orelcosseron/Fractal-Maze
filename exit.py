class Exit():
    def __init__(self, name, orientation, x, y):
        self.id = int(name)
        self.orientation = int(orientation)
        self.x = x
        self.y = y

    def setPixmap(self, pixmap):
        self.pixmap = pixmap

    def show(self):
        self.pixmap.show()

    def hide(self):
        self.pixmap.hide()
