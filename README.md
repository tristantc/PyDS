# PyDS

**PyDS** (Python DataSheet) class provides a way to parse SVG files containing line plots and extract path data, transforming it into coordinates. 
It is mainly used for tracing the datasheet curves and converting them in ready-to-use data arrays

---

## 🚀 Features

- Load and parse SVG file containing datasheet curves
- Identify and extract plot paths (supports multi-segment paths)
- Scale and transform coordinates to match plot dimensions
- **Per-path y-axis configuration** for multi-scale plots (dual y-axis support)
- **Multi-rectangle support** for paths with different coordinate systems
- Visualize individual or all plots
- Export coordinate values to dictionaries

---

## 📦 Installation

PyDS relies on the following Python libraries:

- `svgpathtools` - not available in default python installation. Use pip install svgpathtools
- `numpy` - available in default python installation
- `matplotlib` - available in default python installation
- `xml` - available in default python installation

Install the required packages:

```bash
pip install svgpathtools
```
---
## 🧰 Usage

### Initialization

```python
from pyds import PyDS
svg_plot = PyDS(filename="graph.svg", Npoints=100, x=100, y=0, width=100, height=80)
```
-`filename` - default positional argument (should always be used)
-`NPoints` - default positional argument (should always be used)
-`x` - start x position of the grid box. Keyword argument (can be omitted)
-`y` - start y position of the grid box. Keyword argument (can be omitted)
-`width` - width of the grid box. Keyword argument (can be omitted)
-`height` - height of the grid box. Keyword argument (can be omitted)
-`path_params` - dictionary for per-path y-axis configuration. Keyword argument (can be omitted)
-`rect_params` - dictionary for multi-rectangle coordinate systems. Keyword argument (can be omitted)

### Advanced: Per-Path Y-Axis Configuration

For SVG files with multiple curves on different scales (e.g., dual y-axis plots), use `path_params` to configure each path independently:

```python
svg_plot = PyDS(
    "multi_scale_plot.svg", 
    Npoints=100,
    x=1,
    width=1,
    path_params={
        0: {'y': 450, 'height': 90},   # Path 0: custom y-start and height
        1: {'y': 0.5, 'height': 0.1}   # Path 1: different scale
    }
)
```

This is particularly useful when creating dual y-axis plots with matplotlib:

```python
import matplotlib.pyplot as plt

fig, ax1 = plt.subplots()

# Plot first path on primary y-axis
ax1.plot(svg_plot.line['x'][0], svg_plot.line['y'][0], 'o-', label='Head')
ax1.set_ylabel('Head [m]', color='tab:blue')

# Create secondary y-axis for second path
ax2 = ax1.twinx()
ax2.plot(svg_plot.line['x'][1], svg_plot.line['y'][1], 's-', label='Efficiency', color='tab:orange')
ax2.set_ylabel('Efficiency', color='tab:orange')

plt.show()
```

### Advanced: Multi-Rectangle Coordinate Systems

For SVG files with multiple reference rectangles (grids) with different coordinate systems, use `rect_params` to define each rectangle and link paths to them:

```python
svg_plot = PyDS(
    "multi_grid_plot.svg",
    Npoints=100,
    rect_params={
        'rect_primary': {'x': 0, 'y': 0, 'width': 100, 'height': 200},
        'rect_secondary': {'x': 0, 'y': 0, 'width': 50, 'height': 100}
    },
    path_params={
        0: {'rect_id': 'rect_primary', 'y': 0, 'height': 200},
        1: {'rect_id': 'rect_secondary', 'y': 0, 'height': 100},
        2: {'rect_id': 'rect_primary', 'y': 50, 'height': 150}
    }
)
```

**Use cases:**
- SVG files with separate sub-plots
- Charts with inset graphs at different scales
- Multi-panel datasheets with independent coordinate systems

Each path is transformed using its assigned rectangle's coordinate system, allowing accurate extraction from complex multi-grid layouts.


### Plot All Paths

```python
svg_plot.plot_all(labels=["Line A", "Line B"])
```

### Access Path Values

Returns extracted coordinate values as a dictionary with 'x' and 'y' keys:

```python
data = svg_plot.values(0)  # Get data from path 0
print(data['x'], data['y'])
```

### Export to CSV or DataFrame

The extracted data can be easily exported to various formats:

```python
import pandas as pd

# Extract data from a path
path0_data = svg_plot.values(0)

# Create DataFrame
df = pd.DataFrame({
    'x': path0_data['x'],
    'y': path0_data['y']
})

# Export to CSV
df.to_csv('output/extracted_data.csv', index=False)
```

---

## 📊 Advanced Features

### Multi-Segment Path Support

PyDS automatically handles complex SVG paths with multiple segments. The tool concatenates all segments and samples points proportionally across the entire path, ensuring accurate representation of complex curves.

### Direct Access to Line Data

For advanced use cases, you can access the raw line data directly:

```python
# Access x-coordinates for all paths
all_x = svg_plot.line['x']

# Access y-coordinates for path 0
path0_y = svg_plot.line['y'][0]
```

---
## 🔗 Dependencies
-`svgpathtools`
-`matplotlib`
-`numpy`
-`xml.etree.ElementTree`

## 📝 License
MIT License. See LICENSE file for details.
## ✍️ Author
Developed by Dr. Anatolii Tcai
