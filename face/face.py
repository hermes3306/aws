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
        # Create a notebook for categorized features
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

        # Draw button
        ttk.Button(self.master, text="Generate Face", command=self.draw_face).pack(pady=10)

        # Canvas for drawing
        self.canvas = tk.Canvas(self.master, width=600, height=800, bg='white')
        self.canvas.pack(padx=10, pady=10)

    def create_category_widgets(self, frame, features):
        for i, feature in enumerate(features):
            ttk.Label(frame, text=feature.replace('_', ' ').title() + ':').grid(row=i, column=0, sticky='w', padx=5, pady=5)
            if isinstance(self.features[feature], tk.BooleanVar):
                ttk.Checkbutton(frame, variable=self.features[feature]).grid(row=i, column=1, sticky='w', padx=5, pady=5)
            elif isinstance(self.features[feature], tk.DoubleVar):
                ttk.Scale(frame, from_=0.5, to=1.5, variable=self.features[feature], orient=tk.HORIZONTAL).grid(row=i, column=1, sticky='we', padx=5, pady=5)
            elif isinstance(self.features[feature], tk.IntVar):
                ttk.Scale(frame, from_=18, to=80, variable=self.features[feature], orient=tk.HORIZONTAL).grid(row=i, column=1, sticky='we', padx=5, pady=5)
            else:
                ttk.Combobox(frame, textvariable=self.features[feature], values=self.get_feature_options(feature)).grid(row=i, column=1, sticky='we', padx=5, pady=5)

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
        return self.color_map.get(color_name, (0, 0, 0))  # Default to black if color not found

    # Each of these functions would need to be implemented with much more 
    # sophisticated drawing techniques, possibly using pre-made assets or 
    # even machine learning models for generating realistic facial features.

    def draw_face(self):
        # Create a new image
        image = Image.new('RGB', (600, 800), color='white')
        draw = ImageDraw.Draw(image)

        # Draw face shape
        self.draw_face_shape(draw)

        # Apply skin tone and texture
        self.apply_skin_properties(image)

        # Draw facial features
        self.draw_eyes(draw)
        self.draw_eyebrows(draw)
        self.draw_nose(draw)
        self.draw_mouth(draw)

        # Draw hair
        self.draw_hair(draw)

        # Add additional features
        self.add_freckles_and_moles(draw)
        self.add_glasses(draw)
        self.apply_expression(draw)

        # Apply age effects
        self.apply_age_effects(image, draw)

        # Display the image
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        

    def draw_face_shape(self, draw):
        width, height = 600, 800
        face_shapes = {
            'oval': lambda: draw.ellipse([(100, 100), (500, 700)], fill=self.get_color(self.features['skin_tone'].get())),
            'round': lambda: draw.ellipse([(150, 150), (450, 650)], fill=self.get_color(self.features['skin_tone'].get())),
            'square': lambda: draw.rectangle([(100, 100), (500, 700)], fill=self.get_color(self.features['skin_tone'].get())),
            'heart': lambda: draw.polygon([(300, 100), (100, 300), (100, 700), (500, 700), (500, 300)], fill=self.get_color(self.features['skin_tone'].get())),
            'diamond': lambda: draw.polygon([(300, 100), (100, 400), (300, 700), (500, 400)], fill=self.get_color(self.features['skin_tone'].get())),
            'triangle': lambda: draw.polygon([(300, 100), (100, 700), (500, 700)], fill=self.get_color(self.features['skin_tone'].get())),
        }
        face_shapes[self.features['face_shape'].get()]()

    def apply_skin_properties(self, image):
        # Apply skin tone
        skin_tone = self.get_color(self.features['skin_tone'].get())
        skin_layer = Image.new('RGB', image.size, skin_tone)
        image.paste(skin_layer, (0, 0), mask=image.split()[0])

        # Apply skin texture
        textures = {
            'smooth': 0,
            'normal': 1,
            'rough': 2
        }
        texture = textures[self.features['skin_texture'].get()]
        if texture > 0:
            image = image.filter(ImageFilter.GaussianBlur(radius=texture))

    def draw_eyes(self, draw):
        eye_width = 60 * self.features['eye_distance'].get()
        eye_height = 30
        left_eye_center = (250 - eye_width/2, 300)
        right_eye_center = (350 + eye_width/2, 300)

        eye_shapes = {
            'round': lambda x, y: draw.ellipse([(x-30, y-15), (x+30, y+15)], fill=self.get_color('white'), outline=self.get_color('black')),
            'almond': lambda x, y: draw.polygon([(x-30, y), (x, y-15), (x+30, y), (x, y+15)], fill=self.get_color('white'), outline=self.get_color('black')),
            'hooded': lambda x, y: draw.polygon([(x-30, y), (x, y-10), (x+30, y), (x, y+15)], fill=self.get_color('white'), outline=self.get_color('black')),
            'downturned': lambda x, y: draw.polygon([(x-30, y-5), (x, y-15), (x+30, y-5), (x, y+15)], fill=self.get_color('white'), outline=self.get_color('black')),
            'upturned': lambda x, y: draw.polygon([(x-30, y+5), (x, y-15), (x+30, y+5), (x, y+15)], fill=self.get_color('white'), outline=self.get_color('black')),
        }

        eye_shape = self.features['eye_shape'].get()
        eye_shapes[eye_shape](*left_eye_center)
        eye_shapes[eye_shape](*right_eye_center)

        # Draw iris and pupil
        iris_color = self.get_color(self.features['eye_color'].get())
        for center in [left_eye_center, right_eye_center]:
            draw.ellipse([(center[0]-15, center[1]-15), (center[0]+15, center[1]+15)], fill=iris_color)
            draw.ellipse([(center[0]-5, center[1]-5), (center[0]+5, center[1]+5)], fill=self.get_color('black'))

    def draw_eyes(self, draw):
        eye_width = 60 * self.features['eye_distance'].get()
        eye_height = 30
        left_eye_center = (250 - eye_width/2, 300)
        right_eye_center = (350 + eye_width/2, 300)

        eye_shapes = {
            'round': lambda x, y: draw.ellipse([(x-30, y-15), (x+30, y+15)], fill='white', outline='black'),
            'almond': lambda x, y: draw.polygon([(x-30, y), (x, y-15), (x+30, y), (x, y+15)], fill='white', outline='black'),
            'hooded': lambda x, y: draw.polygon([(x-30, y), (x, y-10), (x+30, y), (x, y+15)], fill='white', outline='black'),
            'downturned': lambda x, y: draw.polygon([(x-30, y-5), (x, y-15), (x+30, y-5), (x, y+15)], fill='white', outline='black'),
            'upturned': lambda x, y: draw.polygon([(x-30, y+5), (x, y-15), (x+30, y+5), (x, y+15)], fill='white', outline='black'),
        }

        eye_shape = self.features['eye_shape'].get()
        eye_shapes[eye_shape](*left_eye_center)
        eye_shapes[eye_shape](*right_eye_center)

        # Draw iris and pupil
        iris_color = self.features['eye_color'].get()
        for center in [left_eye_center, right_eye_center]:
            draw.ellipse([(center[0]-15, center[1]-15), (center[0]+15, center[1]+15)], fill=iris_color)
            draw.ellipse([(center[0]-5, center[1]-5), (center[0]+5, center[1]+5)], fill='black')

    def draw_eyebrows(self, draw):
        eyebrow_shapes = {
            'straight': lambda x, y: draw.line([(x-30, y), (x+30, y)], fill='black', width=5),
            'curved': lambda x, y: draw.arc([(x-30, y-10), (x+30, y+10)], start=0, end=180, fill='black', width=5),
            'arched': lambda x, y: draw.arc([(x-30, y-20), (x+30, y+20)], start=0, end=180, fill='black', width=5),
            'S-shaped': lambda x, y: draw.line([(x-30, y), (x-15, y-5), (x+15, y+5), (x+30, y)], fill='black', width=5),
        }

        thickness = 5 * self.features['eyebrow_thickness'].get()
        left_eyebrow_center = (250, 250)
        right_eyebrow_center = (350, 250)

        eyebrow_shape = self.features['eyebrow_shape'].get()
        eyebrow_shapes[eyebrow_shape](*left_eyebrow_center)
        eyebrow_shapes[eyebrow_shape](*right_eyebrow_center)

    def draw_nose(self, draw):
        nose_center = (300, 400)
        nose_size = 30 * self.features['nose_size'].get()

        nose_shapes = {
            'straight': lambda x, y, s: draw.line([(x, y-s), (x, y+s)], fill='black', width=2),
            'curved': lambda x, y, s: draw.arc([(x-s, y-s), (x+s, y+s)], start=0, end=180, fill='black', width=2),
            'bumpy': lambda x, y, s: draw.line([(x, y-s), (x+s/2, y), (x, y+s)], fill='black', width=2),
            'wide': lambda x, y, s: draw.polygon([(x-s, y+s), (x, y-s), (x+s, y+s)], outline='black'),
            'narrow': lambda x, y, s: draw.polygon([(x-s/2, y+s), (x, y-s), (x+s/2, y+s)], outline='black'),
        }

        nose_shape = self.features['nose_shape'].get()
        nose_shapes[nose_shape](*nose_center, nose_size)


    def draw_mouth(self, draw):
        mouth_center = (300, 500)
        mouth_width = 80 * self.features['mouth_size'].get()
        mouth_height = 30 * self.features['lip_thickness'].get()

        mouth_shapes = {
            'full': lambda x, y, w, h: draw.chord([(x-w/2, y-h/2), (x+w/2, y+h/2)], start=0, end=180, fill=self.get_color('red')),
            'thin': lambda x, y, w, h: draw.arc([(x-w/2, y-h/4), (x+w/2, y+h/4)], start=0, end=180, fill=self.get_color('red'), width=2),
            'heart-shaped': lambda x, y, w, h: draw.polygon([(x-w/2, y), (x, y-h/2), (x+w/2, y), (x, y+h/2)], fill=self.get_color('red')),
            'wide': lambda x, y, w, h: draw.chord([(x-w/2, y-h/4), (x+w/2, y+h/4)], start=0, end=180, fill=self.get_color('red')),
            'bow-shaped': lambda x, y, w, h: draw.arc([(x-w/2, y-h), (x+w/2, y+h)], start=0, end=180, fill=self.get_color('red'), width=3),
        }

        mouth_shape = self.features['mouth_shape'].get()
        mouth_shapes[mouth_shape](*mouth_center, mouth_width, mouth_height)

    def draw_hair(self, draw):
        hair_color = self.get_color(self.features['hair_color'].get())
        hair_style = self.features['hair_style'].get()
        hair_texture = self.features['hair_texture'].get()

        if hair_style == 'bald':
            return

        if hair_style in ['short', 'buzz cut']:
            draw.ellipse([(100, 50), (500, 300)], fill=hair_color)
        elif hair_style in ['medium', 'long']:
            draw.ellipse([(50, 50), (550, 400)], fill=hair_color)
            if hair_style == 'long':
                draw.rectangle([(100, 400), (500, 700)], fill=hair_color)
        elif hair_style == 'pixie':
            draw.ellipse([(100, 50), (500, 250)], fill=hair_color)
            draw.polygon([(150, 250), (300, 350), (450, 250)], fill=hair_color)
        elif hair_style == 'bob':
            draw.ellipse([(75, 50), (525, 350)], fill=hair_color)
            draw.rectangle([(75, 350), (525, 450)], fill=hair_color)

        if hair_texture == 'wavy':
            for i in range(100, 501, 40):
                draw.arc([(i, 100), (i+80, 500)], start=0, end=180, fill=hair_color, width=5)
        elif hair_texture == 'curly':
            for _ in range(100):
                x = random.randint(100, 500)
                y = random.randint(100, 500)
                draw.ellipse([(x, y), (x+20, y+20)], fill=hair_color)

    def add_freckles_and_moles(self, draw):
        if self.features['freckles'].get():
            for _ in range(50):
                x = random.randint(150, 450)
                y = random.randint(250, 500)
                draw.point((x, y), fill=self.get_color('brown'))

        if self.features['moles'].get():
            for _ in range(3):
                x = random.randint(150, 450)
                y = random.randint(250, 600)
                draw.ellipse([(x, y), (x+5, y+5)], fill=self.get_color('brown'))


    def add_glasses(self, draw):
        if self.features['glasses'].get() != 'none':
            glasses_style = self.features['glasses'].get()
            left_eye_center = (250, 300)
            right_eye_center = (350, 300)

            if glasses_style == 'round':
                draw.ellipse([(left_eye_center[0]-40, left_eye_center[1]-30), (left_eye_center[0]+40, left_eye_center[1]+30)], outline='black', width=3)
                draw.ellipse([(right_eye_center[0]-40, right_eye_center[1]-30), (right_eye_center[0]+40, right_eye_center[1]+30)], outline='black', width=3)
            elif glasses_style == 'square':
                draw.rectangle([(left_eye_center[0]-40, left_eye_center[1]-30), (left_eye_center[0]+40, left_eye_center[1]+30)], outline='black', width=3)
                draw.rectangle([(right_eye_center[0]-40, right_eye_center[1]-30), (right_eye_center[0]+40, right_eye_center[1]+30)], outline='black', width=3)
            elif glasses_style == 'oval':
                draw.ellipse([(left_eye_center[0]-45, left_eye_center[1]-25), (left_eye_center[0]+45, left_eye_center[1]+25)], outline='black', width=3)
                draw.ellipse([(right_eye_center[0]-45, right_eye_center[1]-25), (right_eye_center[0]+45, right_eye_center[1]+25)], outline='black', width=3)
            elif glasses_style == 'cat-eye':
                draw.polygon([(left_eye_center[0]-45, left_eye_center[1]), (left_eye_center[0], left_eye_center[1]-30), (left_eye_center[0]+45, left_eye_center[1]), (left_eye_center[0], left_eye_center[1]+20)], outline='black', width=3)
                draw.polygon([(right_eye_center[0]-45, right_eye_center[1]), (right_eye_center[0], right_eye_center[1]-30), (right_eye_center[0]+45, right_eye_center[1]), (right_eye_center[0], right_eye_center[1]+20)], outline='black', width=3)

            # Draw bridge
            draw.line([(left_eye_center[0]+40, left_eye_center[1]), (right_eye_center[0]-40, right_eye_center[1])], fill='black', width=3)

    def apply_expression(self, draw):
        expression = self.features['expression'].get()
        mouth_center = (300, 500)
        eye_centers = [(250, 300), (350, 300)]

        if expression == 'happy':
            # Curved up mouth
            draw.arc([(mouth_center[0]-50, mouth_center[1]-30), (mouth_center[0]+50, mouth_center[1]+30)], start=0, end=180, fill='red', width=3)
            # Curved up eyebrows
            for eye in eye_centers:
                draw.arc([(eye[0]-30, eye[1]-50), (eye[0]+30, eye[1]-30)], start=0, end=180, fill='black', width=3)
        elif expression == 'sad':
            # Curved down mouth
            draw.arc([(mouth_center[0]-50, mouth_center[1]+30), (mouth_center[0]+50, mouth_center[1]-30)], start=180, end=0, fill='red', width=3)
            # Curved down eyebrows
            for eye in eye_centers:
                draw.arc([(eye[0]-30, eye[1]-30), (eye[0]+30, eye[1]-50)], start=180, end=0, fill='black', width=3)
        elif expression == 'surprised':
            # O-shaped mouth
            draw.ellipse([(mouth_center[0]-20, mouth_center[1]-20), (mouth_center[0]+20, mouth_center[1]+20)], outline='red', width=3)
            # Raised eyebrows
            for eye in eye_centers:
                draw.arc([(eye[0]-30, eye[1]-60), (eye[0]+30, eye[1]-40)], start=0, end=180, fill='black', width=3)
        elif expression == 'angry':
            # Straight line mouth
            draw.line([(mouth_center[0]-30, mouth_center[1]), (mouth_center[0]+30, mouth_center[1])], fill='red', width=3)
            # Angled eyebrows
            draw.line([(eye_centers[0][0]-30, eye_centers[0][1]-30), (eye_centers[0][0]+30, eye_centers[0][1]-40)], fill='black', width=3)
            draw.line([(eye_centers[1][0]-30, eye_centers[1][1]-40), (eye_centers[1][0]+30, eye_centers[1][1]-30)], fill='black', width=3)

    def apply_age_effects(self, image, draw):
        age = self.features['age'].get()
        if age > 40:
            # Add wrinkles
            for _ in range(int((age - 40) / 5)):
                x1 = random.randint(150, 450)
                y1 = random.randint(250, 500)
                x2 = x1 + random.randint(-30, 30)
                y2 = y1 + random.randint(-30, 30)
                draw.line([(x1, y1), (x2, y2)], fill='gray', width=1)

        if age > 50:
            # Add age spots
            for _ in range(int((age - 50) / 5)):
                x = random.randint(150, 450)
                y = random.randint(250, 600)
                draw.ellipse([(x, y), (x+5, y+5)], fill='brown')

        # Adjust overall face appearance based on age
        if age > 60:
            # Add some sag to the face
            image = image.transform(image.size, Image.AFFINE, (1, 0, 0, 0, 1.05, -30))
root = tk.Tk()
face_creator = AdvancedFaceCreator(root)
root.mainloop()