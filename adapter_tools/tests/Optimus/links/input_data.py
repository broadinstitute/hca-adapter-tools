import os

analysis_process_path = os.path.join(
    os.path.dirname(__file__),
    "analysis_process/14438140-4f0f-4dd8-b9c4-00212f112a99_2021-05-24T12:00:00.000000Z.json",
)

analysis_protocol_path = os.path.join(
    os.path.dirname(__file__),
    "analysis_protocol/61223a2e-a775-53f4-8aab-fc3b4ef88722_2021-05-24T12:00:00.000000Z.json",
)

outputs_path = os.path.join(os.path.dirname(__file__), "outputs.json")

# Input UUIDS are the fastq uuids for the intermediate run
# Optimus can have multiple fastq1 and fastq1 per run
LINKS_INPUT = {
    "project_id": "9d97f01f-9313-416e-9b07-560f048b2350",
    "workspace_version": "2021-05-24T12:00:00.000000Z",
    "input_uuids": [
        "0af14740-753f-42e4-a025-e02c438b8591",
        "0132474c-2452-4c80-9334-d95b999864ad",
        "9dd8ad36-5570-4109-ac92-04363aafafe5",
        "3f1313f0-fe17-4063-9955-56ead2cb7de0",
    ],
    "output_file_path": outputs_path,
    "analysis_process_path": analysis_process_path,
    "analysis_protocol_path": analysis_protocol_path,
    "file_name_string": "6f911b71-158e-4f50-b8e5-395f386a343b",
    "pipeline_type": "Optimus",
    "project_level": False,
}
