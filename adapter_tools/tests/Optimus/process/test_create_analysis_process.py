import pytest
import os
import json

from .input_data import ANALYSIS_PROCESS_INPUT

import adapter_tools.commands.create_analysis_process as cap


@pytest.fixture()
def analysis_process_input():
    return ANALYSIS_PROCESS_INPUT


# Creat intermediate analysis process file
def test_create_analysis_process(analysis_process_input):
    analysis_process_file = cap.test_build_analysis_process_optimus(
        analysis_process_input
    )

    expected_output_path = os.path.join(
        os.path.dirname(__file__), "analysis_process_expected.json"
    )

    with open(expected_output_path) as f:
        expected_output = json.load(f)

    assert expected_output == analysis_process_file
