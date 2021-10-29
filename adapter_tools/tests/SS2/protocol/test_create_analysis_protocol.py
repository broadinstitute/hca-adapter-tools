import pytest
import os
import json

from .input_data import ANALYSIS_PROTOCOL_INPUT

import adapter_tools.commands.create_analysis_protocol as cap


@pytest.fixture()
def analysis_protocol_input():
    return ANALYSIS_PROTOCOL_INPUT


# Create intermediate analysis protocol file
def test_create_analysis_protocol(analysis_protocol_input):
    analysis_protocol_file = cap.test_build_analysis_protocol(analysis_protocol_input)

    expected_output_path = os.path.join(
        os.path.dirname(__file__), "analysis_protocol_expected.json"
    )

    with open(expected_output_path) as f:
        expected_output = json.load(f)

    assert expected_output == analysis_protocol_file
