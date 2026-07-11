# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT
"""Grain engine — the pure workflow reducer and the store port (P37-T14 onward).

Deliberately NOT imported by `grain/__init__.py` or any CLI module: the engine is a library
for drivers (grain recipe runner, Diwa Missions executor), never part of startup.
"""
