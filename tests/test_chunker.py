def test_chunker_returns_list(chunker, loader):
    files = loader.data_loading()
    chunks = chunker.chunk_content(files)
    assert isinstance(chunks, list)
    if chunks:
        assert "content" in chunks[0]
        assert "metadata" in chunks[0]

def test_chunk_metadata(chunker, loader):
    files = loader.data_loading()
    chunks = chunker.chunk_content(files)
    if chunks:
        meta = chunks[0]["metadata"]
        assert "file_name" in meta
        assert "file_type" in meta