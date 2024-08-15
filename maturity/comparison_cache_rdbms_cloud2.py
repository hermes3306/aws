import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

categories = ['Cache', 'RDBMS', 'NoSQL']

subcategories = [
    'Scalability',
    'Cloud managed',
    'Transaction support',
    'SQL support',
    'ACID support',
    'Popularity',
    'OLTP compliance',
    'OLAP compliance',
    'Cost',
    'Management and Monitoring tool support',
    'Ecosystems',
    'Communities',
    'Documentation and related blogs support',
    'Deployment'
]

tools = {
    'Redis': {
        'category': 'Cache',
        'Scalability': 4.5,
        'Cloud managed': 4.0,
        'Transaction support': 3.0,
        'SQL support': 2.0,
        'ACID support': 3.0,
        'Popularity': 5.0,
        'OLTP compliance': 3.5,
        'OLAP compliance': 2.0,
        'Cost': 4.0,
        'Management and Monitoring tool support': 4.0,
        'Ecosystems': 4.5,
        'Communities': 4.5,
        'Documentation and related blogs support': 4.5,
        'Deployment': 4.0
    },
    'Memcached': {
        'category': 'Cache',
        'Scalability': 4.0,
        'Cloud managed': 3.5,
        'Transaction support': 2.0,
        'SQL support': 1.0,
        'ACID support': 2.0,
        'Popularity': 4.0,
        'OLTP compliance': 3.0,
        'OLAP compliance': 1.5,
        'Cost': 4.5,
        'Management and Monitoring tool support': 3.5,
        'Ecosystems': 3.5,
        'Communities': 4.0,
        'Documentation and related blogs support': 4.0,
        'Deployment': 3.5
    },
    'PostgreSQL': {
        'category': 'RDBMS',
        'Scalability': 4.0,
        'Cloud managed': 4.5,
        'Transaction support': 5.0,
        'SQL support': 5.0,
        'ACID support': 5.0,
        'Popularity': 4.5,
        'OLTP compliance': 5.0,
        'OLAP compliance': 4.0,
        'Cost': 4.5,
        'Management and Monitoring tool support': 4.5,
        'Ecosystems': 4.5,
        'Communities': 5.0,
        'Documentation and related blogs support': 5.0,
        'Deployment': 4.0
    },
    'MySQL': {
        'category': 'RDBMS',
        'Scalability': 4.0,
        'Cloud managed': 4.5,
        'Transaction support': 4.5,
        'SQL support': 5.0,
        'ACID support': 4.5,
        'Popularity': 5.0,
        'OLTP compliance': 5.0,
        'OLAP compliance': 3.5,
        'Cost': 4.5,
        'Management and Monitoring tool support': 4.5,
        'Ecosystems': 5.0,
        'Communities': 5.0,
        'Documentation and related blogs support': 5.0,
        'Deployment': 4.5
    },
    'MongoDB': {
        'category': 'NoSQL',
        'Scalability': 4.5,
        'Cloud managed': 4.5,
        'Transaction support': 4.0,
        'SQL support': 3.0,
        'ACID support': 4.0,
        'Popularity': 4.5,
        'OLTP compliance': 4.0,
        'OLAP compliance': 3.5,
        'Cost': 4.0,
        'Management and Monitoring tool support': 4.5,
        'Ecosystems': 4.5,
        'Communities': 4.5,
        'Documentation and related blogs support': 4.5,
        'Deployment': 4.5
    },
    'Cassandra': {
        'category': 'NoSQL',
        'Scalability': 5.0,
        'Cloud managed': 4.0,
        'Transaction support': 3.5,
        'SQL support': 3.5,
        'ACID support': 3.5,
        'Popularity': 4.0,
        'OLTP compliance': 4.0,
        'OLAP compliance': 3.0,
        'Cost': 4.0,
        'Management and Monitoring tool support': 4.0,
        'Ecosystems': 4.0,
        'Communities': 4.0,
        'Documentation and related blogs support': 4.0,
        'Deployment': 4.0
    }
}

# Create main window
root = tk.Tk()
root.title("Database Systems Maturity Model")
root.geometry("1400x900")

# Create figure and axis
fig, ax = plt.subplots(figsize=(14, 10))

# Create canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Create dictionaries to store category and subcategory checkboxes state
category_vars = {category: tk.BooleanVar(value=True) for category in categories}
subcategory_vars = {subcategory: tk.BooleanVar(value=True) for subcategory in subcategories}

# Create a dictionary for maturity levels with 0.5 increments
maturity_levels = [f"{i:.1f}" for i in [j/2 for j in range(2, 11)]]  # 1.0 to 5.0 with 0.5 increments
maturity_vars = {level: tk.BooleanVar(value=True) for level in maturity_levels}

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
    ax.set_xlim(min_maturity - 0.25, max_maturity + 0.25)
    xticks = [i/2 for i in range(int(min_maturity*2), int(max_maturity*2)+1)]
    ax.set_xticks(xticks)
    ax.set_xticklabels([f'{i:.1f}' for i in xticks], rotation=45, ha='right')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Group tools by category and subcategory
    grouped_tools = defaultdict(lambda: defaultdict(list))
    for tool, data in tools.items():
        if category_vars[data['category']].get():
            for subcategory in subcategories:
                if subcategory_vars[subcategory].get() and subcategory in data:
                    maturity = data[subcategory]
                    if maturity_vars[f"{maturity:.1f}"].get():
                        grouped_tools[data['category']][subcategory].append((tool, maturity))

    # Set up y-axis
    subcategories_to_plot = [subcat for subcat in subcategories if subcategory_vars[subcat].get()]
    ax.set_ylim(-0.5, len(subcategories_to_plot) * len(categories) - 0.5)
    ax.set_yticks(range(0, len(subcategories_to_plot) * len(categories), len(categories)))
    ax.set_yticklabels(subcategories_to_plot)

    # Plot tools
    for subcat_index, subcategory in enumerate(subcategories_to_plot):
        for cat_index, category in enumerate(categories):
            y = subcat_index * len(categories) + cat_index
            if category in grouped_tools and subcategory in grouped_tools[category]:
                for i, (tool, maturity) in enumerate(grouped_tools[category][subcategory]):
                    x = maturity
                    offset = (i - (len(grouped_tools[category][subcategory]) - 1) / 2) * 0.2
                    ax.plot(x, y, 'ro', markersize=10)
                    ax.annotate(tool, (x, y + offset), xytext=(5, 0), textcoords='offset points', 
                                ha='left', va='center',
                                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'),
                                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                                rotation=45)  # 레이블을 45도 회전

    # Add category labels
    for cat_index, category in enumerate(categories):
        ax.text(-0.5, cat_index - 0.5, category, ha='right', va='center', fontweight='bold')

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
        category_menu.add_checkbutton(label=category, variable=category_vars[category], command=plot_landscape)

    subcategory_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Subcategories", menu=subcategory_menu)
    
    for subcategory in subcategories:
        subcategory_menu.add_checkbutton(label=subcategory, variable=subcategory_vars[subcategory], command=plot_landscape)

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
info_label = ttk.Label(info_frame, text="Use the 'Categories', 'Subcategories', and 'Maturity Levels' menus to filter the display. Use 'Zoom' menu to zoom in or out.", wraplength=1380)
info_label.pack()

# Run the application
root.mainloop()