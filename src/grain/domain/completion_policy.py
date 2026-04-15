from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CompletionPolicy:
    require_defined_deliverable: bool = True
    require_results_recorded: bool = True
    require_rule_check: bool = True
    require_user_approval: bool = True
    require_verification_pass: bool = False
    allow_close_when_verification_not_run: bool = True
