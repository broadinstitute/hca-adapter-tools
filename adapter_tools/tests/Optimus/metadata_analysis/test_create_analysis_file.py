import pytest
import os
import json

from .input_data import ANALYSIS_FILE_INPUT

import adapter_tools.commands.create_analysis_file as caf


@pytest.fixture()
def analysis_file_input():
    return ANALYSIS_FILE_INPUT


# Create metadata outputs.json
# Outputs.json respresents the merged list of the loom and bam analysis metadata files
def test_analysis_file(analysis_file_input):
    analysis_outputs = caf.test_build_analysis_file_optimus(analysis_file_input)

    expected_output_path = os.path.join(
        os.path.dirname(__file__), "analysis_outputs_expected.json"
    )

    with open(expected_output_path) as f:
        expected_output = json.load(f)

    assert expected_output == analysis_outputs
