#!/usr/bin/env python3
# thoth-python
# Copyright(C) 2018, 2019 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# type: ignore

"""Tests for package index handling - package source control."""

import os
import json
import typing

from pathlib import Path

import pytest
import requests

from flexmock import flexmock

from thoth.python.aiosource import AIOSource, AsyncIterablePackages, AsyncIterableVersions
from thoth.python.artifact import Artifact

from .base import PythonTestCase

import tempfile

from zipfile import ZipFile


class TestAIOSource(PythonTestCase):
    @pytest.mark.online
    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_default_warehouse(self):
        source_info = {
            "url": "https://index-aicoe.a3c1.starter-us-west-1.openshiftapps.com/",
            "verify_ssl": True,
            "name": "redhat-aicoe-experiments",
        }

        source = AIOSource.from_dict(source_info)
        assert source.warehouse is False, "Default warehouse configuration is not implicitly set to False"

    @pytest.mark.online
    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_get_packages(self):
        source_info = {
            "name": "my-pypi",
            "url": "https://tensorflow.pypi.thoth-station.ninja/index/manylinux2010/AVX2/simple",
            "verify_ssl": True,
            "warehouse": True,
        }

        source = AIOSource.from_dict(source_info)
        assert source.get_package_hashes("tensorflow", "2.0.0") == [
            {
                "name": "tensorflow-2.0.0-cp36-cp36m-linux_x86_64.whl",
                "sha256": "9a62e16ea9dc730d006e1271231f318ee2dad48d145fd3b9e902a925ea3cca2e",
            }
        ]

    @pytest.mark.online
    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_get_packages(self):
        source_info = {
            "name": "my-pypi",
            "url": "https://tensorflow.pypi.thoth-station.ninja/index/manylinux2010/AVX2/simple",
            "verify_ssl": True,
            "warehouse": True,
        }

        source = AIOSource.from_dict(source_info)

        package_name_iterator = await source.get_packages()

        assert type(package_name_iterator) is AsyncIterablePackages

        async for package_name in package_name_iterator:
            assert package_name in ["tensorflow-serving-api", "tensorflow-cpu", "tensorflow-gpu", "tensorflow"]

    @pytest.mark.online
    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_get_package_hashes_warehouse(self):
        pypi_index = {"name": "pypi", "url": "https://pypi.python.org/simple", "verify_ssl": True, "warehouse": True}

        source = AIOSource.from_dict(pypi_index)
        hashes = await source.get_package_hashes("selinon", "1.0.0")
        assert type(hashes) is list

        for actual in hashes:
            assert actual in [
                {
                    "name": "selinon-1.0.0-py3-none-any.whl",
                    "sha256": "9a62e16ea9dc730d006e1271231f318ee2dad48d145fd3b9e902a925ea3cca2e",
                },
                {
                    "name": "selinon-1.0.0.tar.gz",
                    "sha256": "392ab7d2ff1430417a50327515538cec3e9f302b7513dc8e8474745a1b28187a",
                },
            ]

    @pytest.mark.online
    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_get_package_versions_warehouse(self):
        source_info = {"name": "my-pypi", "url": "https://pypi.org/simple", "verify_ssl": True, "warehouse": True}

        source = AIOSource.from_dict(source_info)
        versions = await source.get_package_versions("selinon")

        async for version in versions:
            if version == "1.1.0":
                return True

        return False

    @pytest.mark.online
    @pytest.mark.timeout(120)
    @pytest.mark.asyncio
    async def test_get_package_versions_simple(self):
        source_info = {"name": "my-pypi", "url": "https://pypi.org/simple", "verify_ssl": True, "warehouse": False}

        source = AIOSource.from_dict(source_info)
        versions = await source.get_package_versions("tensorflow")

        async for version in versions:
            if version == "2.0.0":
                return True

        return False
