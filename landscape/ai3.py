import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import CheckButtons, Slider
from tkinter import Tk, Menu

# Categories and tools (same as before)
categories = [
    "NLP", "ML Platforms", "Vector Databases", "Conversational AI", 
    "Predictive Analytics", "Computer Vision", "AI Chipsets", "AI in Healthcare",
    "AI in Cybersecurity", "Robotics"
]

tools = [
    [("BERT", 5.5), ("RoBERTa", 6.2), ("XLNet", 6.5), ("T5", 7.0), ("GPT-3", 8.5), ("ChatGPT", 9.2), ("GPT-4", 9.8)],
    [("MindsDB", 6.0), ("H2O.ai", 7.2), ("RapidMiner", 7.5), ("KNIME", 7.8), ("DataRobot", 8.3), ("Databricks", 8.7), ("Azure ML", 9.0), ("SageMaker", 9.3), ("TensorFlow", 9.5)],
    [("Milvus", 5.5), ("Pinecone", 6.2), ("Weaviate", 6.8), ("Qdrant", 7.3), ("Vespa", 7.7), ("Faiss", 8.2), ("Chroma", 8.6), ("pgvector", 9.0)],
    [("LUIS", 6.0), ("Wit.ai", 6.5), ("IBM Watson Assistant", 7.2), ("Amazon Lex", 7.8), ("Rasa", 8.3), ("Dialogflow", 8.7), ("ChatGPT API", 9.5), ("Anthropic Claude", 9.2)],
    [("Prophet", 6.5), ("ARIMA", 7.0), ("Scikit-learn", 8.0), ("XGBoost", 8.5), ("LightGBM", 8.8), ("AutoML", 9.0), ("H2O.ai Driverless AI", 9.3), ("DataRobot", 9.5)],
    [("OpenCV", 7.5), ("Caffe", 7.8), ("YOLO", 8.3), ("Mask R-CNN", 8.7), ("TensorFlow Object Detection", 9.0), ("Google Vision AI", 9.3), ("Azure Computer Vision", 9.5), ("OpenAI DALL-E", 9.8)],
    [("Intel Nervana", 6.0), ("AMD Instinct", 7.0), ("Apple M1", 7.5), ("Google TPU", 8.5), ("Graphcore IPU", 8.8), ("Cerebras WSE", 9.0), ("NVIDIA A100", 9.5), ("NVIDIA H100", 9.8)],
    [("Butterfly Network", 6.5), ("Atomwise", 7.0), ("Zebra Medical", 7.5), ("Tempus", 8.0), ("Flatiron Health", 8.5), ("IBM Watson Health", 9.0), ("Google Health", 9.3), ("DeepMind Health", 9.5)],
    [("LogRhythm", 7.0), ("Exabeam", 7.5), ("Splunk", 8.0), ("Rapid7", 8.3), ("FireEye", 8.7), ("Vectra AI", 9.0), ("CrowdStrike", 9.3), ("Darktrace", 9.5)],
    [("V-REP", 6.0), ("Webots", 6.5), ("PyBullet", 7.0), ("OpenAI Gym", 7.5), ("Gazebo", 8.0), ("MoveIt", 8.5), ("ROS", 9.0), ("NVIDIA Isaac", 9.5)]
]

# Create the main window
root = Tk()
root.withdraw()  # Hide the main window

# Create the menubar
menubar = Menu(root)

# Create the File menu
file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label="Save")
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)

# Create the Edit menu
edit_menu = Menu(menubar, tearoff=0)
edit_menu.add_command(label="Copy")
edit_menu.add_command(label="Paste")
menubar.add_cascade(label="Edit", menu=edit_menu)

# Create the View menu
view_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="View", menu=view_menu)

# Create the About menu
about_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="About", menu=about_menu)

# Configure the root window to use the menubar
root.config(menu=menubar)

fig, (ax, ax_check) = plt.subplots(1, 2, figsize=(20, 10), gridspec_kw={'width_ratios': [3, 1]})
plt.subplots_adjust(left=0.1, right=0.95, bottom=0.2, top=0.9)

ax.set_facecolor('white')

lines = []
annotations = []

for i, category in enumerate(tools):
    y = i
    for tool, maturity in category:
        line, = ax.plot(maturity, y, 'bo', markersize=5)
        annotation = ax.annotate(tool, (maturity, y), xytext=(20, 20), textcoords='offset points', 
                    fontsize=8, rotation=45, ha='left', va='bottom',
                    arrowprops=dict(arrowstyle='->', color='blue', lw=0.5))
        lines.append(line)
        annotations.append(annotation)

ax.set_yticks(range(len(categories)))
ax.set_yticklabels(categories)
ax.set_xticks(range(1, 11))
ax.set_xlim(0.5, 10.5)
ax.set_ylim(-0.5, len(categories) - 0.5)

ax.grid(True, color='blue', linestyle='-', linewidth=0.2)
ax.set_title("AI Landscape: Technology Categories vs. Maturity Levels", fontsize=12)
ax.set_xlabel("Maturity Level", fontsize=10)
ax.set_ylabel("AI Technology Categories", fontsize=10)

# Add checkbuttons
check = CheckButtons(ax_check, categories, [True] * len(categories))

def func(label):
    index = categories.index(label)
    for line, annotation in zip(lines[index::len(categories)], annotations[index::len(categories)]):
        line.set_visible(not line.get_visible())
        annotation.set_visible(not annotation.get_visible())
    plt.draw()

check.on_clicked(func)

# Add font size slider
ax_slider = plt.axes([0.1, 0.05, 0.3, 0.03])
font_size_slider = Slider(ax_slider, 'Font Size', 6, 16, valinit=8, valstep=1)

def update_font_size(val):
    font_size = int(val)
    for annotation in annotations:
        annotation.set_fontsize(font_size)
    ax.set_title("AI Landscape: Technology Categories vs. Maturity Levels", fontsize=font_size+4)
    ax.set_xlabel("Maturity Level", fontsize=font_size+2)
    ax.set_ylabel("AI Technology Categories", fontsize=font_size+2)
    plt.draw()

font_size_slider.on_changed(update_font_size)

plt.tight_layout()
plt.show()

# Start the Tkinter event loop
root.mainloop()