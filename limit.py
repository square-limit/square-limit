
import turtle
import Tkinter

# vector
def make_vector(x, y):
    return (x, y)

def xcoor_vector(vector):
    return vector[0]

def ycoor_vector(vector):
    return vector[1]

def scale_vector(m, v):
    return make_vector(m * xcoor_vector(v), m * ycoor_vector(v))

def add_vector(v1, v2):
    return make_vector(xcoor_vector(v1) + xcoor_vector(v2), ycoor_vector(v1) + ycoor_vector(v2))

def sub_vector(v1, v2):
    return make_vector(xcoor_vector(v1) - xcoor_vector(v2), ycoor_vector(v1) - ycoor_vector(v2))

# frame
def make_frame(orig, edge1, edge2):
    return (orig, edge1, edge2)

def origin_frame(frame):
    return frame[0]

def edge1_frame(frame):
    return frame[1]

def edge2_frame(frame):
    return frame[2]

# Segment
def start_segment(seg):
    return seg[0]

def end_segment(seg):
    return seg[1]

def make_seg(point1, point2):
    return (point1, point2)

# coordinate
def frame_coord_map(frame):
    def assign_vector(v):
        return add_vector(
            origin_frame(frame),
            add_vector(
                scale_vector(xcoor_vector(v), edge1_frame(frame)),
                scale_vector(ycoor_vector(v), edge2_frame(frame))))
    return assign_vector

def transform_painter(painter, origin, corner1, corner2):
    def f(frame):
        cm = frame_coord_map(frame)
        new_origin = cm(origin)
        return painter(make_frame(
            new_origin,
            sub_vector(cm(corner1), new_origin),
            sub_vector(cm(corner2), new_origin)))
    return f

def join(painter1, painter2):
    def f(frame):
        def d(draw_line):
            (painter1(frame))(draw_line)
            (painter2(frame))(draw_line)
        return d
    return f

def EMPTY(frame):
    def assign_draw(draw_line):
        pass
    return assign_draw

def beside(left, right, ratio):
    split_point = make_vector(ratio, 0.0)
    paint_left = transform_painter(left,
        make_vector(0.0, 0.0),
        split_point,
        make_vector(0.0, 1.0))
    paint_right = transform_painter(right,
        split_point,
        make_vector(1.0, 0.0),
        make_vector(ratio, 1.0))
    return join(paint_left, paint_right)

def below(bottom, top, ratio):
    split_point = make_vector(0.0, ratio)
    paint_bottom = transform_painter(bottom,
        make_vector(0.0, 0.0),
        make_vector(1.0, 0.0),
        split_point)
    paint_top = transform_painter(top,
        split_point,
        make_vector(1.0, ratio),
        make_vector(0.0, 1.0))
    return join(paint_bottom, paint_top)

def identity(painter):
    return transform_painter(painter,
        make_vector(0.0, 0.0),
        make_vector(1.0, 0.0),
        make_vector(0.0, 1.0))

def rotate_45(painter):
    return transform_painter(painter,
        make_vector(0, 0.5),
        make_vector(0.5, 0.0),
        make_vector(0.5, 1.0))

def rotate_90(painter):
    return transform_painter(painter,
        make_vector(0.0, 1.0),
        make_vector(0.0, 0.0),
        make_vector(1.0, 1.0))

def rotate_180(painter):
    return transform_painter(painter,
        make_vector(1.0, 1.0),
        make_vector(0.0, 1.0),
        make_vector(1.0, 0.0))

def rotate_270(painter):
    return transform_painter(painter,
        make_vector(1.0, 0.0),
        make_vector(1.0, 1.0),
        make_vector(0.0, 0.0))

def flip_horiz(painter):
    return transform_painter(painter,
        make_vector(1.0, 0.0),
        make_vector(0.0, 0.0),
        make_vector(1.0, 1.0))

def flip_vert(painter):
    return transform_painter(painter,
        make_vector(0.0, 1.0),
        make_vector(1.0, 1.0),
        make_vector(0.0, 0.0))

def rhombus(painter, ratio = 0.7):
    return transform_painter(painter,
        make_vector(0.0, 0.0),
        make_vector(ratio, 1.0 - ratio),
        make_vector(1.0 - ratio, ratio))

def right_split(painter, n, ratio):
    right = right_split(painter, n - 1, ratio) if n > 1 else painter
    return beside(painter, below(right, right, 0.5), ratio)

def up_split(painter, n, ratio):
    return rotate_270(right_split(rotate_90(painter), n, ratio))

def corner_split(painter, n, ratio):
    up = up_split(painter, n - 1, ratio) if n > 1 else painter
    right = right_split(painter, n - 1, ratio) if n > 1 else painter
    top_right = corner_split(painter, n - 1, ratio) if n > 1 else painter
    top_left = beside(up, up, 0.5)
    bottom_right = below(right, right, 0.5)
    return below(
        beside(painter, bottom_right, 0.5),
        beside(top_left, top_right, 0.5),
        0.5)

def square_of_foor(bl, br, tl, tr):
    def p(painter):
        bottom = beside(bl(painter), br(painter), 0.5)
        top = beside(tl(painter), tr(painter), 0.5)
        return below(bottom, top, 0.5)
    return p

def square_limit(painter, n):
    corner = corner_split(painter, n, 0.5)
    return square_of_foor(rotate_180, flip_vert, flip_horiz, identity)(corner)

def flipped_pairs(painter):
    return square_of_foor(identity, flip_horiz, flip_vert, rotate_180)(painter)

def diagonal(painter):
    empty = lambda p: EMPTY
    return square_of_foor(empty, identity, identity, empty)(painter)

def paris(painter):
    return square_of_foor(identity, identity, identity, identity)(painter)


# draw
def segs_painter(segs):
    def assign_frame(frame):
        def assign_draw(draw_line):
            cm = frame_coord_map(frame)
            map(lambda seg: draw_line(
                cm(start_segment(seg)),
                cm(end_segment(seg))), segs)
        return assign_draw
    return assign_frame

SIZE = 200
def turtle_draw(a, b):
    turtle.pencolor('blue')
    turtle.penup()
    turtle.goto(a)
    turtle.pendown()
    turtle.goto(b)

class Canvas:
    OFFSET = SIZE * 1.1
    def __init__(self):
        self.top = Tkinter.Tk()
        self.canvas = Tkinter.Canvas(self.top, bg = 'white', width = self.OFFSET * 2, height = self.OFFSET * 2)

    def line(self, a, b):
        self.canvas.create_line(
            self.OFFSET + xcoor_vector(a), self.OFFSET - ycoor_vector(a),
            self.OFFSET + xcoor_vector(b), self.OFFSET - ycoor_vector(b),
            fill = 'blue')

    def show(self):
        self.canvas.pack()
        self.top.mainloop()

# draw base
SEGMENTS = [
    make_seg(make_vector(0.25, 0.5), make_vector(0, 1)),
    make_seg(make_vector(0, 1), make_vector(0.5, 1)),
    make_seg(make_vector(0.5, 1), make_vector(0.25, 0.5)),
    make_seg(make_vector(0.25, 0.5), make_vector(0.75, 0.5)),
    make_seg(make_vector(0.75, 0.5), make_vector(0.5, 0)),
    make_seg(make_vector(0.5, 0), make_vector(1, 0)),
    make_seg(make_vector(1, 0), make_vector(0.75, 0.5)),
]
G = segs_painter(SEGMENTS)
FRAME = make_frame((-SIZE, -SIZE), (SIZE * 2, 0), (0, SIZE * 2))

def draw_by_turtle(draw):
    turtle.resizemode('auto')
    turtle.speed('fastest')
    draw(FRAME)(turtle_draw)
    turtle.hideturtle()
    turtle.exitonclick()

def draw_by_tk(draw):
    canvas = Canvas()
    draw(FRAME)(canvas.line)
    canvas.show()

pic_base = rhombus(flip_vert(G))
pic_beside = beside(G, G, 0.5)
pic_below = below(G, G, 0.5)
pic_rotate_90 = rotate_90(G)
pic_flip_horiz = flip_horiz(G)
pic_flip_vert = flip_vert(G)
pic_right_split = right_split(G, 4, 0.5)
pic_corner_split = corner_split(G, 4, 0.5)
pic_square_limit = square_limit(identity(flip_vert(G)), 4)
pic_rotate_45 = rotate_45(square_limit(identity(flip_vert(G)), 4))
pic_rhombus = rhombus(square_limit(flipped_pairs(flip_vert(G)), 4))
pic_composite1 = rotate_45(square_limit(flipped_pairs(rhombus(flip_vert(G))), 4))
pic_composite2 = rotate_45(square_limit(flipped_pairs(flipped_pairs(rhombus(flip_vert(G)))), 4))
pic_composite3 = diagonal(square_limit(flipped_pairs(flipped_pairs(rhombus(flip_vert(G)))), 4))
pic_composite4 = rotate_45(diagonal(square_limit(flipped_pairs(flipped_pairs(rhombus(flip_vert(G)))), 3)))
pic_composite5 = paris(diagonal(square_limit(flipped_pairs(flipped_pairs(rhombus(flip_vert(G)))), 2)))

def draw_pictures(draw):
    pictures = [
        pic_base,
        pic_beside,
        pic_below,
        pic_rotate_90,
        pic_flip_horiz,
        pic_flip_vert,
        pic_right_split,
        pic_corner_split,
        pic_square_limit,
        pic_rotate_45,
        pic_rhombus,
        pic_composite1,
        pic_composite2,
        pic_composite3,
        pic_composite4,
        pic_composite5,
        ]
    map(draw, pictures)

if __name__ == "__main__":
    # draw_pictures(draw_by_turtle)
    draw_pictures(draw_by_tk)
