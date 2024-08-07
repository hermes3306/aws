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
    'ChatGPT': {'category': 'Generative AI', 'maturity': 4.5},
    'Claude': {'category': 'Generative AI', 'maturity': 4.0},
    'LLaMA': {'category': 'Generative AI', 'maturity': 3.5},
    'Gemini': {'category': 'Generative AI', 'maturity': 4.5},
    'DALL-E': {'category': 'Generative AI', 'maturity': 4.0},
    'Stable Diffusion': {'category': 'Generative AI', 'maturity': 3.5},
    'GPT-J': {'category': 'Generative AI', 'maturity': 3.0},

    'MindsDB': {'category': 'Data-based Prediction', 'maturity': 4.0},
    'RapidMiner': {'category': 'Data-based Prediction', 'maturity': 5.0},
    'H2O.ai': {'category': 'Data-based Prediction', 'maturity': 4.5},
    'DataRobot': {'category': 'Data-based Prediction', 'maturity': 5.0},
    'Prophet': {'category': 'Data-based Prediction', 'maturity': 4.0},
    'Auto-WEKA': {'category': 'Data-based Prediction', 'maturity': 3.5},
    'TPOT': {'category': 'Data-based Prediction', 'maturity': 3.5},

    'Unity ML-Agents': {'category': 'Game AI', 'maturity': 3.5},
    'Unreal Engine AI': {'category': 'Game AI', 'maturity': 4.0},
    'Godot AI': {'category': 'Game AI', 'maturity': 2.5},
    'OpenAI Gym': {'category': 'Game AI', 'maturity': 4.0},
    'DeepMind Lab': {'category': 'Game AI', 'maturity': 4.5},
    'AirSim': {'category': 'Game AI', 'maturity': 3.5},
    'PettingZoo': {'category': 'Game AI', 'maturity': 2.5},

    'TensorFlow': {'category': 'Deep Learning Frameworks', 'maturity': 5.0},
    'PyTorch': {'category': 'Deep Learning Frameworks', 'maturity': 5.0},
    'Keras': {'category': 'Deep Learning Frameworks', 'maturity': 4.5},
    'MXNet': {'category': 'Deep Learning Frameworks', 'maturity': 4.0},
    'Caffe': {'category': 'Deep Learning Frameworks', 'maturity': 3.5},
    'Theano': {'category': 'Deep Learning Frameworks', 'maturity': 3.0},
    'Paddle': {'category': 'Deep Learning Frameworks', 'maturity': 3.5},

    'NVIDIA GPUs': {'category': 'AI Hardware', 'maturity': 5.0},
    'Google TPUs': {'category': 'AI Hardware', 'maturity': 4.5},
    'Intel Nervana': {'category': 'AI Hardware', 'maturity': 3.5},
    'Apple Neural Engine': {'category': 'AI Hardware', 'maturity': 4.0},
    'Graphcore IPU': {'category': 'AI Hardware', 'maturity': 3.5},
    'Cerebras CS-2': {'category': 'AI Hardware', 'maturity': 3.5},
    'Groq TSP': {'category': 'AI Hardware', 'maturity': 2.5},

    'AWS SageMaker': {'category': 'AI Cloud', 'maturity': 5.0},
    'Google Cloud AI': {'category': 'AI Cloud', 'maturity': 5.0},
    'Azure Machine Learning': {'category': 'AI Cloud', 'maturity': 5.0},
    'IBM Watson Studio': {'category': 'AI Cloud', 'maturity': 4.5},
    'Alibaba Cloud PAI': {'category': 'AI Cloud', 'maturity': 4.0},
    'Oracle AI Cloud': {'category': 'AI Cloud', 'maturity': 3.5},
    'Baidu AI Cloud': {'category': 'AI Cloud', 'maturity': 3.5},

    'Pandas': {'category': 'Data Prep', 'maturity': 5.0},
    'Numpy': {'category': 'Data Prep', 'maturity': 5.0},
    'Dask': {'category': 'Data Prep', 'maturity': 4.5},
    'Vaex': {'category': 'Data Prep', 'maturity': 3.5},
    'Modin': {'category': 'Data Prep', 'maturity': 3.5},
    'CuDF': {'category': 'Data Prep', 'maturity': 3.5},
    'Polars': {'category': 'Data Prep', 'maturity': 2.5},

    'Hugging Face': {'category': 'Fine-tuning', 'maturity': 4.5},
    'OpenAI Fine-tuning': {'category': 'Fine-tuning', 'maturity': 4.5},
    'Google Cloud AutoML': {'category': 'Fine-tuning', 'maturity': 4.0},
    'Fast.ai': {'category': 'Fine-tuning', 'maturity': 3.5},
    'Ludwig': {'category': 'Fine-tuning', 'maturity': 3.5},
    'Kedro': {'category': 'Fine-tuning', 'maturity': 3.5},
    'Ray Tune': {'category': 'Fine-tuning', 'maturity': 3.5},

    'LangChain': {'category': 'RAG', 'maturity': 3.5},
    'Haystack': {'category': 'RAG', 'maturity': 3.5},
    'Semantic Kernel': {'category': 'RAG', 'maturity': 2.5},
    'LlamaIndex': {'category': 'RAG', 'maturity': 2.5},
    'Deepset FARM': {'category': 'RAG', 'maturity': 3.5},
    'Rasa': {'category': 'RAG', 'maturity': 4.0},
    'Botpress': {'category': 'RAG', 'maturity': 3.5},

    'OpenCV': {'category': 'Computer Vision', 'maturity': 5.0},
    'TensorFlow Object Detection': {'category': 'Computer Vision', 'maturity': 4.5},
    'YOLO': {'category': 'Computer Vision', 'maturity': 4.5},
    'Detectron2': {'category': 'Computer Vision', 'maturity': 4.0},
    'Mediapipe': {'category': 'Computer Vision', 'maturity': 3.5},
    'Kornia': {'category': 'Computer Vision', 'maturity': 3.5},
    'OpenPose': {'category': 'Computer Vision', 'maturity': 3.5},

    'NLTK': {'category': 'NLP', 'maturity': 5.0},
    'spaCy': {'category': 'NLP', 'maturity': 4.5},
    'Gensim': {'category': 'NLP', 'maturity': 4.0},
    'Transformers': {'category': 'NLP', 'maturity': 4.5},
    'AllenNLP': {'category': 'NLP', 'maturity': 3.5},
    'StanfordNLP': {'category': 'NLP', 'maturity': 4.0},
    'Flair': {'category': 'NLP', 'maturity': 3.5},

    'OpenAI Gym': {'category': 'RL', 'maturity': 4.5},
    'Stable Baselines3': {'category': 'RL', 'maturity': 3.5},
    'RLlib': {'category': 'RL', 'maturity': 3.5},
    'Dopamine': {'category': 'RL', 'maturity': 3.5},
    'Coach': {'category': 'RL', 'maturity': 3.5},
    'Acme': {'category': 'RL', 'maturity': 2.5},
    'KerasRL': {'category': 'RL', 'maturity': 2.5},

    'AI Ethics Toolkit': {'category': 'AI Ethics', 'maturity': 2.5},
    'Aequitas': {'category': 'AI Ethics', 'maturity': 3.5},
    'Fairlearn': {'category': 'AI Ethics', 'maturity': 3.5},
    'AI Fairness 360': {'category': 'AI Ethics', 'maturity': 3.5},
    'LIME': {'category': 'AI Ethics', 'maturity': 3.5},
    'SHAP': {'category': 'AI Ethics', 'maturity': 3.5},
    'What-If Tool': {'category': 'AI Ethics', 'maturity': 3.5},

    'TensorFlow Serving': {'category': 'Model Serving', 'maturity': 4.5},
    'TorchServe': {'category': 'Model Serving', 'maturity': 3.5},
    'Seldon Core': {'category': 'Model Serving', 'maturity': 3.5},
    'MLflow': {'category': 'Model Serving', 'maturity': 4.0},
    'BentoML': {'category': 'Model Serving', 'maturity': 3.5},
    'Cortex': {'category': 'Model Serving', 'maturity': 3.5},
    'KFServing': {'category': 'Model Serving', 'maturity': 3.5},

    'Pinecone': {'category': 'Vector DB', 'maturity': 4.0},
    'Milvus': {'category': 'Vector DB', 'maturity': 4.0},
    'Weaviate': {'category': 'Vector DB', 'maturity': 3.5},
    'Qdrant': {'category': 'Vector DB', 'maturity': 3.5},
    'Faiss': {'category': 'Vector DB', 'maturity': 4.0},
    'Vespa': {'category': 'Vector DB', 'maturity': 4.0},
    'Chroma': {'category': 'Vector DB', 'maturity': 2.5},

    'LangChain': {'category': 'AI Development', 'maturity': 3.5},
    'AutoML': {'category': 'AI Development', 'maturity': 4.0},
    'RAPIDS': {'category': 'AI Development', 'maturity': 3.5},
    'Gradio': {'category': 'AI Development', 'maturity': 3.5},
    'Streamlit': {'category': 'AI Development', 'maturity': 4.0},
    'Weights & Biases': {'category': 'AI Development', 'maturity': 4.0},
    'DVC': {'category': 'AI Development', 'maturity': 3.5},
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
    ax.set_xlim(0.5, 5.5)
    ax.set_xticks([i/2 for i in range(2, 11)])
    ax.set_xticklabels([f'{i/2:.1f}' for i in range(2, 11)])
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
