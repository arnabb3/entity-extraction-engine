import pandas as pd
import re

def optimize_entity_stats(df, text_col, rating_col, entities):
    import re

    # Ensure text_col and rating_col exist
    if text_col not in df.columns or rating_col not in df.columns:
        return pd.DataFrame(columns=["Entity", "Mentions", "Average Rating"])

    # Pre-compile regex patterns once
    patterns = {e: re.compile(rf"\b{re.escape(e)}\b", flags=re.IGNORECASE) for e in entities}

    # Initialize counters
    entity_stats = {e: {'Mentions': 0, 'Total Rating': 0.0, 'Count': 0} for e in entities}

    for _, row in df.iterrows():
        text = str(row[text_col])
        rating = row[rating_col] if pd.notnull(row[rating_col]) else None
        for entity, pattern in patterns.items():
            if pattern.search(text):
                entity_stats[entity]['Mentions'] += 1
                if rating is not None:
                    entity_stats[entity]['Total Rating'] += rating
                    entity_stats[entity]['Count'] += 1

    # Format into DataFrame
    results = []
    for entity, stats in entity_stats.items():
        avg_rating = (stats['Total Rating'] / stats['Count']) if stats['Count'] > 0 else None
        results.append({
            'Entity': entity,
            'Mentions': stats['Mentions'],
            'Average Rating': round(avg_rating, 2) if avg_rating is not None else None
        })

    return pd.DataFrame(results)

