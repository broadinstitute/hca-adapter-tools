import base64
import json
import logging
import uuid
from functools import (
    cached_property,
    lru_cache,
)
from typing import (
    MutableMapping,
    MutableSequence,
    Optional,
    Tuple,
    TypeVar,
)
from urllib import (
    parse,
)

import google.cloud.storage as gcs
import requests
from jsonschema import (
    FormatChecker,
    validate,
)
from more_itertools import (
    one,
)

T = TypeVar('T')
JSON = MutableMapping[str, T]

log = logging.getLogger(__name__)

staging_area_properties_schema = {
    '$schema': 'https://json-schema.org/draft/2019-09/schema',
    'properties': {
        'is_delta': {
            'type': 'boolean'
        }
    },
    'required': [
        'is_delta'
    ],
    'additionalProperties': False
}


class StagingAreaValidator:

    def main(self):
        self._run()
        exit_code = 0
        for file_name, e in self.file_errors.items():
            log.error('Error with file: %s', file_name, exc_info=e)
        for file_name in self.extra_files:
            log.warning('File is not part of a subgraph: %s', file_name)
        if self.file_errors:
            exit_code |= 1
            log.error('Encountered %i files with errors',
                      len(self.file_errors))
        return exit_code

    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(
            self,
            staging_area: str,
            ignore_dangling_inputs: bool,
            validate_json: bool
    ) -> None:
        super().__init__()
        self.staging_area = staging_area
        self.validate_json = validate_json
        self.ignore_dangling_inputs = ignore_dangling_inputs

        self.gcs = gcs.Client()

        # A boolean to tell us if this is a delta or non-delta staging area
        self.is_delta = None
        # A mapping of data file name to metadata id
        self.names_to_id: MutableMapping[str, str] = {}
        # The status of each metadata file checked
        self.metadata_files: MutableMapping[str, JSON] = {}
        # A mapping of file name to validation error
        self.file_errors: MutableMapping[str, Exception] = {}
        # Any files found that are not part of a subgraph link
        self.extra_files: MutableSequence[str] = []
        self.bucket, self.sa_path = self._parse_gcs_url(self.staging_area)

    @cached_property
    def validator(self):
        return SchemaValidator()

    def _parse_gcs_url(self, gcs_url: str) -> Tuple[gcs.Bucket, str]:
        """
        Parse a GCS URL into its Bucket and path components
        """
        split_url = parse.urlsplit(gcs_url)
        if split_url.scheme != 'gs' or not split_url.netloc:
            print('Error: Google Cloud Storage URL must be in gs://<bucket>[/<path>] format')
            exit(1)
        if split_url.path.endswith('/'):
            print('Error: Google Cloud Storage URL must not end with a "/"')
            exit(1)
        if split_url.path:
            path = split_url.path.lstrip('/') + '/'
        else:
            path = ''
        bucket = gcs.Bucket(self.gcs, split_url.netloc)
        return bucket, path

    def _run(self):
        self.file_errors.clear()
        self.validate_staging_area_properties()
        if not self.file_errors:
            self.validate_files('links')
            self.validate_files('metadata')
            self.validate_files('descriptors')
            self.validate_files('data')
            self.check_results()

    def validate_staging_area_properties(self) -> None:
        """
        Verify and parse the staging area properties file.
        """
        print('Checking staging area properties')
        properties_file_path = self.sa_path + 'staging_area.json'
        blob = self.bucket.get_blob(properties_file_path)
        assert isinstance(blob, gcs.Blob), properties_file_path
        file_json = self.download_blob_as_json(blob)
        self.validate_file_json(file_json, blob.name, staging_area_properties_schema)
        self.is_delta = file_json['is_delta']
        assert isinstance(self.is_delta, bool), file_json

    def validate_files(self, path: str) -> None:
        print(f'Checking files in {self.sa_path}{path}')
        validate_file_fn = getattr(self, f'validate_{path}_file')
        for blob in self.bucket.list_blobs(prefix=f'{self.sa_path}{path}'):
            try:
                validate_file_fn(blob)
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                log.error('File error: %s', blob.name)
                self.file_errors[blob.name] = e

    def download_blob_as_json(self, blob: gcs.Blob) -> Optional[JSON]:
        file_json = json.loads(blob.download_as_bytes())
        return file_json

    def validate_links_file(self, blob: gcs.Blob) -> None:
        # Expected syntax: links/{bundle_uuid}_{version}_{project_uuid}.json
        _, _, file_name = blob.name.rpartition('/')
        assert file_name.count('_') == 2
        assert file_name.endswith('.json')
        _, _, project_uuid = file_name[:-5].split('_')
        file_json = self.download_blob_as_json(blob)
        self.validate_file_json(file_json, blob.name)
        for link in file_json['links']:
            link_type = link['link_type']
            if link_type == 'process_link':
                self.add_metadata_file(entity_id=link['process_id'],
                                       entity_type=link['process_type'],
                                       project_uuid=project_uuid,
                                       category='process')
                for category in ('input', 'output', 'protocol'):
                    for entity in link[f'{category}s']:
                        entity_type = entity[f'{category}_type']
                        entity_id = entity[f'{category}_id']
                        self.add_metadata_file(entity_id=entity_id,
                                               entity_type=entity_type,
                                               project_uuid=project_uuid,
                                               category=category)
            elif link_type == 'supplementary_file_link':
                assert link['entity']['entity_type'] == 'project', link['entity']
                assert link['entity']['entity_id'] == project_uuid, link['entity']
                for entity in link['files']:
                    entity_type = entity['file_type']
                    entity_id = entity['file_id']
                    self.add_metadata_file(entity_id=entity_id,
                                           entity_type=entity_type,
                                           project_uuid=project_uuid,
                                           category='supplementary')
        if project_uuid not in self.metadata_files:
            self.add_metadata_file(entity_id=project_uuid,
                                   entity_type='project',
                                   project_uuid=project_uuid,
                                   category='project')

    def add_metadata_file(self,
                          entity_id: str,
                          entity_type: str,
                          project_uuid: str,
                          category: str
                          ) -> None:
        try:
            file = self.metadata_files[entity_id]
        except KeyError:
            self.metadata_files[entity_id] = {
                'name': set(),
                'entity_id': entity_id,
                'entity_type': entity_type,
                'metadata_versions': set(),
                'descriptor_versions': set(),
                'project': {project_uuid},
                'category': {category},
                'found_metadata': False,
            }
        else:
            file['project'].add(project_uuid)
            file['category'].add(category)
        assert self.metadata_files[entity_id]['entity_type'] == entity_type

    def validate_metadata_file(self, blob: gcs.Blob) -> None:
        # Expected syntax: metadata/{metadata_type}/{metadata_id}_{version}.json
        metadata_type, metadata_file = blob.name.split('/')[-2:]
        assert metadata_file.count('_') == 1
        assert metadata_file.endswith('.json')
        metadata_id, metadata_version = metadata_file[:-5].split('_')
        file_json = self.download_blob_as_json(blob)
        self.validate_file_json(file_json, blob.name)
        if provenance := file_json.get('provenance'):
            assert metadata_id == provenance['document_id']
        if metadata_file := self.metadata_files.get(metadata_id):
            metadata_file['name'].add(blob.name)
            metadata_file['metadata_versions'].add(metadata_version)
            metadata_file['found_metadata'] = True
            if metadata_type.endswith('_file'):
                metadata_file['data_file_name'] = file_json['file_core']['file_name']
                metadata_file['found_data_file'] = False
            if metadata_type == 'supplementary_file' and file_json.get('provenance', {}).get('submitter_id'):
                try:
                    self.validate_file_description(file_json.get('file_description'))
                except Exception as e:
                    self.file_errors[blob.name] = e
                    metadata_file['valid_stratification'] = False
                    log.error('Invalid file_description in %s.', blob.name)
                else:
                    metadata_file['valid_stratification'] = True
        else:
            self.extra_files.append(blob.name)

    def validate_file_description(self, file_description: str) -> None:
        if not file_description:
            return
        strata = [
            {
                dimension: values.split(',')
                for dimension, values in (point.split('=')
                                          for point in stratum.split(';'))
            } for stratum in file_description.split('\n')
        ]
        log.debug(strata)
        valid_keys = [
            'genusSpecies',
            'developmentStage',
            'organ',
            'libraryConstructionApproach',
        ]
        for stratum in strata:
            for dimension, values in stratum.items():
                assert dimension in valid_keys, stratum
                assert len(values) > 0, stratum

    def validate_descriptors_file(self, blob: gcs.Blob) -> None:
        # Expected syntax: descriptors/{metadata_type}/{metadata_id}_{version}.json
        metadata_type, descriptor_file = blob.name.split('/')[-2:]
        assert descriptor_file.count('_') == 1
        assert descriptor_file.endswith('.json')

        metadata_id, descriptor_version = descriptor_file[:-5].split('_')
        file_json = self.download_blob_as_json(blob)
        self.validate_file_json(file_json, blob.name)
        file_name = file_json['file_name']
        self.names_to_id[file_name] = metadata_id

        if metadata_file := self.metadata_files.get(metadata_id):
            metadata_file['crc32c'] = file_json['crc32c']
            metadata_versions = metadata_file['metadata_versions']
            assert descriptor_version in metadata_versions, f'Corresponding metadata version for descriptor version {descriptor_version} not found'
            metadata_file['descriptor_versions'].add(descriptor_version)
        else:
            self.extra_files.append(blob.name)

    def validate_data_file(self, blob: gcs.Blob) -> None:
        # Expected syntax: data/{file_path}
        prefix = self.sa_path + 'data/'
        assert blob.name.startswith(prefix)
        file_name = blob.name[len(prefix):]
        metadata_file = None
        if metadata_id := self.names_to_id.get(file_name):
            if metadata_file := self.metadata_files.get(metadata_id):
                metadata_file['found_data_file'] = True
                assert metadata_file['crc32c'] == base64.b64decode(blob.crc32c).hex()
        if metadata_file is None:
            self.extra_files.append(blob.name)

    def validate_file_json(self,
                           file_json: JSON,
                           file_name: str,
                           schema: Optional[JSON] = None
                           ) -> None:
        if self.validate_json:
            print(f'Validating JSON of {file_name}')
            try:
                self.validator.validate_json(file_json, schema)
            except Exception as e:
                log.error('File %s failed json validation.', file_name)
                self.file_errors[file_name] = e

    def check_results(self):
        print('Checking results')
        for metadata_id, metadata_file in self.metadata_files.items():
            try:
                self.check_result(metadata_file)
            except Exception as e:
                log.error('File error: %s', metadata_file)
                self.file_errors[metadata_id] = e
        if not self.file_errors and not self.extra_files:
            print('No errors found')

    def check_result(self, metadata_file):
        if self.ignore_dangling_inputs and metadata_file['category'] == {'input'}:
            pass
        else:
            if not metadata_file['found_metadata']:
                if metadata_file['entity_type'] == 'project':
                    log.warning('A metadata file was not found for project %s',
                                one(metadata_file['project']))
                else:
                    raise Exception('Did not find metadata file', metadata_file)
            if self.is_delta and len(metadata_file['metadata_versions']) > 1:
                raise Exception('Delta staging areas must not contain redundant '
                                'versions of metadata.',
                                metadata_file)
            if metadata_file['entity_type'].endswith('_file'):
                if not metadata_file['descriptor_versions'] == metadata_file['metadata_versions']:
                    raise Exception('Did not find a matching descriptor file', metadata_file)
                if not metadata_file['found_data_file']:
                    raise Exception('Did not find data file', metadata_file)
        try:
            stratification = metadata_file['valid_stratification']
        except KeyError:
            pass
        else:
            if not stratification:
                raise Exception('File has a invalid stratification value', metadata_file)
            else:
                pass

    def validate_uuid(self, value: str) -> None:
        """
        Verify given value is a valid UUID string.
        """
        try:
            uuid.UUID(value)
        except ValueError as e:
            raise ValueError('Invalid uuid value', value) from e


class SchemaValidator:

    @classmethod
    def validate_json(cls,
                      file_json: JSON,
                      schema: Optional[JSON] = None
                      ) -> None:
        if schema is None:
            try:
                schema = cls._download_schema(file_json['describedBy'])
            except json.decoder.JSONDecodeError as e:
                schema_url = file_json['describedBy']
                raise Exception('Failed to parse schema JSON', schema_url) from e
        validate(file_json, schema, format_checker=FormatChecker())

    @classmethod
    @lru_cache
    def _download_schema(cls, schema_url: str) -> JSON:
        log.debug('Downloading schema %s', schema_url)
        response = requests.get(schema_url, allow_redirects=False)
        response.raise_for_status()
        return response.json()