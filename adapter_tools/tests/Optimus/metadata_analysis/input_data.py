import os

cromwell_metadata_path = expected_output_path = os.path.join(
    os.path.dirname(__file__), "cromwell_metadata.json"
)

# Optimus adapter creates both analysis_metadata files via the cromwell metadata
ANALYSIS_FILE_INPUT = {
    "input_uuid": "6f911b71-158e-4f50-b8e5-395f386a343b",
    "pipeline_type": "Optimus",
    "workspace_version": "2021-05-24T12:00:00.000000Z",
    "input_file": cromwell_metadata_path,
    "project_level": False,
}
