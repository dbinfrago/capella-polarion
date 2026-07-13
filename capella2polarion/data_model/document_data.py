# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Module providing data classes for documents."""

from __future__ import annotations

import dataclasses

__all__ = ["DocumentInfo"]


@dataclasses.dataclass
class DocumentInfo:
    """Class for information regarding a document which should be created."""

    project_id: str | None
    doc_type: str | None
    module_folder: str
    module_name: str
    text_work_item_type: str
    text_work_item_id_field: str
