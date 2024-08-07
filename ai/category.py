import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

# Restructured data
ai_landscape = {
    "AI Foundations": {
        "Machine Learning": {
            "Scikit-learn": 5, "TensorFlow": 5, "PyTorch": 5, "Keras": 4, "XGBoost": 4
        },
        "Deep Learning": {
            "TensorFlow": 5, "PyTorch": 5, "Keras": 4, "MXNet": 3, "Caffe": 3
        },
        "Neural Networks": {
            "TensorFlow": 5, "PyTorch": 5, "Keras": 4, "Theano": 3, "Chainer": 3
        }
    },
    "AI Applications": {
        "Natural Language Processing": {
            "NLTK": 5, "spaCy": 4, "Gensim": 4, "Stanford NLP": 4, "Transformers": 5
        },
        "Computer Vision": {
            "OpenCV": 5, "TensorFlow Object Detection": 4, "YOLO": 4, "Detectron2": 4, "Mediapipe": 3
        },
        "Speech Recognition": {
            "DeepSpeech": 4, "Kaldi": 4, "CMU Sphinx": 3, "Wav2Letter++": 3, "ESPnet": 3
        }
    },
    "AI Infrastructure": {
        "Cloud Platforms": {
            "AWS SageMaker": 5, "Google Cloud AI": 5, "Azure ML": 5, "IBM Watson": 4, "Oracle AI": 3
        },
        "Hardware Acceleration": {
            "NVIDIA GPUs": 5, "Google TPUs": 4, "Intel AI": 4, "AMD ROCm": 3, "Graphcore IPUs": 3
        },
        "Model Serving": {
            "TensorFlow Serving": 4, "TorchServe": 3, "Seldon Core": 3, "MLflow": 4, "BentoML": 3
        }
    }
}

# Create main window
root = tk.Tk()
root.title("AI Landscape")
root.geometry("1400x900")

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 8))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Create menu
menu_frame = ttk.Frame(root)
menu_frame.pack(fill=tk.X, padx=10, pady=10)

category_var = tk.StringVar()
subcategory_var = tk.StringVar()

category_menu = ttk.Combobox(menu_frame, textvariable=category_var, values=list(ai_landscape.keys()))
category_menu.pack(side=tk.LEFT, padx=5)
category_menu.set("Select Category")

subcategory_menu = ttk.Combobox(menu_frame, textvariable=subcategory_var)
subcategory_menu.pack(side=tk.LEFT, padx=5)
subcategory_menu.set("Select Subcategory")

def update_subcategories(*args):
    category = category_var.get()
    if category in ai_landscape:
        subcategories = list(ai_landscape[category].keys())
        subcategory_menu['values'] = subcategories
        subcategory_menu.set("Select Subcategory")
    else:
        subcategory_menu['values'] = []
        subcategory_menu.set("Select Subcategory")

category_var.trace('w', update_subcategories)

def plot_landscape(*args):
    category = category_var.get()
    subcategory = subcategory_var.get()
    
    if category in ai_landscape and subcategory in ai_landscape[category]:
        ax.clear()
        tools = ai_landscape[category][subcategory]
        
        # Sort tools by maturity
        sorted_tools = sorted(tools.items(), key=lambda x: x[1], reverse=True)
        
        tools, maturities = zip(*sorted_tools)
        y_pos = range(len(tools))
        
        ax.barh(y_pos, maturities, align='center')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(tools)
        ax.invert_yaxis()
        ax.set_xlabel('Maturity Level')
        ax.set_title(f'{category} - {subcategory}')
        
        plt.tight_layout()
        canvas.draw()

subcategory_var.trace('w', plot_landscape)

# Info display
info_frame = ttk.Frame(root)
info_frame.pack(fill=tk.X, padx=10, pady=10)
info_label = ttk.Label(info_frame, text="Select a category and subcategory to view the landscape", wraplength=1380)
info_label.pack()

# Run the application
root.mainloop()