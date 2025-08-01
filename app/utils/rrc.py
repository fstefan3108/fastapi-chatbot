def reciprocal_rank_fusion(list1, list2, k=60):
    from collections import defaultdict
    fused_scores = defaultdict(float)

    for rank, chunk in enumerate(list1):
        fused_scores[chunk] += 1 / (rank + k)
    for rank, chunk in enumerate(list2):
        fused_scores[chunk] += 1 / (rank + k)

    # Sort by combined score descending
    sorted_chunks = sorted(fused_scores.items(), key=lambda x: -x[1])

    # Return just the chunks (text), ranked
    return [chunk for chunk, score in sorted_chunks]

# defaultdict() - same as regular dict, but has a default value (float in this case) #