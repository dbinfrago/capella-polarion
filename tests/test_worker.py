# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from unittest import mock

import capellambse
import pytest

from capella2polarion.connectors import polarion_worker
from capella2polarion.data_model import work_items
from capella2polarion.elements import converter_config, data_session


def test_polarion_worker_non_delete_mode():
    with mock.patch.object(
        polarion_worker.CapellaPolarionWorker, "check_client"
    ):
        worker = polarion_worker.CapellaPolarionWorker(
            polarion_worker.PolarionWorkerParams(
                project_id="TEST",
                url="http://127.0.0.1",
                pat="PrivateAccessToken",
                delete_work_items=False,
            )
        )
    assert worker.project_client.work_items.delete_status == "deleted"


def test_polarion_worker_delete_mode():
    with mock.patch.object(
        polarion_worker.CapellaPolarionWorker, "check_client"
    ):
        worker = polarion_worker.CapellaPolarionWorker(
            polarion_worker.PolarionWorkerParams(
                project_id="TEST",
                url="http://127.0.0.1",
                pat="PrivateAccessToken",
                delete_work_items=True,
            )
        )
    assert worker.project_client.work_items.delete_status is None


@pytest.mark.asyncio
async def test_polarion_worker_reuse_deleted_work_item(
    model: capellambse.MelodyModel,
    empty_polarion_worker: polarion_worker.CapellaPolarionWorker,
):
    new_work_item = work_items.CapellaWorkItem(
        "ID", title="Test", status="open", uuid_capella="123", type="test"
    )
    old_work_item = work_items.CapellaWorkItem(
        "ID",
        status="deleted",
        type="test",
        uuid_capella="123",
        checksum=new_work_item.calculate_checksum(),
    )
    empty_polarion_worker.polarion_data_repo.update_work_items([old_work_item])
    empty_polarion_worker.project_client.work_items.async_get = mock.AsyncMock(
        return_value=old_work_item
    )
    empty_polarion_worker.project_client.work_items.async_update = (
        mock.AsyncMock()
    )
    empty_polarion_worker.project_client.work_items.delete_status = "deleted"
    empty_polarion_worker.project_client.work_items.attachments.async_get_all = mock.AsyncMock(
        return_value=[]
    )

    await empty_polarion_worker.compare_and_update_work_items(
        {
            "123": data_session.ConverterData(
                "la",
                converter_config.CapellaTypeConfig("test"),
                model.la.extensions.create("FakeModelObject", uuid="123"),
                new_work_item,
            )
        }
    )
    assert (
        empty_polarion_worker.project_client.work_items.async_update.call_count
        == 1
    )


@pytest.mark.asyncio
async def test_compare_and_update_work_items_with_parallelization(
    model: capellambse.MelodyModel,
    empty_polarion_worker: polarion_worker.CapellaPolarionWorker,
):
    num_work_items = 10
    converter_session = {}
    old_work_items = []

    for i in range(num_work_items):
        uuid = f"uuid-{i}"
        new_work_item = work_items.CapellaWorkItem(
            id=f"WI-{i}",
            title=f"Test Work Item {i}",
            status="open",
            uuid_capella=uuid,
            type="test",
        )
        old_work_item = work_items.CapellaWorkItem(
            id=f"WI-{i}",
            status="open",
            type="test",
            uuid_capella=uuid,
            checksum='{"__C2P__WORK_ITEM": "old_checksum_value"}',
        )
        old_work_items.append(old_work_item)
        empty_polarion_worker.polarion_data_repo.update_work_items(
            [old_work_item]
        )
        converter_session[uuid] = data_session.ConverterData(
            "la",
            converter_config.CapellaTypeConfig("test"),
            model.la.extensions.create("FakeModelObject", uuid=uuid),
            new_work_item,
        )

    async def async_get_side_effect(work_item_id, work_item_cls=None):  # noqa: ARG001
        for wi in old_work_items:
            if wi.id == work_item_id:
                return wi
        return old_work_items[0]

    empty_polarion_worker.project_client.work_items.async_get = mock.AsyncMock(
        side_effect=async_get_side_effect
    )
    empty_polarion_worker.project_client.work_items.async_update = (
        mock.AsyncMock()
    )
    empty_polarion_worker.project_client.work_items.attachments.async_get_all = mock.AsyncMock(
        return_value=[]
    )
    empty_polarion_worker.project_client.work_items.links.async_get_all = (
        mock.AsyncMock(return_value=[])
    )
    empty_polarion_worker.max_workers = 4

    await empty_polarion_worker.compare_and_update_work_items(
        converter_session
    )
    assert (
        empty_polarion_worker.project_client.work_items.async_update.call_count
        == num_work_items
    )
