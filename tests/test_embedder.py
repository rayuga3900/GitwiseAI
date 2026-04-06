def test_embedder_output_shape(fake_embedder):
    texts = ["sample text 1", "sample text 2"]
    embeddings = fake_embedder.embed_chunks(texts)
    assert isinstance(embeddings, list)
    assert all(isinstance(vec, list) for vec in embeddings)
    assert len(embeddings) == len(texts)
    assert all(len(vec) == 384 for vec in embeddings)  # matches mocked embedding dim