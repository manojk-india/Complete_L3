</think>

import pandas as pd
df = pd.read_csv("generated_files/new_custom.csv")
filtered_df = df[(df['assignee'] == 'Hari') & (df['sprint'] == 8)]
filtered_df.to_csv('generated_files/output.csv', index=False)
