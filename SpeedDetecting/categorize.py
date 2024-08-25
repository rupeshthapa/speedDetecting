def categorize_movements(labels, boxes, indexes):
    categorized_movements = {"human": [], "bike": [], "vehicle": []}
    
    if len(indexes) > 0:
        for i in indexes.flatten():
            label = labels[i]
            box = boxes[i]

            if label in ["person"]:
                categorized_movements["human"].append(box)
            elif label in ["bicycle", "motorbike"]:
                categorized_movements["bike"].append(box)
            elif label in ["car", "bus", "truck"]:
                categorized_movements["vehicle"].append(box)
                
    return categorized_movements