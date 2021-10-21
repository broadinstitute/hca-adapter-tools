import pytest
import os
import json

from .input_data import LOOM_INPUT, BAM_INPUT

import adapter_tools.commands.create_file_descriptor as cfd


@pytest.fixture()
def loom_input_data():
    return LOOM_INPUT


@pytest.fixture()
def bam_input_data():
    return BAM_INPUT


# Create intermediate loom descriptor file
def test_loom_intermediate(loom_input_data):
    loom_file_descriptor = cfd.test_build_file_descriptor(loom_input_data)

    expected_output_path = os.path.join(
        os.path.dirname(__file__), "descriptor_loom_expected.json"
    )

    with open(expected_output_path) as f:
        expected_output = json.load(f)

    assert expected_output == loom_file_descriptor


# Create intermediate bam descriptor file
def test_bam_intermediate(bam_input_data):
    bam_file_descriptor = cfd.test_build_file_descriptor(bam_input_data)

    expected_output_path = os.path.join(
        os.path.dirname(__file__), "descriptor_bam_expected.json"
    )

    with open(expected_output_path) as f:
        expected_output = json.load(f)

    assert expected_output == bam_file_descriptor
