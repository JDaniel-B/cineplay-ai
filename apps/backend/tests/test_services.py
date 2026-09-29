from app.services.llm import allocate_usage, count_unicode_words


def test_unicode_word_count() -> None:
    assert count_unicode_words("Película: acción, emoción y déjà-vu.") == 6


def test_dual_category_allocation_is_reproducible() -> None:
    sources = {"peliculas": [{"titulo": "Uno"}], "videojuegos": [{"titulo": "Dos"}]}
    allocation = allocate_usage(101, sources)
    assert sum(allocation.values()) == 101
    assert allocation == allocate_usage(101, sources)
