# dg-metadata-manager

A module to convert data retrieved from a specific storage into the format of a specific schema (*).

* A schema that has internal data conforming to NII RDC-AP or its extension, DG-AP.

## Installation

```bash
pip install git+https://github.com/NII-DG/dg-metadata-manager.git
```

## Usage

```python
from dg_mm import MetadataManager

mm = MetadataManager()
metadata = mm.get_metadata('schema name', 'storage name', token='token for storage access', id='storage id')
```

## List of currently available schema names


| Schema Name | Description                           |
| ----------- | ------------------------------------- |
| RF          | Schema used in Research Flow / DG-Web |

## List of currently available storage names

| Storage Name | Description | Required parameters for access |
| ------------ | ----------- | ------------------------------ |
| GRDM         | GakuNin RDM | token, id (specify project ID) |
