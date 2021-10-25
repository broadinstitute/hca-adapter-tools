import os


analysis_process_path = os.path.join(
    os.path.dirname(__file__),
    "analysis_process/f4a596eb-0f35-4cd4-b4e6-64324537c448_2021-10-19T17:43:52.000000Z.json",
)

analysis_protocol_path = os.path.join(
    os.path.dirname(__file__),
    "analysis_protocol/e1914217-708b-5bdf-907f-97235dc8fd9e_2021-10-19T17:43:52.000000Z.json",
)

analysis_process_list_path = os.path.join(
    os.path.dirname(__file__), "analysis_process/analysis_process_list.json"
)

analysis_protocol_list_path = os.path.join(
    os.path.dirname(__file__), "analysis_protocol/analysis_protocol_list.json"
)

input_uuids_path = os.path.join(os.path.dirname(__file__), "input_lists/uuid_list.json")

bai_path = os.path.join(os.path.dirname(__file__), "input_lists/bai_list.json")

bam_path = os.path.join(os.path.dirname(__file__), "input_lists/bam_list.json")

fastq1_path = os.path.join(os.path.dirname(__file__), "input_lists/fastq1_list.json")

fastq2_path = os.path.join(os.path.dirname(__file__), "input_lists/fastq2_list.json")

outputs_path = os.path.join(os.path.dirname(__file__), "outputs.json")


LINKS_INPUT = {
    "project_id": "0c3b7785-f74d-4091-8616-a68757e4c2a8",
    "workspace_version": "2021-10-19T17:43:52.000000Z",
    "output_file_path": outputs_path,
    "analysis_process_path": analysis_process_path,
    "analysis_protocol_path": analysis_protocol_path,
    "input_uuids_path": input_uuids_path,
    "input_uuids": [],
    "analysis_process_list_path": analysis_process_list_path,
    "analysis_protocol_list_path": analysis_protocol_list_path,
    "ss2_bam": bam_path,
    "ss2_bai": bai_path,
    "ss2_fastq1": fastq1_path,
    "ss2_fastq2": fastq2_path,
    "file_name_string": "project=0c3b7785-f74d-4091-8616-a68757e4c2a8;library=Smart-seq2;species=Homo sapiens;organ=hematopoietic system",
    "pipeline_type": "SS2",
    "project_level": True,
}
