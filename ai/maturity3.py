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
    'ChatGPT': {'category': 'Generative AI', 'maturity': 4},
    'Claude': {'category': 'Generative AI', 'maturity': 4},
    'LLaMA': {'category': 'Generative AI', 'maturity': 3},
    'Gemini': {'category': 'Generative AI', 'maturity': 4},
    'DALL-E': {'category': 'Generative AI', 'maturity': 4},
    'Stable Diffusion': {'category': 'Generative AI', 'maturity': 3},
    'GPT-J': {'category': 'Generative AI', 'maturity': 3},

    'MindsDB': {'category': 'Data-based Prediction', 'maturity': 4},
    'RapidMiner': {'category': 'Data-based Prediction', 'maturity': 5},
    'H2O.ai': {'category': 'Data-based Prediction', 'maturity': 4},
    'DataRobot': {'category': 'Data-based Prediction', 'maturity': 5},
    'Prophet': {'category': 'Data-based Prediction', 'maturity': 4},
    'Auto-WEKA': {'category': 'Data-based Prediction', 'maturity': 3},
    'TPOT': {'category': 'Data-based Prediction', 'maturity': 3},

    'Unity ML-Agents': {'category': 'Game AI', 'maturity': 3},
    'Unreal Engine AI': {'category': 'Game AI', 'maturity': 4},
    'Godot AI': {'category': 'Game AI', 'maturity': 2},
    'OpenAI Gym': {'category': 'Game AI', 'maturity': 4},
    'DeepMind Lab': {'category': 'Game AI', 'maturity': 4},
    'AirSim': {'category': 'Game AI', 'maturity': 3},
    'PettingZoo': {'category': 'Game AI', 'maturity': 2},

    'TensorFlow': {'category': 'Deep Learning Frameworks', 'maturity': 5},
    'PyTorch': {'category': 'Deep Learning Frameworks', 'maturity': 5},
    'Keras': {'category': 'Deep Learning Frameworks', 'maturity': 4},
    'MXNet': {'category': 'Deep Learning Frameworks', 'maturity': 4},
    'Caffe': {'category': 'Deep Learning Frameworks', 'maturity': 3},
    'Theano': {'category': 'Deep Learning Frameworks', 'maturity': 3},
    'Paddle': {'category': 'Deep Learning Frameworks', 'maturity': 3},

    'NVIDIA GPUs': {'category': 'AI Hardware', 'maturity': 5},
    'Google TPUs': {'category': 'AI Hardware', 'maturity': 4},
    'Intel Nervana': {'category': 'AI Hardware', 'maturity': 3},
    'Apple Neural Engine': {'category': 'AI Hardware', 'maturity': 4},
    'Graphcore IPU': {'category': 'AI Hardware', 'maturity': 3},
    'Cerebras CS-2': {'category': 'AI Hardware', 'maturity': 3},
    'Groq TSP': {'category': 'AI Hardware', 'maturity': 2},

    'AWS SageMaker': {'category': 'AI Cloud', 'maturity': 5},
    'Google Cloud AI': {'category': 'AI Cloud', 'maturity': 5},
    'Azure Machine Learning': {'category': 'AI Cloud', 'maturity': 5},
    'IBM Watson Studio': {'category': 'AI Cloud', 'maturity': 4},
    'Alibaba Cloud PAI': {'category': 'AI Cloud', 'maturity': 4},
    'Oracle AI Cloud': {'category': 'AI Cloud', 'maturity': 3},
    'Baidu AI Cloud': {'category': 'AI Cloud', 'maturity': 3},

    'Pandas': {'category': 'Data Prep', 'maturity': 5},
    'Numpy': {'category': 'Data Prep', 'maturity': 5},
    'Dask': {'category': 'Data Prep', 'maturity': 4},
    'Vaex': {'category': 'Data Prep', 'maturity': 3},
    'Modin': {'category': 'Data Prep', 'maturity': 3},
    'CuDF': {'category': 'Data Prep', 'maturity': 3},
    'Polars': {'category': 'Data Prep', 'maturity': 2},

    'Hugging Face': {'category': 'Fine-tuning', 'maturity': 4},
    'OpenAI Fine-tuning': {'category': 'Fine-tuning', 'maturity': 4},
    'Google Cloud AutoML': {'category': 'Fine-tuning', 'maturity': 4},
    'Fast.ai': {'category': 'Fine-tuning', 'maturity': 3},
    'Ludwig': {'category': 'Fine-tuning', 'maturity': 3},
    'Kedro': {'category': 'Fine-tuning', 'maturity': 3},
    'Ray Tune': {'category': 'Fine-tuning', 'maturity': 3},

    'LangChain': {'category': 'RAG', 'maturity': 3},
    'Haystack': {'category': 'RAG', 'maturity': 3},
    'Semantic Kernel': {'category': 'RAG', 'maturity': 2},
    'LlamaIndex': {'category': 'RAG', 'maturity': 2},
    'Deepset FARM': {'category': 'RAG', 'maturity': 3},
    'Rasa': {'category': 'RAG', 'maturity': 4},
    'Botpress': {'category': 'RAG', 'maturity': 3},

    'OpenCV': {'category': 'Computer Vision', 'maturity': 5},
    'TensorFlow Object Detection': {'category': 'Computer Vision', 'maturity': 4},
    'YOLO': {'category': 'Computer Vision', 'maturity': 4},
    'Detectron2': {'category': 'Computer Vision', 'maturity': 4},
    'Mediapipe': {'category': 'Computer Vision', 'maturity': 3},
    'Kornia': {'category': 'Computer Vision', 'maturity': 3},
    'OpenPose': {'category': 'Computer Vision', 'maturity': 3},

    'NLTK': {'category': 'NLP', 'maturity': 5},
    'spaCy': {'category': 'NLP', 'maturity': 4},
    'Gensim': {'category': 'NLP', 'maturity': 4},
    'Transformers': {'category': 'NLP', 'maturity': 4},
    'AllenNLP': {'category': 'NLP', 'maturity': 3},
    'StanfordNLP': {'category': 'NLP', 'maturity': 4},
    'Flair': {'category': 'NLP', 'maturity': 3},

    'OpenAI Gym': {'category': 'RL', 'maturity': 4},
    'Stable Baselines3': {'category': 'RL', 'maturity': 3},
    'RLlib': {'category': 'RL', 'maturity': 3},
    'Dopamine': {'category': 'RL', 'maturity': 3},
    'Coach': {'category': 'RL', 'maturity': 3},
    'Acme': {'category': 'RL', 'maturity': 2},
    'KerasRL': {'category': 'RL', 'maturity': 2},

    'AI Ethics Toolkit': {'category': 'AI Ethics', 'maturity': 2},
    'Aequitas': {'category': 'AI Ethics', 'maturity': 3},
    'Fairlearn': {'category': 'AI Ethics', 'maturity': 3},
    'AI Fairness 360': {'category': 'AI Ethics', 'maturity': 3},
    'LIME': {'category': 'AI Ethics', 'maturity': 3},
    'SHAP': {'category': 'AI Ethics', 'maturity': 3},
    'What-If Tool': {'category': 'AI Ethics', 'maturity': 3},

    'TensorFlow Serving': {'category': 'Model Serving', 'maturity': 4},
    'TorchServe': {'category': 'Model Serving', 'maturity': 3},
    'Seldon Core': {'category': 'Model Serving', 'maturity': 3},
    'MLflow': {'category': 'Model Serving', 'maturity': 4},
    'BentoML': {'category': 'Model Serving', 'maturity': 3},
    'Cortex': {'category': 'Model Serving', 'maturity': 3},
    'KFServing': {'category': 'Model Serving', 'maturity': 3},

    'Pinecone': {'category': 'Vector DB', 'maturity': 4},
    'Milvus': {'category': 'Vector DB', 'maturity': 4},
    'Weaviate': {'category': 'Vector DB', 'maturity': 3},
    'Qdrant': {'category': 'Vector DB', 'maturity': 3},
    'Faiss': {'category': 'Vector DB', 'maturity': 4},
    'Vespa': {'category': 'Vector DB', 'maturity': 4},
    'Chroma': {'category': 'Vector DB', 'maturity': 2},

    'LangChain': {'category': 'AI Development', 'maturity': 3},
    'AutoML': {'category': 'AI Development', 'maturity': 4},
    'RAPIDS': {'category': 'AI Development', 'maturity': 3},
    'Gradio': {'category': 'AI Development', 'maturity': 3},
    'Streamlit': {'category': 'AI Development', 'maturity': 4},
    'Weights & Biases': {'category': 'AI Development', 'maturity': 4},
    'DVC': {'category': 'AI Development', 'maturity': 3},
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

# Create a dictionary to store category checkboxes state
category_vars = {category: tk.BooleanVar(value=True) for category in categories}

def plot_landscape():
    ax.clear()
    
    # Set up the plot
    ax.set_xlabel('Maturity Level')
    ax.set_xticks(range(1, 6))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Group tools by category and maturity
    grouped_tools = defaultdict(list)
    for tool, data in tools.items():
        if category_vars[data['category']].get():
            grouped_tools[data['category']].append((tool, data['maturity']))

    # Sort tools by maturity and get top 3 for unchecked categories
    for category, tool_list in grouped_tools.items():
        sorted_tools = sorted(tool_list, key=lambda x: x[1], reverse=True)
        if not category_vars[category].get():
            grouped_tools[category] = sorted_tools[:3]
        else:
            grouped_tools[category] = sorted_tools

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

# Create menu
create_menu()

# Initial plot
plot_landscape()

# Info display
info_frame = ttk.Frame(root)
info_frame.pack(fill=tk.X, padx=10, pady=10)
info_label = ttk.Label(info_frame, text="Use the 'Categories' menu to select which categories to display in detail", wraplength=1380)
info_label.pack()

# Run the application
root.mainloop()
