from sentence_transformers import SentenceTransformer
_model = None

def load_model(name="sentence-transformers/bert-base-nli-mean-tokens"):
    global _model
    if _model is None:
        _model = SentenceTransformer(name)

    return _model

def embed_texts(text_list):
    model = load_model()
    return model.encode(text_list, show_progress_bar=False, convert_to_numpy=True)

# test run
error = embed_texts(["ERROR: Tests failed: AssertionError at test_utils.py:42"])
print(error.shape)