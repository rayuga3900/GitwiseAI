def test_loader_returns_list(loader):
    files = loader.data_loading()
    assert isinstance(files, list)

def test_loader_file_keys(loader):
    files = loader.data_loading()
    if files:
        keys = files[0].keys()
        assert "repo" in keys
        assert "path" in keys
        assert "content" in keys
        assert "language" in keys