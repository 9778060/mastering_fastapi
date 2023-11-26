import contextlib
import os
import pathlib
import tempfile

import pytest
from httpx import AsyncClient
from fastapi import status

from ...main import prefix_files


@pytest.fixture
def sample_image(fs) -> pathlib.Path:
    path = (pathlib.Path(__file__).parent / "assets" / "myfile.png").resolve()
    fs.create_file(path)
    return path


@pytest.fixture(autouse=True)
def mock_b2_upload_file(mocker):
    return mocker.patch("socialapi.routers.files.b2_upload_file", return_value="https://fakeurl.com")


@pytest.fixture(autouse=True)
def aiofiles_mock_open(mocker, fs):
    import io

    mock_open = mocker.patch("aiofiles.open")

    @contextlib.asynccontextmanager
    async def async_file_open(fname: str, mode: str = "r"):
        out_fs_mock = mocker.AsyncMock(name=f"async_file_open:{fname!r}/{mode!r}")
        with io.open(fname, mode) as fin:
            out_fs_mock.read.side_effect = fin.read
            yield out_fs_mock

    mock_open.side_effect = async_file_open
    
    return mock_open


async def call_upload_endpoint(async_client: AsyncClient, token: str, sample_image: pathlib.Path):
    return await async_client.post(
        prefix_files + "/upload",
        files={"file": open(sample_image, "rb")},
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.mark.anyio
async def test_upload_image(async_client: AsyncClient, logged_in_token: str, sample_image: pathlib.Path):
    response = await call_upload_endpoint(async_client, logged_in_token, sample_image)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["file_url"] == "https://fakeurl.com"


@pytest.mark.anyio
async def test_temp_file_removed_after_upload(async_client: AsyncClient, logged_in_token: str, sample_image: pathlib.Path, mocker):
    # Spy on the NamedTemporaryFile function
    named_temp_file_spy = mocker.spy(tempfile, "NamedTemporaryFile")

    response = await call_upload_endpoint(async_client, logged_in_token, sample_image)
    assert response.status_code == status.HTTP_201_CREATED

    # Get the filename of the temporary file created by the upload endpoint
    created_temp_file = named_temp_file_spy.spy_return

    # Check if the temp_file is removed after the file is uploaded
    assert not os.path.exists(created_temp_file.name)
