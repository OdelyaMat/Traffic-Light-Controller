from matplotlib import pyplot as plt

class Visualizer:
    def __init__(self):
        # 's' = Photo size. 'm' = Margin from center cluster.
        s = 0.22  
        m = 0.08  
        
        self.img_rects = {
        0: [0.5 - s/2, 0.5 + m,   s, s], # North
        1: [0.5 + m,   0.5 - s/2, s, s], # East
        2: [0.5 - s/2, 0.5 - m - s, s, s], # South
        3: [0.5 - m - s, 0.5 - s/2, s, s]  # West
    }
    
        self.labels = ["North", "East", "South", "West"]
        
        plt.ion()
        self.fig = plt.figure(figsize=(10, 10))
        self.fig.patch.set_facecolor('#121212')

    def display(self, images, cars_in_intersection: list[int], cars_remaining: list[int], green_light_idx: int, detections=None):
        if not plt.fignum_exists(self.fig.number):
            return

        self.fig.clf() 
        
        for i in range(len(cars_in_intersection)):
            at_light_count = cars_in_intersection[i]
            reservoir_count = cars_remaining[i]
            
            rect = self.img_rects[i]
            ax = self.fig.add_axes(rect)
            
            img = images[i]
            if img is not None:
                ax.imshow(img, aspect='equal')
                # Draw bounding boxes if detections are provided
                if detections is not None and i < len(detections):
                    det = detections[i]
                    boxes = det.get('boxes', [])
                    for j, box in enumerate(boxes):
                        x1, y1, x2, y2 = box
                        width = x2 - x1
                        height = y2 - y1
                        # Draw rectangle
                        rect_patch = plt.Rectangle((x1, y1), width, height, linewidth=2, edgecolor='yellow', facecolor='none', zorder=20)
                        ax.add_patch(rect_patch)

            
            # Traffic Light
            light_color = 'lime' if green_light_idx == i else 'red'
            circle = plt.Circle((0.1, 0.9), 0.07, color=light_color, 
                                transform=ax.transAxes, zorder=10)
            ax.add_patch(circle)
            
            ax.set_title(f"{self.labels[i]}\nRes: {reservoir_count}", 
                         color='white', fontsize=10, weight='bold', pad=8)
            ax.axis('off')

            dots_to_draw = min(at_light_count, 144)
            if dots_to_draw > 0:
                l, b, w, h = rect
                q_width = 0.07 
                gap = 0.005

                # North (0) and West (3) -> Place queue on the left
                # East (1) and South (2) -> Place queue on the right
                if i in [0, 3]: 
                    d_rect = [l - q_width - gap, b, q_width, h]
                else:           
                    d_rect = [l + w + gap, b, q_width, h]
                
                dot_ax = self.fig.add_axes(d_rect)
                
                grid_dim = 12
                x_dots = [d // grid_dim for d in range(dots_to_draw)]
                y_dots = [d % grid_dim for d in range(dots_to_draw)]
                
                # If on the left side (N or W), reverse X so they stack "outwards" to the left
                if i in [0, 3]: 
                    x_dots = [grid_dim - x for x in x_dots]

                dot_ax.scatter(x_dots, y_dots, c='orange', s=8, 
                               edgecolors='black', linewidth=0.2)
                
                dot_ax.set_xlim(-1, grid_dim + 1)
                dot_ax.set_ylim(-1, grid_dim + 1)
                dot_ax.axis('off')

        plt.draw()
        plt.pause(0.1)