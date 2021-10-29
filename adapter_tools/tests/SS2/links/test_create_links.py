import pytest
import os
import json

from .input_data import LINKS_INPUT

import adapter_tools.commands.create_links as cl


@pytest.fixture()
def links_input():
    return LINKS_INPUT


# Create project links file
# SS2 creates a single links json which merges all of the intermediate runs with the project level run
# For testing purposed we are only using a single sample
def test_create_links_file(links_input):
    links_file = cl.test_build_links_file_SS2(links_input)

    expected_output_path = os.path.join(
        os.path.dirname(__file__), "links_expected.json"
    )

    with open(expected_output_path) as f:
        expected_output = json.load(f)

    assert expected_output == links_file
