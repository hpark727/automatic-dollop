from insider_data import InsiderData
from formatter import format_scores_to_dict
test = InsiderData()
new = test.get_data().clean_values().compute_score()
print(new.clean_data)




