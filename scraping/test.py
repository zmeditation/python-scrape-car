from colour import Color


def check_color(color):
    try:
        Color(color)
        return True
    except ValueError:
        return False
    

s = 'Drab Green Paintwork'

_color = [i for i in s.split(' ') if check_color(i)]

print(_color)
