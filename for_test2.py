from src.milkdown.service.vertor.base import vector_store

a = vector_store.embed_model.get_text_embedding("participate in")
b = vector_store.embed_model.get_text_embedding("at")


import numpy as np
vec1 = np.array(a)
vec2 = np.array(b)

cos_sim = vec1.dot(vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
print(cos_sim)

