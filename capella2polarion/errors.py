# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Module for Capella-Polarion errors and handling."""

RENDER_ERROR_CHECKSUM = "__RENDER_ERROR__"
"""Marker used as checksum when diagram rendering fails."""
ERROR_IMAGE = b"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200">
  <rect width="400" height="200" fill="#d32f2f"/>
  <text x="200" y="90" text-anchor="middle" fill="white" font-size="24" font-weight="bold">
    Capella2Polarion: Diagram Failed to Render
  </text>
  <text x="200" y="130" text-anchor="middle" fill="white" font-size="18">
    Please contact support for assistance
  </text>
</svg>"""
"""Static SVG image to use when diagram rendering fails."""
