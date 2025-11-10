class PyDS:
    def __init__(self, filename: str, Npoints: int, **kwargs):
        import numpy as np
        
        # Load defaults and override with user-provided kwargs
        self.defaults(**kwargs)
        kwargs = {**self.defKwargs, **kwargs}
        self.points = np.linspace(0, 1, Npoints)
        
        # Load the SVG file and process contents
        self.load(filename)
        self.find_rect() # Find the reference rectangle
        self.find_plots() # Find the plot paths
    
    def load(self, filename):
        # Load paths and attributes from SVG
        self.paths, self.attributes = self.svg(filename)
    
    def find_plots(self):
        # Identify all 'path' type elements in the SVG
        for i, attr in enumerate(self.attributes):
            if attr['id'][:4].lower() == 'path':
                self.path_i.append(i)
        
        # Convert SVG path coordinates to plot coordinates
        for path_idx, i in enumerate(self.path_i):
            # Get per-path parameters (y_start and height) or use defaults
            if path_idx in self.path_params:
                path_y_start = self.path_params[path_idx].get('y', self.y_start)
                path_height = self.path_params[path_idx].get('height', self.or_height)
            else:
                path_y_start = self.y_start
                path_height = self.or_height
            
            # Calculate per-path scaling factor for y-axis
            path_ky = path_height / self.h_box
            path_y_origin = self.paths[self.rect_i][1].point(0).imag + path_y_start / path_ky
            
            # Handle multi-segment paths by concatenating all segments
            path_obj = self.paths[i]
            
            # Calculate total length of all segments
            total_length = sum(seg.length() for seg in path_obj)
            
            # Sample points proportionally across all segments
            x_coords = []
            y_coords = []
            
            for t in self.points:
                # Find which segment this t value corresponds to
                target_length = t * total_length
                cumulative_length = 0
                
                for seg in path_obj:
                    seg_length = seg.length()
                    if cumulative_length + seg_length >= target_length:
                        # This segment contains our point
                        local_t = (target_length - cumulative_length) / seg_length if seg_length > 0 else 0
                        local_t = max(0, min(1, local_t))  # Clamp to [0, 1]
                        point = seg.point(local_t)
                        
                        # Apply per-path coordinate transformation
                        x_coords.append(self.kx * (point.real - self.x_origin))
                        y_coords.append(path_ky * (self.h_box - point.imag + path_y_origin))
                        break
                    cumulative_length += seg_length
            
            self.line['x'].append(x_coords)
            self.line['y'].append(y_coords)
        
    def plot(self, N, **kwargs):
        import matplotlib.pyplot as plt
        if 'label' in kwargs:
            plt.plot(self.line['x'][N], self.line['y'][N], label=kwargs['label'], marker='o')
        else:
            plt.plot(self.line['x'][N], self.line['y'][N])
    
    def plot_all(self, **kwargs):
        import matplotlib.pyplot as plt
        if 'labels' in kwargs:
            labels = kwargs['labels']
        else:
            labels = [f'Plot {i}' for i in self.path_i]
        
        for i, label in zip(self.path_i, labels):
            self.plot(i, label=label)
            plt.legend()
        
    def find_rect(self):
        # Find the bounding box (usually the background rectangle) from SVG
        for i, attr in enumerate(self.attributes):
            if attr['id'][:4].lower() == 'rect':
                self.rect_i = i
        
        # Extract bounding box real/im coordinates
        self.w_box = self.paths[self.rect_i][0].point(1).real - self.paths[self.rect_i][0].point(0).real
        self.h_box = self.paths[self.rect_i][1].point(1).imag - self.paths[self.rect_i][1].point(0).imag
        
        # Scaling factors from SVG units to plotting units
        self.kx = self.or_width / self.w_box
        self.ky = self.or_height / self.h_box
        
        # Origins for transforming coordinate system
        self.x_origin = self.paths[self.rect_i][0].point(0).real - self.x_start / self.kx
        self.y_origin = self.paths[self.rect_i][1].point(0).imag + self.y_start / self.ky
        
        # For completeness
        self.x_box = self.x_origin
        self.y_box = self.h_box
    
    def defaults(self, **kwargs):
        # Load libraries
        from svgpathtools import svg2paths, wsvg
        import xml.etree.ElementTree as ET
        
        self.ET = ET
        self.svg = svg2paths
        self.wsvg = wsvg
        
        # Default plotting parameters
        self.defKwargs = {    'width': 50,    'height': 50,    'Nplots': 1,    'x': 0,    'y': 0,    'path_params': None    }
        
        # Combine defaults with user kwargs
        kwargs = {**self.defKwargs, **kwargs}
        
        # Set base dimensions and starting points
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.x_start = kwargs['x']
        self.y_start = kwargs['y']
        
        # Per-path parameters: dict with path indices as keys, {'y': y_start, 'height': height} as values
        # Example: path_params={0: {'y': 450, 'height': 90}, 1: {'y': 50, 'height': 10}}
        self.path_params = kwargs['path_params'] if kwargs['path_params'] is not None else {}
        
        # Internal state
        self.rect_i = None
        self.path_i = []
        self.line = {'x': [], 'y': []}
    
    def values(self, i: int) -> dict:
        # Return a dictionary of x/y values for a single path
        size = len(self.line['x'][i])
        x = [float(self.line['x'][i][j]) for j in range(size)]
        y = [float(self.line['y'][i][j]) for j in range(size)]
        return {'x': x, 'y': y}
    
    @property
    def width(self):
        print(f"Width of the graph is {self.or_width}")
        return self.or_width
    
    @width.setter
    def width(self, value):
        self.or_width = value
    
    @property
    def height(self):
        print(f"Height of the graph is {self.or_height}")
        return self.or_height
    
    @height.setter
    def height(self, value):
        self.or_height = value
