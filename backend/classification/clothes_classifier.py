
class ClothesClassifier:
    UPPER_BODY_KEYWORDS = ['shirt', 'blouse', 'top', 'jacket', 'coat', 'sweater']
    LOWER_BODY_KEYWORDS = ['pants', 'trousers', 'shorts', 'jeans', 'skirt']
    DRESS_KEYWORDS = ['dress', 'playsuit']

    def classify_item(self, item_name):
        item_name_lower = item_name.lower()

        if any(keyword in item_name_lower for keyword in ClothesClassifier.UPPER_BODY_KEYWORDS):
            return 'Upper-body'
        elif any(keyword in item_name_lower for keyword in ClothesClassifier.LOWER_BODY_KEYWORDS):
            return 'Lower-body'
        elif any(keyword in item_name_lower for keyword in ClothesClassifier.DRESS_KEYWORDS):
            return 'Dress'
        else:
            return 'Unknown'


if __name__ == '__main__':
    # Example usage
    item_name = "COTTON AND MODAL CROP TOP"
    ClothesClassifier = ClothesClassifier()
    category = ClothesClassifier.classify_item(item_name)
    print(f"Item '{item_name}' is classified as: {category}")
