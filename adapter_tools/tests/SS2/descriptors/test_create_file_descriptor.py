import pytest
import os
import json

from .input_data import BAI_INPUT, BAM_INPUT

import adapter_tools.commands.create_file_descriptor as cfd


@pytest.fixture()
def bai_input_data():
    return BAI_INPUT


@pytest.fixture()
def bam_input_data():
    return BAM_INPUT


# Create intermediate loom descriptor file
def test_bai_intermediate(bai_input_data):
    bai_file_descriptor = cfd.test_build_file_descriptor(bai_input_data)

    expected_output_path = os.path.join(
        os.path.dirname(__file__), "descriptor_bai_expected.json"
    )

    with open(expected_output_path) as f:
        expected_output = json.load(f)

    assert expected_output == bai_file_descriptor


# Create intermediate bam descriptor file
def test_bam_intermediate(bam_input_data):
    bam_file_descriptor = cfd.test_build_file_descriptor(bam_input_data)

    expected_output_path = os.path.join(
        os.path.dirname(__file__), "descriptor_bam_expected.json"
    )

    with open(expected_output_path) as f:
        expected_output = json.load(f)

    assert expected_output == bam_file_descriptor
