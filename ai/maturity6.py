import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

categories = [
    'Generative AI', 'Data-based Prediction', 'Game AI', 'Deep Learning Frameworks',
    'AI Hardware', 'AI Cloud', 'Data Prep', 'Fine-tuning', 'RAG', 'Computer Vision',
    'NLP', 'RL', 'AI Ethics', 'Model Serving', 'Vector DB', 'AI Development'
]

tools = {
    'Claude': {'category': 'Generative AI', 'maturity': 4.50},
    'LLaMA': {'category': 'Generative AI', 'maturity': 3.75},
    'Gemini': {'category': 'Generative AI', 'maturity': 4.75},
    'ChatGPT': {'category': 'Generative AI', 'maturity': 4.75},

    'MindsDB': {'category': 'Data-based Prediction', 'maturity': 4.00},
    'RapidMiner': {'category': 'Data-based Prediction', 'maturity': 4.75},
    'H2O.ai': {'category': 'Data-based Prediction', 'maturity': 4.50},
    'DataRobot': {'category': 'Data-based Prediction', 'maturity': 4.75},

    'Unity ML-Agents': {'category': 'Game AI', 'maturity': 3.75},
    'Godot AI': {'category': 'Game AI', 'maturity': 2.75},
    'OpenAI Gym': {'category': 'Game AI', 'maturity': 4.25},
    'DeepMind Lab': {'category': 'Game AI', 'maturity': 4.50},

    'TensorFlow': {'category': 'Deep Learning Frameworks', 'maturity': 5.00},
    'PyTorch': {'category': 'Deep Learning Frameworks', 'maturity': 5.00},
    'Caffe': {'category': 'Deep Learning Frameworks', 'maturity': 3.50},
    'Theano': {'category': 'Deep Learning Frameworks', 'maturity': 3.00},
    'Paddle': {'category': 'Deep Learning Frameworks', 'maturity': 3.75},

    'NVIDIA GPUs': {'category': 'AI Hardware', 'maturity': 5.00},
    'Google TPUs': {'category': 'AI Hardware', 'maturity': 4.75},
    'Intel Nervana': {'category': 'AI Hardware', 'maturity': 3.50},
    'Apple Neural Engine': {'category': 'AI Hardware', 'maturity': 4.25},
    'Graphcore IPU': {'category': 'AI Hardware', 'maturity': 3.75},

    'AWS SageMaker': {'category': 'AI Cloud', 'maturity': 5.00},
    'Google Cloud AI': {'category': 'AI Cloud', 'maturity': 5.00},
    'Azure Machine Learning': {'category': 'AI Cloud', 'maturity': 4.75},
    'IBM Watson Studio': {'category': 'AI Cloud', 'maturity': 4.50},
    'Alibaba Cloud PAI': {'category': 'AI Cloud', 'maturity': 4.25},
    'Oracle AI Cloud': {'category': 'AI Cloud', 'maturity': 3.75},
    'Baidu AI Cloud': {'category': 'AI Cloud', 'maturity': 3.75},

    'Pandas': {'category': 'Data Prep', 'maturity': 5.00},
    'Numpy': {'category': 'Data Prep', 'maturity': 5.00},
    'CuDF': {'category': 'Data Prep', 'maturity': 3.75},

    'Hugging Face': {'category': 'Fine-tuning', 'maturity': 4.75},
    'OpenAI Fine-tuning': {'category': 'Fine-tuning', 'maturity': 4.50},
    'Google Cloud AutoML': {'category': 'Fine-tuning', 'maturity': 4.25},
    'Fast.ai': {'category': 'Fine-tuning', 'maturity': 3.75},

    'LangChain': {'category': 'RAG', 'maturity': 3.75},
    'Deepset FARM': {'category': 'RAG', 'maturity': 3.50},
    'Rasa': {'category': 'RAG', 'maturity': 4.25},
    'Botpress': {'category': 'RAG', 'maturity': 3.75},

    'OpenCV': {'category': 'Computer Vision', 'maturity': 5.00},
    'TensorFlow Object Detection': {'category': 'Computer Vision', 'maturity': 4.75},
    'Mediapipe': {'category': 'Computer Vision', 'maturity': 3.75},
    'Kornia': {'category': 'Computer Vision', 'maturity': 3.50},

    'spaCy': {'category': 'NLP', 'maturity': 4.50},
    'Gensim': {'category': 'NLP', 'maturity': 4.25},
    'Transformers': {'category': 'NLP', 'maturity': 4.75},
    'Flair': {'category': 'NLP', 'maturity': 3.75},

    'OpenAI Gym': {'category': 'RL', 'maturity': 4.50},
    'RLlib': {'category': 'RL', 'maturity': 3.75},
    'Coach': {'category': 'RL', 'maturity': 3.50},
    'KerasRL': {'category': 'RL', 'maturity': 2.75},

    'Aequitas': {'category': 'AI Ethics', 'maturity': 3.50},
    'AI Fairness 360': {'category': 'AI Ethics', 'maturity': 3.75},
    'SHAP': {'category': 'AI Ethics', 'maturity': 3.75},

    'TensorFlow Serving': {'category': 'Model Serving', 'maturity': 4.50},
    'TorchServe': {'category': 'Model Serving', 'maturity': 3.75},
    'MLflow': {'category': 'Model Serving', 'maturity': 4.25},
    'Cortex': {'category': 'Model Serving', 'maturity': 3.50},

    'Pinecone': {'category': 'Vector DB', 'maturity': 4.25},
    'Milvus': {'category': 'Vector DB', 'maturity': 4.25},
    'Weaviate': {'category': 'Vector DB', 'maturity': 3.75},
    'Qdrant': {'category': 'Vector DB', 'maturity': 3.75},
    'Faiss': {'category': 'Vector DB', 'maturity': 4.25},
    'Vespa': {'category': 'Vector DB', 'maturity': 4.00},
    'Chroma': {'category': 'Vector DB', 'maturity': 2.75},

    'LangChain': {'category': 'AI Development', 'maturity': 3.75},
    'AutoML': {'category': 'AI Development', 'maturity': 4.25},
    'RAPIDS': {'category': 'AI Development', 'maturity': 3.75},
    'Gradio': {'category': 'AI Development', 'maturity': 3.75},
}


# Create main window
root = tk.Tk()
root.title("AI Landscape")
root.geometry("1400x900")

# Create figure and axis
fig, ax = plt.subplots(figsize=(14, 10))

# Create canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Create dictionaries to store category and maturity checkboxes state
unchecked_categories = ['Data Prep', 'RAG', 'Computer Vision', 'NLP', 'RL', 'AI Ethics']
category_vars = {category: tk.BooleanVar(value=(category not in unchecked_categories)) for category in categories}

# Create a dictionary for maturity levels with 0.25 increments
maturity_levels = [f"{i:.2f}" for i in [j/4 for j in range(4, 21)]]  # 1.00 to 5.00 with 0.25 increments
maturity_vars = {level: tk.BooleanVar(value=(float(level) >= 3.5)) for level in maturity_levels}

# Add zoom factor
zoom_factor = 1.0

def plot_landscape():
    global zoom_factor
    ax.clear()
    
    # Determine the active maturity range
    active_maturity_levels = [float(level) for level, var in maturity_vars.items() if var.get()]
    if not active_maturity_levels:
        ax.text(0.5, 0.5, "No maturity levels selected", ha='center', va='center', transform=ax.transAxes)
        canvas.draw()
        return
    
    min_maturity = min(active_maturity_levels)
    max_maturity = max(active_maturity_levels)
    
    # Set up the plot
    ax.set_xlabel('Maturity Level')
    ax.set_xlim(min_maturity - 0.125, max_maturity + 0.125)
    xticks = [i/4 for i in range(int(min_maturity*4), int(max_maturity*4)+1)]
    ax.set_xticks(xticks)
    ax.set_xticklabels([f'{i:.2f}' for i in xticks], rotation=45, ha='right')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Group tools by category and maturity
    grouped_tools = defaultdict(list)
    for tool, data in tools.items():
        maturity = data['maturity']
        if (category_vars[data['category']].get() and 
            maturity_vars[f"{maturity:.2f}"].get()):
            grouped_tools[data['category']].append((tool, maturity))

    # Sort tools by maturity
    for category, tool_list in grouped_tools.items():
        grouped_tools[category] = sorted(tool_list, key=lambda x: x[1], reverse=True)

    # Set up y-axis
    categories_to_plot = list(grouped_tools.keys())
    ax.set_ylim(-0.5, len(categories_to_plot) - 0.5)
    ax.set_yticks(range(len(categories_to_plot)))
    ax.set_yticklabels(categories_to_plot)

    # Plot tools
    for y, (category, tool_list) in enumerate(grouped_tools.items()):
        for i, (tool, maturity) in enumerate(tool_list):
            x = maturity
            offset = (i - (len(tool_list) - 1) / 2) * 0.2
            if category_vars[category].get():
                ax.plot(x, y, 'ro', markersize=10)
            ax.annotate(tool, (x, y + offset), xytext=(20, 0), textcoords='offset points', ha='left', va='center',
                        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    ax.set_xlim(xlim[0]/zoom_factor, xlim[1]/zoom_factor)
    ax.set_ylim(ylim[0]/zoom_factor, ylim[1]/zoom_factor)

    # Adjust layout
    plt.tight_layout()
    canvas.draw()



def zoom_in():
    global zoom_factor
    zoom_factor *= 1.2
    plot_landscape()

def zoom_out():
    global zoom_factor
    zoom_factor /= 1.2
    plot_landscape()

def create_menu():
    menu = tk.Menu(root)
    root.config(menu=menu)
    
    category_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Categories", menu=category_menu)
    
    for category in categories:
        if category == 'Vector DB':
            category_menu.add_separator()
        category_menu.add_checkbutton(label=category, variable=category_vars[category], command=plot_landscape)

    maturity_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Maturity Levels", menu=maturity_menu)
    
    for level in maturity_levels:
        maturity_menu.add_checkbutton(label=level, variable=maturity_vars[level], command=plot_landscape)

    # Add Zoom menu
    zoom_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Zoom", menu=zoom_menu)
    zoom_menu.add_command(label="Zoom In", command=zoom_in)
    zoom_menu.add_command(label="Zoom Out", command=zoom_out)

# Create menu
create_menu()

# Initial plot
plot_landscape()

# Info display
info_frame = ttk.Frame(root)
info_frame.pack(fill=tk.X, padx=10, pady=10)
info_label = ttk.Label(info_frame, text="Use the 'Categories' and 'Maturity Levels' menus to filter the display. Use 'Zoom' menu to zoom in or out.", wraplength=1380)
info_label.pack()

# Run the application
root.mainloop()