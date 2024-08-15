import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageEnhance, ImageFilter
import random
import math

class AdvancedFaceCreator:
    def __init__(self, master):
        self.master = master
        master.title("Advanced Face Creator")

        self.color_map = {
            'very fair': (255, 224, 189),
            'fair': (255, 205, 148),
            'medium': (234, 192, 134),
            'olive': (255, 233, 194),
            'brown': (141, 85, 36),
            'dark': (78, 67, 63),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'gray': (128, 128, 128),
        }

        self.features = {
            'face_shape': tk.StringVar(value='oval'),
            'skin_tone': tk.StringVar(value='medium'),
            'skin_texture': tk.StringVar(value='smooth'),
            'age': tk.IntVar(value=30),
            'eye_shape': tk.StringVar(value='almond'),
            'eye_color': tk.StringVar(value='brown'),
            'eye_distance': tk.DoubleVar(value=1.0),
            'eyebrow_shape': tk.StringVar(value='arched'),
            'eyebrow_thickness': tk.DoubleVar(value=1.0),
            'nose_shape': tk.StringVar(value='straight'),
            'nose_size': tk.DoubleVar(value=1.0),
            'mouth_shape': tk.StringVar(value='full'),
            'mouth_size': tk.DoubleVar(value=1.0),
            'lip_thickness': tk.DoubleVar(value=1.0),
            'cheekbone_prominence': tk.DoubleVar(value=1.0),
            'jaw_shape': tk.StringVar(value='rounded'),
            'chin_shape': tk.StringVar(value='rounded'),
            'hair_style': tk.StringVar(value='short'),
            'hair_color': tk.StringVar(value='black'),
            'hair_texture': tk.StringVar(value='straight'),
            'facial_hair': tk.StringVar(value='none'),
            'freckles': tk.BooleanVar(value=False),
            'moles': tk.BooleanVar(value=False),
            'glasses': tk.StringVar(value='none'),
            'expression': tk.StringVar(value='neutral'),
        }

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        categories = [
            ("Face", ['face_shape', 'skin_tone', 'skin_texture', 'age', 'cheekbone_prominence', 'jaw_shape', 'chin_shape']),
            ("Eyes", ['eye_shape', 'eye_color', 'eye_distance', 'eyebrow_shape', 'eyebrow_thickness']),
            ("Nose & Mouth", ['nose_shape', 'nose_size', 'mouth_shape', 'mouth_size', 'lip_thickness']),
            ("Hair", ['hair_style', 'hair_color', 'hair_texture', 'facial_hair']),
            ("Additional", ['freckles', 'moles', 'glasses', 'expression'])
        ]

        for category, features in categories:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=category)
            self.create_category_widgets(frame, features)

        self.canvas = tk.Canvas(self.master, width=600, height=800, bg='white')
        self.canvas.pack(padx=10, pady=10)

        # Initial face draw
        self.draw_face()

    def create_category_widgets(self, frame, features):
        for i, feature in enumerate(features):
            ttk.Label(frame, text=feature.replace('_', ' ').title() + ':').grid(row=i, column=0, sticky='w', padx=5, pady=5)
            if isinstance(self.features[feature], tk.BooleanVar):
                ttk.Checkbutton(frame, variable=self.features[feature], command=self.draw_face).grid(row=i, column=1, sticky='w', padx=5, pady=5)
            elif isinstance(self.features[feature], tk.DoubleVar):
                ttk.Scale(frame, from_=0.5, to=1.5, variable=self.features[feature], orient=tk.HORIZONTAL, command=lambda _: self.draw_face()).grid(row=i, column=1, sticky='we', padx=5, pady=5)
            elif isinstance(self.features[feature], tk.IntVar):
                ttk.Scale(frame, from_=18, to=80, variable=self.features[feature], orient=tk.HORIZONTAL, command=lambda _: self.draw_face()).grid(row=i, column=1, sticky='we', padx=5, pady=5)
            else:
                ttk.Combobox(frame, textvariable=self.features[feature], values=self.get_feature_options(feature), state="readonly").grid(row=i, column=1, sticky='we', padx=5, pady=5)
                self.features[feature].trace('w', lambda *args: self.draw_face())

    def get_feature_options(self, feature):
        options = {
            'face_shape': ['oval', 'round', 'square', 'heart', 'diamond', 'triangle'],
            'skin_tone': ['very fair', 'fair', 'medium', 'olive', 'brown', 'dark'],
            'skin_texture': ['smooth', 'normal', 'rough'],
            'eye_shape': ['round', 'almond', 'hooded', 'downturned', 'upturned', 'wide-set', 'close-set'],
            'eye_color': ['brown', 'blue', 'green', 'hazel', 'gray', 'amber'],
            'eyebrow_shape': ['straight', 'curved', 'arched', 'S-shaped', 'rounded'],
            'nose_shape': ['straight', 'curved', 'bumpy', 'wide', 'narrow'],
            'mouth_shape': ['full', 'thin', 'heart-shaped', 'wide', 'bow-shaped'],
            'jaw_shape': ['rounded', 'square', 'pointed', 'wide'],
            'chin_shape': ['rounded', 'square', 'pointed', 'dimpled'],
            'hair_style': ['short', 'medium', 'long', 'bald', 'buzz cut', 'pixie', 'bob'],
            'hair_color': ['black', 'brown', 'blonde', 'red', 'gray', 'white'],
            'hair_texture': ['straight', 'wavy', 'curly', 'coily'],
            'facial_hair': ['none', 'stubble', 'mustache', 'goatee', 'full beard'],
            'glasses': ['none', 'round', 'square', 'oval', 'cat-eye'],
            'expression': ['neutral', 'happy', 'sad', 'surprised', 'angry']
        }
        return options.get(feature, [])

    def get_color(self, color_name):
        return self.color_map.get(color_name, (0, 0, 0))

    def draw_face(self):
        image = Image.new('RGB', (600, 800), color='white')
        draw = ImageDraw.Draw(image)

        self.draw_face_shape(draw)
        self.apply_skin_properties(image)

        self.draw_eyes(draw)
        self.draw_eyebrows(draw)
        self.draw_nose(draw)
        self.draw_mouth(draw)
        self.draw_hair(draw)

        self.add_freckles_and_moles(draw)
        self.add_glasses(draw)
        self.apply_expression(draw)

        self.apply_age_effects(image, draw)

        self.photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")  # Clear previous image
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)

    def draw_face_shape(self, draw):
        width, height = 600, 800
        face_color = self.get_color(self.features['skin_tone'].get())
        jaw_line_color = self.darken_color(face_color, 0.8)  # Slightly darker than face color for jawline

        face_shapes = {
            'oval': lambda: self.draw_oval_face(draw, face_color, jaw_line_color),
            'round': lambda: self.draw_round_face(draw, face_color, jaw_line_color),
            'square': lambda: self.draw_square_face(draw, face_color, jaw_line_color),
            'heart': lambda: self.draw_heart_face(draw, face_color, jaw_line_color),
            'diamond': lambda: self.draw_diamond_face(draw, face_color, jaw_line_color),
            'triangle': lambda: self.draw_triangle_face(draw, face_color, jaw_line_color),
        }

        face_shape_func = face_shapes.get(self.features['face_shape'].get(), self.draw_default_face)
        face_shape_func()

    def draw_oval_face(self, draw, face_color, jaw_color):
        draw.ellipse([(150, 100), (450, 700)], fill=face_color, outline=jaw_color, width=2)

    def draw_round_face(self, draw, face_color, jaw_color):
        draw.ellipse([(150, 150), (450, 650)], fill=face_color, outline=jaw_color, width=2)

    def draw_square_face(self, draw, face_color, jaw_color):
        draw.rectangle([(150, 150), (450, 650)], fill=face_color, outline=jaw_color, width=2)
        draw.arc([(150, 150), (250, 250)], start=180, end=270, fill=jaw_color, width=2)  # Top left corner
        draw.arc([(350, 150), (450, 250)], start=270, end=0, fill=jaw_color, width=2)    # Top right corner

    def draw_heart_face(self, draw, face_color, jaw_color):
        draw.polygon([(300, 150), (150, 350), (150, 650), (450, 650), (450, 350)], fill=face_color, outline=jaw_color, width=2)
        draw.arc([(150, 150), (450, 550)], start=0, end=180, fill=face_color, outline=jaw_color, width=2)

    def draw_diamond_face(self, draw, face_color, jaw_color):
        draw.polygon([(300, 100), (150, 400), (300, 700), (450, 400)], fill=face_color, outline=jaw_color, width=2)

    def draw_triangle_face(self, draw, face_color, jaw_color):
        draw.polygon([(300, 100), (150, 650), (450, 650)], fill=face_color, outline=jaw_color, width=2)
        draw.arc([(150, 450), (450, 850)], start=180, end=0, fill=face_color, outline=jaw_color, width=2)

    def draw_default_face(self):
        self.draw_oval_face(self.draw, self.get_color(self.features['skin_tone'].get()), self.darken_color(self.get_color(self.features['skin_tone'].get()), 0.8))

    def darken_color(self, color, factor=0.8):
        return tuple(int(c * factor) for c in color)

    def apply_skin_properties(self, image):
        skin_tone = self.get_color(self.features['skin_tone'].get())
        skin_layer = Image.new('RGB', image.size, skin_tone)
        image.paste(skin_layer, (0, 0), mask=None)

        if self.features['skin_texture'].get() == 'rough':
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(0.85)
            image = image.filter(ImageFilter.DETAIL)


    def draw_eyes(self, draw):
        eye_x1, eye_y = 230, 300
        eye_x2 = eye_x1 + 140  # Increased distance between eyes

        eye_shapes = {
            "round": lambda x, y: draw.ellipse([x, y, x+50, y+30], fill="white", outline="black"),
            "almond": lambda x, y: draw.polygon([(x, y+15), (x+25, y), (x+50, y+15), (x+25, y+30)], fill="white", outline="black"),
            "hooded": lambda x, y: draw.polygon([(x, y+20), (x+25, y), (x+50, y+20), (x+25, y+35)], fill="white", outline="black"),
            "monolid": lambda x, y: draw.rectangle([x, y+10, x+50, y+25], fill="white", outline="black"),
            "downturned": lambda x, y: draw.arc([x, y, x+50, y+30], start=20, end=160, fill="white"),
            "upturned": lambda x, y: draw.arc([x, y-30, x+50, y], start=200, end=340, fill="white"),
            "wide-set": lambda x, y: self.draw_default_eye(draw, x-20, y),
            "close-set": lambda x, y: self.draw_default_eye(draw, x+20, y),
        }

        # Use get() method with a default value to avoid KeyError
        eye_shape_func = eye_shapes.get(self.features['eye_shape'].get(), self.draw_default_eye)
        
        # Draw left eye
        eye_shape_func(eye_x1, eye_y)
        
        # Draw right eye
        eye_shape_func(eye_x2, eye_y)

        # Draw irises
        iris_color = self.get_color(self.features['eye_color'].get())
        draw.ellipse([eye_x1+15, eye_y+10, eye_x1+35, eye_y+30], fill=iris_color)
        draw.ellipse([eye_x2+15, eye_y+10, eye_x2+35, eye_y+30], fill=iris_color)

    def draw_default_eye(self, draw, x, y):
        draw.ellipse([x, y, x+50, y+30], fill="white", outline="black")

        

    def draw_eyebrows(self, draw):
        eyebrow_shapes = {
            'straight': lambda x, y: draw.line([x, y, x+80, y], fill='black', width=int(10 * self.features['eyebrow_thickness'].get())),
            'arched': lambda x, y: draw.arc([x, y-10, x+80, y+20], start=0, end=180, fill='black', width=int(10 * self.features['eyebrow_thickness'].get())),
            'curved': lambda x, y: draw.arc([x, y, x+80, y+30], start=0, end=180, fill='black', width=int(10 * self.features['eyebrow_thickness'].get())),
            'S-shaped': lambda x, y: self.draw_s_shaped_eyebrow(draw, x, y),
            'rounded': lambda x, y: draw.arc([x, y-5, x+80, y+15], start=0, end=180, fill='black', width=int(10 * self.features['eyebrow_thickness'].get()))
        }
        
        eyebrow_x1 = 200 - int(30 * self.features['eye_distance'].get())
        eyebrow_x2 = 300 + int(30 * self.features['eye_distance'].get())
        eyebrow_y = 260
        
        # Use get() method with a default value to avoid KeyError
        eyebrow_shape_func = eyebrow_shapes.get(self.features['eyebrow_shape'].get(), self.draw_default_eyebrow)
        
        # Draw left eyebrow
        eyebrow_shape_func(eyebrow_x1, eyebrow_y)
        
        # Draw right eyebrow
        eyebrow_shape_func(eyebrow_x2, eyebrow_y)

    def draw_s_shaped_eyebrow(self, draw, x, y):
        # Drawing an S-shaped eyebrow using two arcs
        thickness = int(10 * self.features['eyebrow_thickness'].get())
        draw.arc([x, y, x+40, y+20], start=0, end=180, fill='black', width=thickness)
        draw.arc([x+40, y-20, x+80, y], start=180, end=360, fill='black', width=thickness)

    def draw_default_eyebrow(self, draw, x, y):
        # Default to a straight eyebrow if shape is not implemented
        draw.line([x, y, x+80, y], fill='black', width=int(10 * self.features['eyebrow_thickness'].get()))


    def draw_nose(self, draw):
        nose_x, nose_y = 300, 380
        nose_width = int(20 * self.features['nose_size'].get())
        nose_height = int(100 * self.features['nose_size'].get())

        nose_shapes = {
            'straight': lambda: draw.line([(nose_x, nose_y), (nose_x, nose_y + nose_height)], fill='brown', width=nose_width),
            'curved': lambda: draw.arc([(nose_x - nose_width, nose_y), (nose_x + nose_width, nose_y + nose_height)], start=0, end=180, fill='brown', width=nose_width),
            'bumpy': lambda: self.draw_bumpy_nose(draw, nose_x, nose_y, nose_width, nose_height),
            'wide': lambda: draw.polygon([(nose_x - nose_width, nose_y + nose_height), (nose_x, nose_y), (nose_x + nose_width, nose_y + nose_height)], fill='brown'),
            'narrow': lambda: draw.polygon([(nose_x - nose_width//2, nose_y + nose_height), (nose_x, nose_y), (nose_x + nose_width//2, nose_y + nose_height)], fill='brown'),
        }
        
        nose_shape_func = nose_shapes.get(self.features['nose_shape'].get(), self.draw_default_nose)
        nose_shape_func()

    def draw_bumpy_nose(self, draw, x, y, width, height):
        draw.line([(x, y), (x - width//2, y + height//2), (x, y + height)], fill='brown', width=width//2)
        draw.line([(x, y), (x + width//2, y + height//2), (x, y + height)], fill='brown', width=width//2)

    def draw_default_nose(self):
        nose_x, nose_y = 300, 380
        nose_width = int(20 * self.features['nose_size'].get())
        nose_height = int(100 * self.features['nose_size'].get())
        self.draw.line([(nose_x, nose_y), (nose_x, nose_y + nose_height)], fill='brown', width=nose_width)


    def draw_hair(self, draw):
        hair_color = self.get_color(self.features['hair_color'].get())
        hair_styles = {
            'short': lambda: draw.rectangle([(150, 100), (450, 200)], fill=hair_color),
            'medium': lambda: draw.rectangle([(150, 100), (450, 300)], fill=hair_color),
            'long': lambda: draw.rectangle([(150, 100), (450, 450)], fill=hair_color),
            'bald': lambda: None,
            'buzz cut': lambda: draw.rectangle([(150, 100), (450, 150)], fill=hair_color),
            'pixie': lambda: self.draw_pixie_hair(draw, hair_color),
            'bob': lambda: self.draw_bob_hair(draw, hair_color)
        }
        
        hair_style_func = hair_styles.get(self.features['hair_style'].get(), self.draw_default_hair)
        hair_style_func()

    def draw_pixie_hair(self, draw, color):
        draw.rectangle([(150, 100), (450, 200)], fill=color)
        draw.ellipse([(200, 150), (400, 250)], fill=color)

    def draw_bob_hair(self, draw, color):
        draw.rectangle([(150, 100), (450, 300)], fill=color)
        draw.arc([(150, 100), (450, 500)], start=0, end=180, fill=color, width=50)

    def draw_default_hair(self):
        hair_color = self.get_color(self.features['hair_color'].get())
        self.draw.rectangle([(150, 100), (450, 200)], fill=hair_color)

    def draw_mouth(self, draw):
        mouth_x, mouth_y = 300, 550
        mouth_width = int(100 * self.features['mouth_size'].get())
        mouth_height = int(30 * self.features['lip_thickness'].get())

        mouth_shapes = {
            'full': lambda: draw.ellipse([(mouth_x - mouth_width//2, mouth_y), (mouth_x + mouth_width//2, mouth_y + mouth_height)], fill='red'),
            'thin': lambda: draw.line([(mouth_x - mouth_width//2, mouth_y + mouth_height//2), (mouth_x + mouth_width//2, mouth_y + mouth_height//2)], fill='red', width=mouth_height),
            'heart-shaped': lambda: self.draw_heart_shaped_mouth(draw, mouth_x, mouth_y, mouth_width, mouth_height),
            'wide': lambda: draw.arc([(mouth_x - mouth_width//2, mouth_y - mouth_height), (mouth_x + mouth_width//2, mouth_y + mouth_height*2)], start=0, end=180, fill='red', width=mouth_height),
            'bow-shaped': lambda: self.draw_bow_shaped_mouth(draw, mouth_x, mouth_y, mouth_width, mouth_height),
        }
        
        mouth_shape_func = mouth_shapes.get(self.features['mouth_shape'].get(), self.draw_default_mouth)
        mouth_shape_func()

    def draw_heart_shaped_mouth(self, draw, x, y, width, height):
        draw.pieslice([(x - width//2, y), (x, y + height)], start=0, end=180, fill='red')
        draw.pieslice([(x, y), (x + width//2, y + height)], start=0, end=180, fill='red')

    def draw_bow_shaped_mouth(self, draw, x, y, width, height):
        draw.arc([(x - width//2, y - height), (x, y + height)], start=180, end=0, fill='red', width=height//2)
        draw.arc([(x, y - height), (x + width//2, y + height)], start=180, end=0, fill='red', width=height//2)

    def draw_default_mouth(self):
        mouth_x, mouth_y = 300, 550
        mouth_width = int(100 * self.features['mouth_size'].get())
        mouth_height = int(30 * self.features['lip_thickness'].get())
        self.draw.line([(mouth_x - mouth_width//2, mouth_y + mouth_height//2), (mouth_x + mouth_width//2, mouth_y + mouth_height//2)], fill='red', width=mouth_height)
        
    def add_freckles_and_moles(self, draw):
        if self.features['freckles'].get():
            for _ in range(random.randint(5, 15)):
                x, y = random.randint(200, 400), random.randint(250, 600)
                draw.ellipse([x, y, x+5, y+5], fill='brown')
        if self.features['moles'].get():
            x, y = random.randint(250, 350), random.randint(300, 700)
            draw.ellipse([x, y, x+10, y+10], fill='darkbrown')

    def add_glasses(self, draw):
        glasses_styles = {
            'round': lambda: draw.ellipse([(200, 290), (260, 350)], outline='black', width=5),
            'square': lambda: draw.rectangle([(200, 290), (260, 350)], outline='black', width=5),
            'oval': lambda: draw.ellipse([(200, 290), (270, 340)], outline='black', width=5)
        }
        if self.features['glasses'].get() != 'none':
            glasses_styles[self.features['glasses'].get()]()
            glasses_styles[self.features['glasses'].get()]()

    def apply_expression(self, draw):
        expressions = {
            'neutral': lambda: None,
            'happy': lambda: draw.arc([(250, 550), (350, 590)], start=0, end=180, fill='red', width=5),
            'sad': lambda: draw.arc([(250, 550), (350, 590)], start=180, end=360, fill='red', width=5),
            'surprised': lambda: draw.ellipse([(280, 540), (320, 580)], outline='red', width=5),
            'angry': lambda: draw.line([(250, 550), (350, 590)], fill='red', width=5)
        }
        expressions[self.features['expression'].get()]()

    def apply_age_effects(self, image, draw):
        age = self.features['age'].get()
        if age > 50:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(0.9)
            image = image.filter(ImageFilter.SHARPEN)

            wrinkles_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
            wrinkles_draw = ImageDraw.Draw(wrinkles_layer)

            # Draw wrinkle lines on the forehead
            wrinkles_draw.arc([(200, 230), (400, 270)], start=0, end=180, fill='gray', width=2)
            wrinkles_draw.arc([(210, 250), (390, 290)], start=0, end=180, fill='gray', width=2)

            # Crow's feet near the eyes
            wrinkles_draw.arc([(160, 300), (230, 340)], start=240, end=300, fill='gray', width=2)
            wrinkles_draw.arc([(370, 300), (440, 340)], start=240, end=300, fill='gray', width=2)

            # Nasolabial folds
            wrinkles_draw.arc([(240, 470), (310, 510)], start=270, end=360, fill='gray', width=2)
            wrinkles_draw.arc([(290, 470), (360, 510)], start=180, end=270, fill='gray', width=2)

            image.paste(wrinkles_layer, (0, 0), mask=wrinkles_layer)

        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)

    def draw_face(self):
        image = Image.new('RGB', (600, 800), color='white')
        draw = ImageDraw.Draw(image)

        self.draw_face_shape(draw)
        self.apply_skin_properties(image)

        self.draw_eyes(draw)
        self.draw_eyebrows(draw)
        self.draw_nose(draw)
        self.draw_mouth(draw)
        self.draw_hair(draw)

        self.add_freckles_and_moles(draw)
        self.add_glasses(draw)
        self.apply_expression(draw)

        self.apply_age_effects(image, draw)

        self.photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")  # Clear previous image
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)

if __name__ == "__main__":
    root = tk.Tk()
    face_creator = AdvancedFaceCreator(root)
    root.mainloop()

