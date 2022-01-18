#!/usr/bin/env python

import argparse
import loompy
import numpy as np
from scipy import sparse


class MergeLooms:
    def __init__(
        self,
        input_loom_files,
        library,
        species,
        organ,
        project_id,
        project_name,
        min_UMIs, 
        output_loom_file,
    ):

        self.input_loom_files = input_loom_files
        self.library = ", ".join(set(library))
        self.species = ", ".join(set(species))
        self.organ = ", ".join(set(organ))
        self.project_id = project_id
        self.project_name = project_name
        self.output_loom_file = output_loom_file

        expression_data_type_list = []
        optimus_output_schema_version_list = []
        pipeline_versions_list = []
        input_id_metadata_field_list = []
        input_name_metadata_field_list = []
        input_id_list = []
        input_name_list = []


        data = np.array([])
        col = np.array([])
        row = np.array([])

        row_attrs = {}
        col_attrs = {}
        n_rows = 0
        n_cols = 0
        for i in range(len(self.input_loom_files)):
            loom_file = self.input_loom_files[i]
            print("processing  loom  file", loom_file)
            with loompy.connect(loom_file) as ds:
                # add global attributes for this file to the running list of global attributes
                expression_data_type_list.append(ds.attrs["expression_data_type"])
                optimus_output_schema_version_list.append(
                    ds.attrs["optimus_output_schema_version"]
                )
                pipeline_versions_list.append(ds.attrs["pipeline_version"])
                input_id_metadata_field_list.append(
                    ds.attrs["input_id_metadata_field"]
                )
                input_name_metadata_field_list.append(
                    ds.attrs["input_name_metadata_field"]
                )
                input_id_list.append(ds.attrs["input_id"])
                input_name_list.append(ds.attrs["input_name"])

                for row_attrib in ds.ra.keys():
                    if row_attrib in ['Gene', 'ensembl_ids', 'gene_names']:
                        row_attrs[row_attrib] = ds.ra[row_attrib]
                    else:
                        if row_attrib not in row_attrs:
                            row_attrs[row_attrib] = ds.ra[row_attrib].reshape(ds.ra[row_attrib].shape[0], -1)
                        else:
                            row_attrs[row_attrib] = np.concatenate((ds.ra[row_attrib].reshape(ds.ra[row_attrib].shape[0], -1), row_attrs[row_attrib]), axis=1)

                for col_attrib in ds.ca.keys():
                    if col_attrib not in col_attrs:
                        col_attrs[col_attrib] = np.array([])

                    if col_attrib=='cell_names':
                        renamed_cell_names = np.array([ x + "-" + str(i) for x in  ds.ca['cell_names']])
                        col_attrs[col_attrib] = np.concatenate((col_attrs[col_attrib],  renamed_cell_names))
                    else:
                        col_attrs[col_attrib] = np.concatenate((col_attrs[col_attrib],  ds.ca[col_attrib]))

                newcoo = ds.sparse()
                data = np.concatenate((data, newcoo.data))
                col = np.concatenate((col, newcoo.col+n_cols))
                row = np.concatenate((row, newcoo.row))
                n_rows = ds.shape[0]
                n_cols = n_cols + ds.shape[1]

        # create a coo matrix to create a loom file
        coo_matrix = sparse.coo_matrix((data, (row, col)), shape=(n_rows, n_cols))
        loompy.create(self.output_loom_file, coo_matrix, row_attrs, col_attrs)

        # add the global atributes to the loom file
        ds = loompy.connect(self.output_loom_file)
        ds.attrs[
            "library_preparation_protocol.library_construction_approach"
        ] = self.library
        ds.attrs["donor_organism.genus_species"] = self.species
        ds.attrs["specimen_from_organism.organ"] = self.organ
        ds.attrs["project.provenance.document_id"] = self.project_id
        ds.attrs["project.project_core.project_name"] = self.project_name
        ds.attrs["expression_data_type"] = ", ".join(set(expression_data_type_list))
        ds.attrs["optimus_output_schema_version"] = ", ".join(
            set(optimus_output_schema_version_list)
        )
        ds.attrs["pipeline_version"] = ", ".join(set(pipeline_versions_list))
        ds.attrs["input_id_metadata_field"] = ", ".join(
            set(input_id_metadata_field_list)
        )
        ds.attrs["input_name_metadata_field"] = ", ".join(
            set(input_name_metadata_field_list)
        )
        ds.attrs["input_id"] = ", ".join(input_id_list)
        ds.attrs["input_name"] = ", ".join(input_name_list)

        ds.close()


def main():
    description = """Combine library level loom files into a single project level loom and add global metadata.
    Cell barcodes from separate libraries are suffixed with a number to avoid collisions."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--input-loom-files',
        dest='input_loom_files',
        nargs="+",
        required=True,
        help="Paths to input loom files",
    )
    parser.add_argument(
        '--library',
        dest='library',
        nargs="+",
        required=True,
        help="Library metadata string",
    )
    parser.add_argument(
        '--species',
        dest='species',
        nargs="+",
        required=True,
        help="Species metadata string",
    )
    parser.add_argument(
        '--organ', dest='organ', nargs="+", required=True, help="Organ metadata string"
    )
    parser.add_argument(
        '--project-id', dest='project_id', required=True, help="Project ID"
    )
    parser.add_argument(
        '--project-name', dest='project_name', required=True, help="Project Name"
    )
    parser.add_argument(
        '--min-umis', dest='min_umis', required=False, type=int,  default=100, help="Minium number of UMIs (n_molecules) to keep the cell"
    )
    parser.add_argument(
        '--output-loom-file',
        dest='output_loom_file',
        required=True,
        help="Path to output loom file",
    )

    args = parser.parse_args()

    MergeLooms(
        args.input_loom_files,
        args.library,
        args.species,
        args.organ,
        args.project_id,
        args.project_name,
        args.min_umis,
        args.output_loom_file,
    )


if __name__ == '__main__':
    main()
