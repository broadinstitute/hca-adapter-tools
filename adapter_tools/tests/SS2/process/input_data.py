import os

cromwell_metadata_path = os.path.join(
    os.path.dirname(__file__), "cromwell_metadata.json"
)

ANALYSIS_PROCESS_INPUT = {
    "input_uuid": "0244354d-cf37-4483-8db3-425b7e504ca6",
    "pipeline_type": "SS2",
    "workspace_version": "2021-10-19T17:43:52.000000Z",
    "references": [
        "gs://gcp-public-data--broad-references/hg38/v0/GRCh38.primary_assembly.genome.fa"
    ],
    "input_file": cromwell_metadata_path,
    "project_level": False,
    "ss2_index": 0,
}
