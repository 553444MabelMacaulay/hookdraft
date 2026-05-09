"""Central route registration for hookdraft."""

from hookdraft.routes.diff_routes import register_diff_routes
from hookdraft.routes.replay_routes import register_replay_routes
from hookdraft.routes.export_routes import register_export_routes
from hookdraft.routes.search_routes import register_search_routes
from hookdraft.routes.stats_routes import register_stats_routes
from hookdraft.routes.tag_routes import register_tag_routes
from hookdraft.routes.notes_routes import register_notes_routes
from hookdraft.routes.pin_routes import register_pin_routes
from hookdraft.routes.bookmark_routes import register_bookmark_routes
from hookdraft.routes.label_routes import register_label_routes
from hookdraft.routes.severity_routes import register_severity_routes
from hookdraft.routes.flag_routes import register_flag_routes
from hookdraft.routes.archive_routes import register_archive_routes
from hookdraft.routes.expiry_routes import register_expiry_routes
from hookdraft.routes.grouping_routes import register_grouping_routes
from hookdraft.routes.snapshot_routes import register_snapshot_routes
from hookdraft.routes.trace_routes import register_trace_routes
from hookdraft.routes.throttle_routes import register_throttle_routes
from hookdraft.routes.routing_routes import register_routing_routes
from hookdraft.routes.priority_routes import register_priority_routes
from hookdraft.routes.lock_routes import register_lock_routes
from hookdraft.routes.mention_routes import register_mention_routes
from hookdraft.routes.annotation_routes import register_annotation_routes


def register_all_routes(app):
    register_diff_routes(app)
    register_replay_routes(app)
    register_export_routes(app)
    register_search_routes(app)
    register_stats_routes(app)
    register_tag_routes(app)
    register_notes_routes(app)
    register_pin_routes(app)
    register_bookmark_routes(app)
    register_label_routes(app)
    register_severity_routes(app)
    register_flag_routes(app)
    register_archive_routes(app)
    register_expiry_routes(app)
    register_grouping_routes(app)
    register_snapshot_routes(app)
    register_trace_routes(app)
    register_throttle_routes(app)
    register_routing_routes(app)
    register_priority_routes(app)
    register_lock_routes(app)
    register_mention_routes(app)
    register_annotation_routes(app)
