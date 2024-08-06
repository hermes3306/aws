import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Define categories and tools (keep your existing definitions)
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

class AILandscapeViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("AI Landscape Viewer")
        self.geometry("1200x800")

        self.category_vars = [tk.BooleanVar(value=True) for _ in categories]
        self.maturity_vars = [tk.BooleanVar(value=True) for _ in range(1, 11)]
        self.font_size = 10

        self.create_menu()
        self.create_plot()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        category_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Category", menu=category_menu)
        for i, category in enumerate(categories):
            category_menu.add_checkbutton(label=category, variable=self.category_vars[i], command=self.update_plot)

        maturity_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Maturity", menu=maturity_menu)
        for i in range(10):
            maturity_menu.add_checkbutton(label=f"Level {i+1}", variable=self.maturity_vars[i], command=self.update_plot)

        font_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Font", menu=font_menu)
        font_menu.add_command(label="Increase (+)", command=self.increase_font)
        font_menu.add_command(label="Decrease (-)", command=self.decrease_font)

        menubar.add_command(label="Print", command=self.print_plot)

    def create_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        
        visible_categories = [cat for cat, var in zip(categories, self.category_vars) if var.get()]
        min_maturity = min((level for level, var in enumerate(self.maturity_vars, 1) if var.get()), default=1)
        max_maturity = max((level for level, var in enumerate(self.maturity_vars, 1) if var.get()), default=10)
        
        for i, (category, tools_in_category) in enumerate(zip(categories, tools)):
            if category in visible_categories:
                y = len(visible_categories) - 1 - visible_categories.index(category)
                for tool, maturity in tools_in_category:
                    if min_maturity <= maturity <= max_maturity:
                        self.ax.plot(maturity, y, 'ko', markersize=5)
                        self.ax.annotate(tool, (maturity, y), xytext=(15, 15), textcoords='offset points', 
                                    fontsize=self.font_size, rotation=45, ha='left', va='bottom',
                                    arrowprops=dict(arrowstyle='->', color='lightgray', lw=0.5))
        
        self.ax.set_yticks(range(len(visible_categories)))
        self.ax.set_yticklabels(visible_categories[::-1], fontsize=self.font_size)
        self.ax.set_xticks(range(min_maturity, max_maturity + 1))
        self.ax.set_xticklabels(range(min_maturity, max_maturity + 1), fontsize=self.font_size)
        self.ax.set_xlim(min_maturity - 0.5, max_maturity + 0.5)
        self.ax.set_ylim(-0.5, len(visible_categories) - 0.5)

        self.ax.grid(True, color='lightgray', linestyle='-', linewidth=0.2)
        self.ax.set_xlabel("Maturity Level", fontsize=self.font_size + 2)
        self.ax.set_ylabel("AI Technology Categories", fontsize=self.font_size + 2)
        
        for spine in self.ax.spines.values():
            spine.set_edgecolor('lightgray')

        self.canvas.draw()

    def increase_font(self):
        self.font_size += 1
        self.update_plot()

    def decrease_font(self):
        if self.font_size > 1:
            self.font_size -= 1
            self.update_plot()

    def print_plot(self):
        plt.savefig('ai_landscape.pdf', format='pdf', bbox_inches='tight')
        print("Plot saved as 'ai_landscape.pdf'")

if __name__ == "__main__":
    app = AILandscapeViewer()
    app.mainloop()