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
    'ChatGPT': {'category': 'Generative AI', 'maturity': 4.75},
    'Claude': {'category': 'Generative AI', 'maturity': 4.50},
    'LLaMA': {'category': 'Generative AI', 'maturity': 3.75},
    'Gemini': {'category': 'Generative AI', 'maturity': 4.75},
    'DALL-E': {'category': 'Generative AI', 'maturity': 4.25},
    'Stable Diffusion': {'category': 'Generative AI', 'maturity': 3.75},
    'GPT-J': {'category': 'Generative AI', 'maturity': 3.25},

    'MindsDB': {'category': 'Data-based Prediction', 'maturity': 4.00},
    'RapidMiner': {'category': 'Data-based Prediction', 'maturity': 4.75},
    'H2O.ai': {'category': 'Data-based Prediction', 'maturity': 4.50},
    'DataRobot': {'category': 'Data-based Prediction', 'maturity': 4.75},
    'Prophet': {'category': 'Data-based Prediction', 'maturity': 4.00},
    'Auto-WEKA': {'category': 'Data-based Prediction', 'maturity': 3.50},
    'TPOT': {'category': 'Data-based Prediction', 'maturity': 3.50},

    'Unity ML-Agents': {'category': 'Game AI', 'maturity': 3.75},
    'Unreal Engine AI': {'category': 'Game AI', 'maturity': 4.25},
    'Godot AI': {'category': 'Game AI', 'maturity': 2.75},
    'OpenAI Gym': {'category': 'Game AI', 'maturity': 4.25},
    'DeepMind Lab': {'category': 'Game AI', 'maturity': 4.50},
    'AirSim': {'category': 'Game AI', 'maturity': 3.75},
    'PettingZoo': {'category': 'Game AI', 'maturity': 2.75},

    'TensorFlow': {'category': 'Deep Learning Frameworks', 'maturity': 5.00},
    'PyTorch': {'category': 'Deep Learning Frameworks', 'maturity': 5.00},
    'Keras': {'category': 'Deep Learning Frameworks', 'maturity': 4.75},
    'MXNet': {'category': 'Deep Learning Frameworks', 'maturity': 4.00},
    'Caffe': {'category': 'Deep Learning Frameworks', 'maturity': 3.50},
    'Theano': {'category': 'Deep Learning Frameworks', 'maturity': 3.00},
    'Paddle': {'category': 'Deep Learning Frameworks', 'maturity': 3.75},

    'NVIDIA GPUs': {'category': 'AI Hardware', 'maturity': 5.00},
    'Google TPUs': {'category': 'AI Hardware', 'maturity': 4.75},
    'Intel Nervana': {'category': 'AI Hardware', 'maturity': 3.50},
    'Apple Neural Engine': {'category': 'AI Hardware', 'maturity': 4.25},
    'Graphcore IPU': {'category': 'AI Hardware', 'maturity': 3.75},
    'Cerebras CS-2': {'category': 'AI Hardware', 'maturity': 3.75},
    'Groq TSP': {'category': 'AI Hardware', 'maturity': 2.75},

    'AWS SageMaker': {'category': 'AI Cloud', 'maturity': 5.00},
    'Google Cloud AI': {'category': 'AI Cloud', 'maturity': 5.00},
    'Azure Machine Learning': {'category': 'AI Cloud', 'maturity': 4.75},
    'IBM Watson Studio': {'category': 'AI Cloud', 'maturity': 4.50},
    'Alibaba Cloud PAI': {'category': 'AI Cloud', 'maturity': 4.25},
    'Oracle AI Cloud': {'category': 'AI Cloud', 'maturity': 3.75},
    'Baidu AI Cloud': {'category': 'AI Cloud', 'maturity': 3.75},

    'Pandas': {'category': 'Data Prep', 'maturity': 5.00},
    'Numpy': {'category': 'Data Prep', 'maturity': 5.00},
    'Dask': {'category': 'Data Prep', 'maturity': 4.50},
    'Vaex': {'category': 'Data Prep', 'maturity': 3.75},
    'Modin': {'category': 'Data Prep', 'maturity': 3.75},
    'CuDF': {'category': 'Data Prep', 'maturity': 3.75},
    'Polars': {'category': 'Data Prep', 'maturity': 2.75},

    'Hugging Face': {'category': 'Fine-tuning', 'maturity': 4.75},
    'OpenAI Fine-tuning': {'category': 'Fine-tuning', 'maturity': 4.50},
    'Google Cloud AutoML': {'category': 'Fine-tuning', 'maturity': 4.25},
    'Fast.ai': {'category': 'Fine-tuning', 'maturity': 3.75},
    'Ludwig': {'category': 'Fine-tuning', 'maturity': 3.50},
    'Kedro': {'category': 'Fine-tuning', 'maturity': 3.50},
    'Ray Tune': {'category': 'Fine-tuning', 'maturity': 3.75},

    'LangChain': {'category': 'RAG', 'maturity': 3.75},
    'Haystack': {'category': 'RAG', 'maturity': 3.50},
    'Semantic Kernel': {'category': 'RAG', 'maturity': 2.75},
    'LlamaIndex': {'category': 'RAG', 'maturity': 2.75},
    'Deepset FARM': {'category': 'RAG', 'maturity': 3.50},
    'Rasa': {'category': 'RAG', 'maturity': 4.25},
    'Botpress': {'category': 'RAG', 'maturity': 3.75},

    'OpenCV': {'category': 'Computer Vision', 'maturity': 5.00},
    'TensorFlow Object Detection': {'category': 'Computer Vision', 'maturity': 4.75},
    'YOLO': {'category': 'Computer Vision', 'maturity': 4.50},
    'Detectron2': {'category': 'Computer Vision', 'maturity': 4.25},
    'Mediapipe': {'category': 'Computer Vision', 'maturity': 3.75},
    'Kornia': {'category': 'Computer Vision', 'maturity': 3.50},
    'OpenPose': {'category': 'Computer Vision', 'maturity': 3.75},

    'NLTK': {'category': 'NLP', 'maturity': 4.75},
    'spaCy': {'category': 'NLP', 'maturity': 4.50},
    'Gensim': {'category': 'NLP', 'maturity': 4.25},
    'Transformers': {'category': 'NLP', 'maturity': 4.75},
    'AllenNLP': {'category': 'NLP', 'maturity': 3.75},
    'StanfordNLP': {'category': 'NLP', 'maturity': 4.25},
    'Flair': {'category': 'NLP', 'maturity': 3.75},

    'OpenAI Gym': {'category': 'RL', 'maturity': 4.50},
    'Stable Baselines3': {'category': 'RL', 'maturity': 3.75},
    'RLlib': {'category': 'RL', 'maturity': 3.75},
    'Dopamine': {'category': 'RL', 'maturity': 3.50},
    'Coach': {'category': 'RL', 'maturity': 3.50},
    'Acme': {'category': 'RL', 'maturity': 2.75},
    'KerasRL': {'category': 'RL', 'maturity': 2.75},

    'AI Ethics Toolkit': {'category': 'AI Ethics', 'maturity': 2.75},
    'Aequitas': {'category': 'AI Ethics', 'maturity': 3.50},
    'Fairlearn': {'category': 'AI Ethics', 'maturity': 3.75},
    'AI Fairness 360': {'category': 'AI Ethics', 'maturity': 3.75},
    'LIME': {'category': 'AI Ethics', 'maturity': 3.50},
    'SHAP': {'category': 'AI Ethics', 'maturity': 3.75},
    'What-If Tool': {'category': 'AI Ethics', 'maturity': 3.50},

    'TensorFlow Serving': {'category': 'Model Serving', 'maturity': 4.50},
    'TorchServe': {'category': 'Model Serving', 'maturity': 3.75},
    'Seldon Core': {'category': 'Model Serving', 'maturity': 3.75},
    'MLflow': {'category': 'Model Serving', 'maturity': 4.25},
    'BentoML': {'category': 'Model Serving', 'maturity': 3.75},
    'Cortex': {'category': 'Model Serving', 'maturity': 3.50},
    'KFServing': {'category': 'Model Serving', 'maturity': 3.75},

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
    'Streamlit': {'category': 'AI Development', 'maturity': 4.25},
    'Weights & Biases': {'category': 'AI Development', 'maturity': 4.25},
    'DVC': {'category': 'AI Development', 'maturity': 3.75},
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
category_vars = {category: tk.BooleanVar(value=True) for category in categories}
maturity_vars = {i: tk.BooleanVar(value=True) for i in range(1, 6)}


def plot_landscape():
    ax.clear()
    
    # Determine the active maturity range
    active_maturity_levels = [i for i in range(1, 6) if maturity_vars[i].get()]
    if not active_maturity_levels:
        ax.text(0.5, 0.5, "No maturity levels selected", ha='center', va='center', transform=ax.transAxes)
        canvas.draw()
        return
    
    min_maturity = min(active_maturity_levels)
    max_maturity = max(active_maturity_levels)
    
    # Set up the plot
    ax.set_xlabel('Maturity Level')
    ax.set_xlim(min_maturity - 0.25, max_maturity + 0.25)
    xticks = [i/4 for i in range(min_maturity*4, max_maturity*4+1)]
    ax.set_xticks(xticks)
    ax.set_xticklabels([f'{i:.2f}' for i in xticks], rotation=45, ha='right')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Group tools by category and maturity
    grouped_tools = defaultdict(list)
    for tool, data in tools.items():
        maturity = data['maturity']
        if (category_vars[data['category']].get() and 
            maturity_vars[int(maturity)].get()):
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
            # Only plot the red point if the category is chosen
            if category_vars[category].get():
                ax.plot(x, y, 'ro', markersize=10)
            ax.annotate(tool, (x, y + offset), xytext=(20, 0), textcoords='offset points', ha='left', va='center',
                        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    # Adjust layout
    plt.tight_layout()
    canvas.draw()

def create_menu():
    menu = tk.Menu(root)
    root.config(menu=menu)
    
    category_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Categories", menu=category_menu)
    
    for category in categories:
        category_menu.add_checkbutton(label=category, variable=category_vars[category], command=plot_landscape)

    maturity_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Maturity Levels", menu=maturity_menu)
    
    for i in range(1, 6):
        maturity_menu.add_checkbutton(label=f"Level {i}", variable=maturity_vars[i], command=plot_landscape)

# Create menu
create_menu()

# Initial plot
plot_landscape()

# Info display
info_frame = ttk.Frame(root)
info_frame.pack(fill=tk.X, padx=10, pady=10)
info_label = ttk.Label(info_frame, text="Use the 'Categories' and 'Maturity Levels' menus to filter the display", wraplength=1380)
info_label.pack()

# Run the application
root.mainloop()