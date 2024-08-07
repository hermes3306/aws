import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Data
categories = [
    'Generative AI', 'Data-based Prediction', 'Game AI', 'Deep Learning Frameworks',
    'AI Hardware', 'AI Cloud', 'Data Prep', 'Fine-tuning', 'RAG', 'Computer Vision',
    'NLP', 'RL', 'AI Ethics', 'Model Serving', 'Vector DB', 'AI Development'
]

tools = {
    'ChatGPT': {'category': 'Generative AI', 'maturity': 4, 'url': 'https://openai.com/chatgpt', 
                'advantages': 'Versatile, good at understanding context', 
                'disadvantages': 'Can produce incorrect information'},
    'Claude': {'category': 'Generative AI', 'maturity': 4, 'url': 'https://www.anthropic.com', 
               'advantages': 'Strong reasoning capabilities, good at following instructions', 
               'disadvantages': 'Limited availability'},
    'LLaMA': {'category': 'Generative AI', 'maturity': 3, 'url': 'https://ai.meta.com/llama/', 
              'advantages': 'Open-source, customizable', 
              'disadvantages': 'Requires significant computational resources'},
    'MindsDB': {'category': 'Data-based Prediction', 'maturity': 4, 'url': 'https://mindsdb.com/', 
                'advantages': 'Easy to use, integrates with databases', 
                'disadvantages': 'Limited to tabular data'},
    'RapidMiner': {'category': 'Data-based Prediction', 'maturity': 5, 'url': 'https://rapidminer.com/', 
                   'advantages': 'Comprehensive suite of data science tools', 
                   'disadvantages': 'Can be complex for beginners'},
    'H2O.ai': {'category': 'Data-based Prediction', 'maturity': 4, 'url': 'https://www.h2o.ai/', 
               'advantages': 'Scalable, supports various ML algorithms', 
               'disadvantages': 'Steeper learning curve'},
    'TensorFlow': {'category': 'Deep Learning Frameworks', 'maturity': 5, 'url': 'https://www.tensorflow.org/', 
                   'advantages': 'Flexible, good performance', 
                   'disadvantages': 'Steep learning curve'},
    'PyTorch': {'category': 'Deep Learning Frameworks', 'maturity': 5, 'url': 'https://pytorch.org/', 
                'advantages': 'Dynamic computation graphs, pythonic', 
                'disadvantages': 'Smaller ecosystem than TensorFlow'},
    'NVIDIA GPUs': {'category': 'AI Hardware', 'maturity': 5, 'url': 'https://www.nvidia.com/en-us/gpu-cloud/', 
                    'advantages': 'High performance, CUDA ecosystem', 
                    'disadvantages': 'Expensive, high power consumption'},
    'Pinecone': {'category': 'Vector DB', 'maturity': 4, 'url': 'https://www.pinecone.io/', 
                 'advantages': 'Fast similarity search, scalable', 
                 'disadvantages': 'Hosted solution, can be expensive at scale'},
    'Milvus': {'category': 'Vector DB', 'maturity': 4, 'url': 'https://milvus.io/', 
               'advantages': 'Open-source, scalable, supports multiple index types', 
               'disadvantages': 'Complex setup for large-scale deployments'},
    'Weaviate': {'category': 'Vector DB', 'maturity': 3, 'url': 'https://www.semi.technology/developers/weaviate/current/', 
                 'advantages': 'GraphQL API, supports various data types', 
                 'disadvantages': 'Younger project, smaller community'},
    'Qdrant': {'category': 'Vector DB', 'maturity': 3, 'url': 'https://qdrant.tech/', 
               'advantages': 'Written in Rust, good performance', 
               'disadvantages': 'Relatively new, smaller ecosystem'},
    'Faiss': {'category': 'Vector DB', 'maturity': 4, 'url': 'https://github.com/facebookresearch/faiss', 
              'advantages': 'High performance, developed by Facebook Research', 
              'disadvantages': 'Primarily a library, not a full database solution'},
    'LangChain': {'category': 'AI Development', 'maturity': 3, 'url': 'https://langchain.com/', 
                  'advantages': 'Simplifies creation of LLM-powered applications', 
                  'disadvantages': 'Rapidly evolving, documentation can lag behind'}
}

# Create main window
root = tk.Tk()
root.title("AI Landscape")
root.geometry("1400x900")

# Create figure and axis
fig, ax = plt.subplots(figsize=(14, 10))

# Create a matrix representation
matrix = np.zeros((len(categories), len(tools)))
tool_names = list(tools.keys())

for i, category in enumerate(categories):
    for j, tool in enumerate(tool_names):
        if tools[tool]['category'] == category:
            matrix[i, j] = tools[tool]['maturity']

# Create custom colormap
from matplotlib.colors import LinearSegmentedColormap
colors = ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#FFDFBA', '#E0BBE4']
n_bins = len(colors)
cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

# Create heatmap
im = ax.imshow(matrix, cmap=cmap)

# Set labels
ax.set_xticks(np.arange(len(tool_names)))
ax.set_yticks(np.arange(len(categories)))
ax.set_xticklabels(tool_names, rotation=45, ha='right')
ax.set_yticklabels(categories)

# Add colorbar
cbar = ax.figure.colorbar(im, ax=ax)
cbar.ax.set_ylabel("Maturity", rotation=-90, va="bottom")

# Adjust layout
plt.tight_layout()

# Create canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Info display
info_frame = ttk.Frame(root)
info_frame.pack(fill=tk.X, padx=10, pady=10)
info_label = ttk.Label(info_frame, text="Click on a cell for more information", wraplength=1380)
info_label.pack()

# Click function
def on_click(event):
    if event.inaxes is not None:
        col = int(event.xdata + 0.5)
        row = int(event.ydata + 0.5)
        if 0 <= col < len(tool_names) and 0 <= row < len(categories):
            category = categories[row]
            tool = tool_names[col]
            if tools[tool]['category'] == category:
                data = tools[tool]
                info_text = f"Tool: {tool}\n"
                info_text += f"Category: {data['category']}\n"
                info_text += f"Maturity: {data['maturity']}\n"
                info_text += f"URL: {data['url']}\n"
                info_text += f"Advantages: {data['advantages']}\n"
                info_text += f"Disadvantages: {data['disadvantages']}"
                info_label.config(text=info_text)
            else:
                info_label.config(text="This tool does not belong to this category")
        else:
            info_label.config(text="Click on a cell for more information")

# Connect events
canvas.mpl_connect('button_press_event', on_click)

# Run the application
root.mainloop()