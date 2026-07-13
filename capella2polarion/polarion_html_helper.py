# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Capella2Polarion-specific Polarion HTML helpers."""

from __future__ import annotations

import pathlib
import re

import jinja2
import polarion_rest_api_client as polarion_api
from capellambse import helpers as chelpers
from capellambse import model as m

from capella2polarion import data_model

TEXT_WORK_ITEM_ID_FIELD = "__C2P__id"
"""Custom ID field for text work items created by capella2polarion.

The upstream default is ``__AUTO_RENDER__id``; we use a distinct name
so documents rendered by this tool can be distinguished.
"""

RE_DESCR_DELETED_PATTERN = re.compile(
    f"&lt;deleted element ({chelpers.RE_VALID_UUID.pattern})&gt;"
)


def strike_through(string: str) -> str:
    """Return a striked-through HTML span from ``string``.

    If the string is a ``<deleted element UUID>`` placeholder, the UUID
    itself is shown struck-through instead of the full placeholder text.
    """
    if match := RE_DESCR_DELETED_PATTERN.match(string):
        string = match.group(1)
    return f'<span style="text-decoration: line-through;">{string}</span>'


class JinjaRendererMixin:
    """A MixIn for converters that render Jinja templates for work items."""

    jinja_envs: dict[str, jinja2.Environment]

    def _get_jinja_env(
        self, template_folder: str | pathlib.Path
    ) -> jinja2.Environment:
        template_folder = str(template_folder)
        if env := self.jinja_envs.get(template_folder):
            return env

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_folder)
        )
        self.setup_env(env)

        self.jinja_envs[template_folder] = env
        return env

    def check_model_element(
        self, obj: object
    ) -> m.ModelElement | m.AbstractDiagram | None:
        """Check if a model element was passed.

        Return None if no element and raise a TypeError if a wrong typed
        element was passed. Returns the element if it matches
        expectations.
        """
        if jinja2.is_undefined(obj) or obj is None:
            return None

        if isinstance(obj, m.ElementList):
            raise TypeError("Cannot make an href to a list of elements")
        if not isinstance(obj, m.ModelElement | m.AbstractDiagram):
            raise TypeError(f"Expected a model object, got {obj!r}")
        return obj

    def setup_env(self, env: jinja2.Environment) -> None:
        """Implement this method to adjust a newly created environment."""


def add_attachment_to_workitem(
    work_item: polarion_api.WorkItem,
    attachment: data_model.Capella2PolarionAttachment,
) -> None:
    """Add the attachment to the workitem and add a PNG version if needed."""
    assert attachment.file_name is not None
    attachment.work_item_id = work_item.id or ""
    work_item.attachments.append(attachment)
    if attachment.mime_type == "image/svg+xml":
        work_item.attachments.append(
            data_model.PngConvertedSvgAttachment(attachment)
        )
