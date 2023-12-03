import pytest


@pytest.fixture()
def mock_generate_cute_creature_api(mocker):
    return mocker.patch(
        "socialapi.tasks._generate_cute_creature_api",
        return_value={"output_url": "http://example.net/image.jpg"},
    )
