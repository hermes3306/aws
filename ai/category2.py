import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

# Restructured data with 5 main categories
ai_landscape = {
    "Machine Learning & Deep Learning": {
        "Scikit-learn": 5, "TensorFlow": 5, "PyTorch": 5, "Keras": 4, "XGBoost": 4,
        "MXNet": 3, "Caffe": 3, "Theano": 3, "Chainer": 3, "FastAI": 4
    },
    "Natural Language Processing": {
        "NLTK": 5, "spaCy": 4, "Gensim": 4, "Stanford NLP": 4, "Transformers": 5,
        "OpenAI GPT": 5, "BERT": 5, "RoBERTa": 4, "XLNet": 4, "T5": 4
    },
    "Computer Vision": {
        "OpenCV": 5, "TensorFlow Object Detection": 4, "YOLO": 4, "Detectron2": 4, "Mediapipe": 3,
        "PyTorch Vision": 4, "Keras Applications": 4, "ImageAI": 3, "Dlib": 4, "SimpleCV": 3
    },
    "AI Infrastructure & Platforms": {
        "AWS SageMaker": 5, "Google Cloud AI": 5, "Azure ML": 5, "IBM Watson": 4, "Oracle AI": 3,
        "NVIDIA GPUs": 5, "Google TPUs": 4, "Intel AI": 4, "AMD ROCm": 3, "Graphcore IPUs": 3
    },
    "AI Applications & Specialized Tools": {
        "TensorFlow Serving": 4, "MLflow": 4, "Kubeflow": 3, "H2O.ai": 4, "RapidMiner": 4,
        "Pandas": 5, "NumPy": 5, "SciPy": 5, "Matplotlib": 5, "Seaborn": 4
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
category_menu = ttk.Combobox(menu_frame, textvariable=category_var, values=list(ai_landscape.keys()))
category_menu.pack(side=tk.LEFT, padx=5)
category_menu.set("Select Category")

def plot_landscape(*args):
    category = category_var.get()
    
    if category in ai_landscape:
        ax.clear()
        tools = ai_landscape[category]
        
        # Create a matrix-like structure
        maturity_levels = range(1, 6)
        matrix = defaultdict(list)
        
        for tool, maturity in tools.items():
            matrix[maturity].append(tool)
        
        # Plot tools
        for maturity in maturity_levels:
            y_positions = range(len(matrix[maturity]))
            ax.scatter([maturity] * len(matrix[maturity]), y_positions, s=100)
            
            for y, tool in zip(y_positions, matrix[maturity]):
                ax.annotate(tool, (maturity, y), xytext=(5, 0), 
                            textcoords='offset points', va='center')
        
        ax.set_xlim(0.5, 5.5)
        ax.set_ylim(-1, max(len(row) for row in matrix.values()))
        ax.set_xlabel('Maturity Level')
        ax.set_ylabel('Tools')
        ax.set_title(f'AI Landscape: {category}')
        ax.set_xticks(range(1, 6))
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        plt.tight_layout()
        canvas.draw()

category_var.trace('w', plot_landscape)

# Info display
info_frame = ttk.Frame(root)
info_frame.pack(fill=tk.X, padx=10, pady=10)
info_label = ttk.Label(info_frame, text="Select a category to view the landscape", wraplength=1380)
info_label.pack()

# Run the application
root.mainloop()