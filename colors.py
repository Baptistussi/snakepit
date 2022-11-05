import random

colors = { 'BEIGE' : (245, 245, 220),
            'BLUE' : (0, 0, 255),
            'BROWN' : (165, 42, 42),
            'GOLD' : (255, 215, 0),
            'GRAY' : (128, 128, 128),
            'GREEN' : (0, 128, 0),
            'ORANGE' : (255, 128, 0),
            'PINK' : (255, 192, 203),
            'PURPLE' : (128, 0, 128),
            'VIOLET' : (238, 130, 238),
            'YELLOW1' : (255, 255, 0) }

def get_random_color():
    k = random.choice(list(colors.keys()))
    color = colors[k]
    colors.pop(k)
    return k, color