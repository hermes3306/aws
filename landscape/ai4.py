import numpy as np
import matplotlib.colors as mcolors
import seaborn as sns
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

print(plt.style.available)

# Set a professional color palette
sns.set_palette("deep")

# Use the updated seaborn style name
plt.style.use('seaborn-v0_8-whitegrid')

# Define categories and tools with color hints
categories = [
    "NLP", "ML Platforms", "Vector Databases", "Conversational AI", 
    "Predictive Analytics", "Computer Vision", "AI Chipsets", "AI in Healthcare",
    "AI in Cybersecurity", "Robotics", "AI Cloud"
]

tools = [
    [("BERT", 5.5, "#0062B1"), ("RoBERTa", 6.2, "#FF6F00"), ("XLNet", 6.5, "#4285F4"), ("T5", 7.0, "#34A853"), 
     ("GPT-3", 8.5, "#10A37F"), ("ChatGPT", 9.2, "#10A37F"), ("GPT-4", 9.8, "#10A37F"), 
     ("Claude", 9.3, "#000000"), ("LLaMA", 8.8, "#792EE5"), ("Gemini", 9.5, "#8E24AA"),  ("DALL-E", 9.0, "#10A37F")],
    [("MindsDB", 6.0, "#00AEEF"), ("H2O.ai", 7.2, "#F7A61E"), ("RapidMiner", 7.5, "#E47C00"), ("KNIME", 7.8, "#FDB813"), 
     ("DataRobot", 8.3, "#771C85"), ("Databricks", 8.7, "#FF3621"), ("Azure ML", 9.0, "#00A4EF"), ("SageMaker", 9.3, "#FF9900"), 
     ("TensorFlow", 9.5, "#FF6F00")],
    [("Milvus", 5.5, "#00A7B5"), ("Pinecone", 6.2, "#5294CF"), ("Weaviate", 6.8, "#3FE1AD"), ("Qdrant", 7.3, "#4B31C3"), 
     ("Vespa", 7.7, "#FF5745"), ("Faiss", 8.2, "#3366CC"), ("Chroma", 8.6, "#9B30FF"), ("pgvector", 9.0, "#336791")],
    [("LUIS", 6.0, "#00A4EF"), ("Wit.ai", 6.5, "#4080FF"), ("IBM Watson Assistant", 7.2, "#054ADA"), 
     ("Amazon Lex", 7.8, "#FF9900"), ("Rasa", 8.3, "#5A17EE"), ("Dialogflow", 8.7, "#FF9800"), 
     ("ChatGPT API", 9.5, "#10A37F"), ("Anthropic Claude", 9.2, "#000000")],
    [("Prophet", 6.5, "#3B5998"), ("ARIMA", 7.0, "#4285F4"), ("Scikit-learn", 8.0, "#F7931E"), ("XGBoost", 8.5, "#003D7C"), 
     ("LightGBM", 8.8, "#3499CD"), ("AutoML", 9.0, "#FF6F00"), ("H2O.ai Driverless AI", 9.3, "#F7A61E"), 
     ("DataRobot", 9.5, "#771C85")],
    [("OpenCV", 7.5, "#5C3EE8"), ("Caffe", 7.8, "#C61A3F"), ("YOLO", 8.3, "#00FFFF"), ("Mask R-CNN", 8.7, "#4285F4"), 
     ("TensorFlow Object Detection", 9.0, "#FF6F00"), ("Google Vision AI", 9.3, "#4285F4"), 
     ("Azure Computer Vision", 9.5, "#00A4EF"), ("OpenAI DALL-E", 9.8, "#10A37F")],
    [("Intel Nervana", 6.0, "#0071C5"), ("AMD Instinct", 7.0, "#ED1C24"), ("Apple M1", 7.5, "#A2AAAD"), 
     ("Google TPU", 8.5, "#4285F4"), ("Graphcore IPU", 8.8, "#FF5800"), ("Cerebras WSE", 9.0, "#00A3E0"), 
     ("NVIDIA A100", 9.5, "#76B900"), ("NVIDIA H100", 9.8, "#76B900")],
    [("Butterfly Network", 6.5, "#1CA0DE"), ("Atomwise", 7.0, "#2CD889"), ("Zebra Medical", 7.5, "#0077C8"), 
     ("Tempus", 8.0, "#00B9E4"), ("Flatiron Health", 8.5, "#2C3E50"), ("IBM Watson Health", 9.0, "#054ADA"), 
     ("Google Health", 9.3, "#4285F4"), ("DeepMind Health", 9.5, "#00A3E0")],
    [("LogRhythm", 7.0, "#00B1B0"), ("Exabeam", 7.5, "#2C3E50"), ("Splunk", 8.0, "#65A637"), ("Rapid7", 8.3, "#FF5733"), 
     ("FireEye", 8.7, "#F4762F"), ("Vectra AI", 9.0, "#7D2E68"), ("CrowdStrike", 9.3, "#FF0000"), ("Darktrace", 9.5, "#67E767")],
    [("V-REP", 6.0, "#E74C3C"), ("Webots", 6.5, "#3498DB"), ("PyBullet", 7.0, "#F1C40F"), ("OpenAI Gym", 7.5, "#2ECC71"), 
     ("Gazebo", 8.0, "#9B59B6"), ("MoveIt", 8.5, "#FF69B4"), ("ROS", 9.0, "#22A7F0"), ("NVIDIA Isaac", 9.5, "#76B900")],
    [("AWS SageMaker", 9.0, "#FF9900"), ("Google Cloud AI", 9.2, "#4285F4"), ("Microsoft Azure AI", 9.1, "#00A4EF"), 
     ("IBM Watson Cloud", 8.8, "#054ADA"), ("Oracle AI Cloud", 8.5, "#F80000"), ("Alibaba Cloud AI", 8.7, "#FF6A00"), 
     ("Huawei Cloud AI", 8.6, "#FF0000")]
]

class AILandscapeViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Landscape Viewer")
        self.geometry("1400x900")

        self.category_vars = [tk.BooleanVar(value=True) for _ in categories]
        self.maturity_vars = [tk.BooleanVar(value=i >= 5) for i in range(1, 11)]
        self.font_size = 11
        self.text_mode = tk.StringVar(value="half_angular")  # Default to half angular

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

        text_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Text", menu=text_menu)
        text_menu.add_radiobutton(label="Horizontal", variable=self.text_mode, value="horizontal", command=self.update_plot)
        text_menu.add_radiobutton(label="Half Angular", variable=self.text_mode, value="half_angular", command=self.update_plot)
        text_menu.add_radiobutton(label="Angular", variable=self.text_mode, value="angular", command=self.update_plot)

        menubar.add_command(label="Save", command=lambda: self.save_plot())


    def create_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
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
                for tool, maturity, color in tools_in_category:
                    if min_maturity <= maturity <= max_maturity:
                        self.ax.plot(maturity, y, 'o', color=color, markersize=8, alpha=0.7)
                        if self.text_mode.get() == "horizontal":
                            self.ax.annotate(tool, (maturity, y), 
                                        xytext=(5, 0), textcoords='offset points', 
                                        fontsize=self.font_size, va='center',
                                        ha='left', annotation_clip=False)
                        elif self.text_mode.get() == "half_angular":
                            self.ax.annotate(tool, (maturity, y), xytext=(10, 10), textcoords='offset points', 
                                        fontsize=self.font_size, rotation=30, ha='left', va='bottom',
                                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7),
                                        arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=0.1"))
                        else:  # Angular mode
                            self.ax.annotate(tool, (maturity, y), xytext=(15, 15), textcoords='offset points', 
                                        fontsize=self.font_size, rotation=45, ha='left', va='bottom',
                                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7),
                                        arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=0.1"))
        
        self.ax.set_yticks(range(len(visible_categories)))
        self.ax.set_yticklabels(visible_categories[::-1], fontsize=self.font_size, fontweight='normal')
        self.ax.set_xticks(range(min_maturity, max_maturity + 1))
        self.ax.set_xticklabels(range(min_maturity, max_maturity + 1), fontsize=self.font_size, fontweight='normal')
        self.ax.set_xlim(min_maturity - 0.5, max_maturity + 0.5)
        self.ax.set_ylim(-0.5, len(visible_categories) - 0.5)

        self.ax.grid(True, color='lightgray', linestyle='--', linewidth=0.5, alpha=0.7)
        self.ax.set_xlabel("Maturity Level", fontsize=self.font_size + 4, fontweight='bold')
        self.ax.set_ylabel("AI Technology Categories", fontsize=self.font_size + 4, fontweight='bold')
        
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        self.ax.set_facecolor('#f5f5f5')
        self.fig.patch.set_facecolor('#f5f5f5')

        plt.tight_layout()
        self.canvas.draw()

    def increase_font(self):
        self.font_size += 1
        self.update_plot()

    def decrease_font(self):
        if self.font_size > 1:
            self.font_size -= 1
        self.update_plot()

    def save_plot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if file_path:
            self.fig.savefig(file_path, format='pdf', bbox_inches='tight')
            print(f"Plot saved as '{file_path}'")

if __name__ == "__main__":
    app = AILandscapeViewer()
    app.mainloop()