import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Set a professional color palette
sns.set_palette("deep")
plt.style.use('seaborn-v0_8-whitegrid')

# Define categories and tools with popularity scores
categories = [
    "NLP", "ML Platforms", "Vector Databases", "Conversational AI", 
    "Predictive Analytics", "Computer Vision", "AI Chipsets", "AI in Healthcare",
    "AI in Cybersecurity", "Robotics", "AI Cloud"
]

tools = [
    # NLP
    [("ChatGPT", 10.0), ("GPT-4", 9.5), ("Gemini", 8.7), ("Claude", 8.0), 
     ("GPT-3", 7.3), ("DALL-E", 6.6), ("LLaMA", 5.9), ("T5", 5.2), 
     ("BERT", 4.5), ("RoBERTa", 3.8), ("XLNet", 3.1)],
    
    # ML Platforms
    [("TensorFlow", 10.0), ("SageMaker", 9.1), ("Azure ML", 8.2), ("Databricks", 7.3), 
     ("DataRobot", 6.4), ("H2O.ai", 5.5), ("RapidMiner", 4.6), ("KNIME", 3.7), 
     ("MindsDB", 2.8)],
    
    # Vector Databases
    [("pgvector", 10.0), ("Pinecone", 8.7), ("Faiss", 7.4), ("Chroma", 6.1), 
     ("Weaviate", 4.8), ("Qdrant", 3.5), ("Vespa", 2.2), ("Milvus", 1.0)],
    
    # Conversational AI
    [("ChatGPT API", 10.0), ("Anthropic Claude", 8.6), ("Dialogflow", 7.2), 
     ("Amazon Lex", 5.8), ("Rasa", 4.4), ("IBM Watson Assistant", 3.0), 
     ("Wit.ai", 1.6), ("LUIS", 1.0)],
    
    # Predictive Analytics
    [("Scikit-learn", 10.0), ("XGBoost", 8.9), ("LightGBM", 7.8), ("AutoML", 6.7), 
     ("DataRobot", 5.6), ("ARIMA", 4.5), ("H2O.ai Driverless AI", 3.4), ("Prophet", 2.3)],
    
    # Computer Vision
    [("OpenAI DALL-E", 10.0), ("TensorFlow Object Detection", 8.7), ("YOLO", 7.4), 
     ("OpenCV", 6.1), ("Google Vision AI", 4.8), ("Azure Computer Vision", 3.5), 
     ("Mask R-CNN", 2.2), ("Caffe", 1.0)],
    
    # AI Chipsets
    [("NVIDIA H100", 10.0), ("NVIDIA A100", 8.7), ("Google TPU", 7.4), ("Apple M1", 6.1), 
     ("AMD Instinct", 4.8), ("Graphcore IPU", 3.5), ("Cerebras WSE", 2.2), ("Intel Nervana", 1.0)],
    
    # AI in Healthcare
    [("DeepMind Health", 10.0), ("Google Health", 8.7), ("Flatiron Health", 7.4), 
     ("Tempus", 6.1), ("Zebra Medical", 4.8), ("Atomwise", 3.5), 
     ("IBM Watson Health", 2.2), ("Butterfly Network", 1.0)],
    
    # AI in Cybersecurity
    [("CrowdStrike", 10.0), ("Darktrace", 8.7), ("FireEye", 7.4), ("Splunk", 6.1), 
     ("Vectra AI", 4.8), ("Rapid7", 3.5), ("Exabeam", 2.2), ("LogRhythm", 1.0)],
    
    # Robotics
    [("ROS", 10.0), ("NVIDIA Isaac", 8.5), ("OpenAI Gym", 7.0), ("MoveIt", 5.5), 
     ("Gazebo", 4.0), ("PyBullet", 2.5), ("Webots", 1.5), ("V-REP", 1.0)],
    
    # AI Cloud
    [("AWS SageMaker", 10.0), ("Google Cloud AI", 8.5), ("Microsoft Azure AI", 7.0), 
     ("IBM Watson Cloud", 5.5), ("Alibaba Cloud AI", 4.0), ("Huawei Cloud AI", 2.5), 
     ("Oracle AI Cloud", 1.0)]
]


class AILandscapeViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Landscape Viewer")
        self.geometry("1600x1000")  # Increased window size

        self.category_vars = [tk.BooleanVar(value=True) for _ in categories]
        self.popularity_vars = [tk.BooleanVar(value=i >= 1) for i in range(1, 11)]
        self.font_size = 10
        self.text_mode = tk.StringVar(value="half_angular")

        self.create_menu()
        self.create_plot()
        self.create_search_bar()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        category_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Category", menu=category_menu)
        for i, category in enumerate(categories):
            category_menu.add_checkbutton(label=category, variable=self.category_vars[i], command=self.update_plot)

        popularity_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Popularity", menu=popularity_menu)
        for i in range(10):
            popularity_menu.add_checkbutton(label=f"Level {i+1}", variable=self.popularity_vars[i], command=self.update_plot)

        font_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Font", menu=font_menu)
        font_menu.add_command(label="Increase (+)", command=self.increase_font)
        font_menu.add_command(label="Decrease (-)", command=self.decrease_font)

        text_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Text", menu=text_menu)
        text_menu.add_radiobutton(label="Horizontal", variable=self.text_mode, value="horizontal", command=self.update_plot)
        text_menu.add_radiobutton(label="Half Angular", variable=self.text_mode, value="half_angular", command=self.update_plot)
        text_menu.add_radiobutton(label="Angular", variable=self.text_mode, value="angular", command=self.update_plot)

        menubar.add_command(label="Save", command=self.save_plot)

    def create_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.update_plot()

    def update_plot(self):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        # Increase figure size
        self.fig.set_size_inches(16, 12)

        visible_categories = [cat for cat, var in zip(categories, self.category_vars) if var.get()]
        min_popularity = min((level for level, var in enumerate(self.popularity_vars, 1) if var.get()), default=1)
        max_popularity = max((level for level, var in enumerate(self.popularity_vars, 1) if var.get()), default=10)
        
        cmap = plt.get_cmap('viridis')
        norm = plt.Normalize(min_popularity, max_popularity)

        for i, (category, tools_in_category) in enumerate(zip(categories, tools)):
            if category in visible_categories:
                y = len(visible_categories) - 1 - visible_categories.index(category)
                for tool, popularity in tools_in_category:
                    if min_popularity <= popularity <= max_popularity:
                        color = cmap(norm(popularity))
                        self.ax.plot(popularity, y, 'o', color=color, markersize=8, alpha=0.7)
                        
                        if self.text_mode.get() == "horizontal":
                            self.ax.annotate(tool, (popularity, y), 
                                        xytext=(5, 0), textcoords='offset points', 
                                        fontsize=self.font_size, va='center', ha='left',
                                        bbox=dict(facecolor=color, edgecolor='none', alpha=0.6),
                                        annotation_clip=False)
                        elif self.text_mode.get() == "half_angular":
                            self.ax.annotate(tool, (popularity, y), xytext=(10, 10), textcoords='offset points', 
                                        fontsize=self.font_size, rotation=30, ha='left', va='bottom',
                                        bbox=dict(facecolor=color, edgecolor='none', alpha=0.6),
                                        arrowprops=dict(arrowstyle='->', color=color, connectionstyle="arc3,rad=0.1"))
                        else:  # Angular mode
                            self.ax.annotate(tool, (popularity, y), xytext=(15, 15), textcoords='offset points', 
                                        fontsize=self.font_size, rotation=45, ha='left', va='bottom',
                                        bbox=dict(facecolor=color, edgecolor='none', alpha=0.6),
                                        arrowprops=dict(arrowstyle='->', color=color, connectionstyle="arc3,rad=0.1"))
        
        self.ax.set_yticks(range(len(visible_categories)))
        self.ax.set_yticklabels(visible_categories[::-1], fontsize=self.font_size, fontweight='normal')
        self.ax.set_xticks(range(min_popularity, max_popularity + 1))
        self.ax.set_xticklabels(range(min_popularity, max_popularity + 1), fontsize=self.font_size, fontweight='normal')
        self.ax.set_xlim(min_popularity - 0.5, max_popularity + 0.5)
        self.ax.set_ylim(-0.5, len(visible_categories) - 0.5)

        self.ax.grid(True, color='lightgray', linestyle='--', linewidth=0.5, alpha=0.7)
        self.ax.set_xlabel("Market Presence and Popularity", fontsize=self.font_size + 4, fontweight='bold')
        self.ax.set_ylabel("AI Technology Categories", fontsize=self.font_size + 4, fontweight='bold')
        
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        self.ax.set_facecolor('#f5f5f5')
        self.fig.patch.set_facecolor('#f5f5f5')

        # Add color bar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])

        # Adjust subplot parameters to give more room on the right
        plt.subplots_adjust(right=0.85)

        # Add color bar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
                
        if hasattr(self, 'cbar'):
            self.cbar.remove()
        
        # Adjust colorbar position and size
        cbar_ax = self.fig.add_axes([0.87, 0.15, 0.02, 0.7])
        self.cbar = self.fig.colorbar(sm, cax=cbar_ax)
        self.cbar.set_label('Market Presence and Popularity', fontsize=self.font_size + 2)

        plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust layout but leave room for colorbar
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

    def create_search_bar(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def update_search(self, *args):
        search_term = self.search_var.get().lower()
        for i, (category, tools_in_category) in enumerate(zip(categories, tools)):
            for tool, _ in tools_in_category:
                if search_term in tool.lower() or search_term in category.lower():
                    print(f"Match found: {tool} in {category}")

if __name__ == "__main__":
    app = AILandscapeViewer()
    app.mainloop()