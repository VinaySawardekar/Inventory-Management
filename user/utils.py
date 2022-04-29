def predict(index):
    if index == 1 or index == 8:
        cat = 'Electronic accessories'
    elif index == 2 or index == 7:
        cat = 'Fashion accessories'
    elif index == 3 or index == 9:
        cat = 'Food and beverages'
    elif index == 4 or index == 10:
        cat = 'Health and beauty'
    elif index == 5 or index == 12:
        cat = 'Home and lifestyle'
    elif index == 6 or index == 11:
        cat = 'Sports and travel'
    return cat


def PredicT(max_index):
    if max_index == 1:
        prod_name = 'Beverages'
    elif max_index == 2:
        prod_name = 'Chocolates'
    elif max_index == 3:
        prod_name = 'Herbal Colors'
    elif max_index == 4:
        prod_name = 'Cosmetics'
    elif max_index == 5:
        prod_name = 'AC'
    elif max_index == 6:
        prod_name = 'Fridge'
    elif max_index == 7:
        prod_name = 'HouseHold Products'
    elif max_index == 8:
        prod_name = 'Sweets'
    elif max_index == 9:
        prod_name = 'Sweets'
    elif max_index == 10:
        prod_name = 'Clothes'
    elif max_index == 11:
        prod_name = 'Decor'
    elif max_index == 12 :
        prod_name = 'Electronics'
    return prod_name