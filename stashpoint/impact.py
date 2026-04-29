"""Impact analysis for stashes.

Determines which other stashes, groups, profiles, workflows, and dependencies
would be affected if a given stash were deleted or modified.
"""

from dataclasses import dataclass, field
from typing import Optional

from stashpoint.storage import load_stashes
from stashpoint.group import load_groups
from stashpoint.dependency import load_dependencies
from stashpoint.alias import load_aliases
from stashpoint.profile import load_profiles


class StashNotFoundError(Exception):
    """Raised when the target stash does not exist."""


@dataclass
class ImpactReport:
    """Describes the downstream impact of removing or changing a stash."""

    stash_name: str
    dependent_stashes: list[str] = field(default_factory=list)   # stashes that depend on this one
    member_of_groups: list[str] = field(default_factory=list)    # groups containing this stash
    member_of_profiles: list[str] = field(default_factory=list)  # profiles referencing this stash
    aliased_by: list[str] = field(default_factory=list)          # aliases pointing to this stash

    @property
    def total_affected(self) -> int:
        """Total number of affected entities across all categories."""
        return (
            len(self.dependent_stashes)
            + len(self.member_of_groups)
            + len(self.member_of_profiles)
            + len(self.aliased_by)
        )

    @property
    def is_safe_to_delete(self) -> bool:
        """True when no other entity references this stash."""
        return self.total_affected == 0


def analyse_impact(stash_name: str) -> ImpactReport:
    """Return an ImpactReport for *stash_name*.

    Args:
        stash_name: Name of the stash to analyse.

    Returns:
        ImpactReport populated with all discovered references.

    Raises:
        StashNotFoundError: If the stash does not exist.
    """
    stashes = load_stashes()
    if stash_name not in stashes:
        raise StashNotFoundError(f"Stash '{stash_name}' not found.")

    report = ImpactReport(stash_name=stash_name)

    # --- dependency graph: find stashes that list stash_name as a dependency ---
    try:
        deps = load_dependencies()
        for name, dep_list in deps.items():
            if name != stash_name and stash_name in dep_list:
                report.dependent_stashes.append(name)
        report.dependent_stashes.sort()
    except Exception:  # noqa: BLE001  — tolerate missing dependency store
        pass

    # --- groups ---
    try:
        groups = load_groups()
        for group_name, members in groups.items():
            if stash_name in members:
                report.member_of_groups.append(group_name)
        report.member_of_groups.sort()
    except Exception:  # noqa: BLE001
        pass

    # --- profiles ---
    try:
        profiles = load_profiles()
        for profile_name, profile_data in profiles.items():
            stash_list = profile_data if isinstance(profile_data, list) else profile_data.get("stashes", [])
            if stash_name in stash_list:
                report.member_of_profiles.append(profile_name)
        report.member_of_profiles.sort()
    except Exception:  # noqa: BLE001
        pass

    # --- aliases ---
    try:
        aliases = load_aliases()
        for alias_name, target in aliases.items():
            if target == stash_name:
                report.aliased_by.append(alias_name)
        report.aliased_by.sort()
    except Exception:  # noqa: BLE001
        pass

    return report


def format_impact(report: ImpactReport) -> str:
    """Render an ImpactReport as a human-readable string."""
    lines = [f"Impact report for '{report.stash_name}':", ""]

    if report.is_safe_to_delete:
        lines.append("  No references found — safe to delete.")
        return "\n".join(lines)

    if report.dependent_stashes:
        lines.append("  Dependent stashes:")
        for name in report.dependent_stashes:
            lines.append(f"    - {name}")

    if report.member_of_groups:
        lines.append("  Member of groups:")
        for name in report.member_of_groups:
            lines.append(f"    - {name}")

    if report.member_of_profiles:
        lines.append("  Referenced by profiles:")
        for name in report.member_of_profiles:
            lines.append(f"    - {name}")

    if report.aliased_by:
        lines.append("  Aliased by:")
        for name in report.aliased_by:
            lines.append(f"    - {name}")

    lines.append("")
    lines.append(f"  Total affected entities: {report.total_affected}")
    return "\n".join(lines)
