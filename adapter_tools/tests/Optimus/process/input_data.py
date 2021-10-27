import os

cromwell_metadata_path = os.path.join(
    os.path.dirname(__file__), "cromwell_metadata.json"
)

ANALYSIS_PROCESS_INPUT = {
    "input_uuid": "6f911b71-158e-4f50-b8e5-395f386a343b",
    "pipeline_type": "Optimus",
    "workspace_version": "2021-05-24T12:00:00.000000Z",
    "references": [
        "gs://hca-dcp-sc-pipelines-test-data/alignmentReferences/optimusGencodeV27/GRCh38.primary_assembly.genome.fa"
    ],
    "input_file": cromwell_metadata_path,
    "project_level": False,
}
