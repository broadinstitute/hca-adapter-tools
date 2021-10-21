import pytest
import os
import json

from .input_data import LINKS_INPUT

import adapter_tools.commands.create_links as cl


@pytest.fixture()
def links_input():
    return LINKS_INPUT


# Create intermediate links file
# Optimus intermediate links require outputs.json, analysis process and analysis protocol files
def test_create_links_file(links_input):
    links_file = cl.test_build_links_file_optimus(links_input)

    expected_output_path = os.path.join(
        os.path.dirname(__file__), "links_expected.json"
    )

    with open(expected_output_path) as f:
        expected_output = json.load(f)

    assert expected_output == links_file
