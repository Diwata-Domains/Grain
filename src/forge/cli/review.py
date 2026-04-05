import click


@click.group("review")
def review_group():
    """Support acceptance, handoff, and completion workflows."""


@review_group.command("check")
def review_check():
    """Run review-oriented validation on a packet."""


@review_group.command("handoff")
def review_handoff():
    """Generate or validate handoff artifacts."""


@review_group.command("summary")
def review_summary():
    """Produce a structured summary of packet state for final inspection."""
