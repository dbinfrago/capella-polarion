# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""A capella2polarion-specific adapter over Polarion's generic renderer."""

from __future__ import annotations

import logging
import typing as t

import capellambse
from capellambse import model as m
from polarion_rest_api_client import document_rendering as pdr

from capella2polarion.connectors import polarion_repo

AREA_END_CLS = "c2pAreaEnd"
"""This class is expected for a div in a wiki macro to end a rendering area in
mixed authority documents."""

AREA_START_CLS = "c2pAreaStart"
"""This class is expected for a div in a wiki macro to start a rendering area
in mixed authority documents."""

logger = logging.getLogger(__name__)


class DocumentRenderer(pdr.DocumentRenderer):
    """Render documents using the shared Polarion API client renderer."""

    def __init__(
        self,
        polarion_repository: polarion_repo.PolarionDataRepository,
        model: capellambse.MelodyModel,
        model_work_item_project_id: str,
    ) -> None:
        self.polarion_repository = polarion_repository
        self.model = model
        self.model_work_item_project_id = model_work_item_project_id
        super().__init__(
            default_project_id=model_work_item_project_id,
            area_start_class=AREA_START_CLS,
            area_end_class=AREA_END_CLS,
        )

    def get_template_context(self) -> dict[str, t.Any]:
        """Return model as additional template context."""
        return {"model": self.model}

    def resolve_work_item(
        self,
        obj: object,
        work_item_id: str | None = None,
    ) -> pdr.document_renderer.WorkItemLookupResult:
        """Resolve Capella elements; delegate all other inputs to base."""
        if isinstance(obj, m.ElementList):
            raise TypeError("Cannot make an href to a list of elements")
        if not isinstance(obj, m.ModelElement | m.AbstractDiagram):
            if work_item_id is not None:
                return super().resolve_work_item(
                    t.cast(str, obj), work_item_id
                )
            return super().resolve_work_item(obj)

        if wi := self.polarion_repository.get_work_item_by_capella_uuid(
            obj.uuid
        ):
            return self.model_work_item_project_id, wi

        return None, None
