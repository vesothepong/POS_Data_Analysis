"""Pure inventory rules: reorder quantity and stock status (no Django imports)."""

STATUS_OUT = "Out of Stock"
STATUS_LOW = "Low Stock"
STATUS_REORDER = "Need Reorder"
STATUS_OK = "Sufficient Stock"
ALL_STATUSES = [STATUS_OUT, STATUS_LOW, STATUS_REORDER, STATUS_OK]
STATUS_BADGES = {
    STATUS_OUT: "text-bg-danger",
    STATUS_LOW: "text-bg-warning",
    STATUS_REORDER: "text-bg-primary",
    STATUS_OK: "text-bg-success",
}


def reorder_quantity(stock, predicted):
    """Reorder Quantity = Predicted Demand - Current Stock (never negative)."""
    if predicted is None:
        return 0
    return max(0, int(predicted) - int(stock))


def inventory_status(stock, reorder_level, predicted=None):
    """Out of Stock > Low Stock (below reorder level) > Need Reorder (below forecast) > Sufficient."""
    if stock <= 0:
        return STATUS_OUT
    if stock < reorder_level:
        return STATUS_LOW
    if predicted is not None and stock < predicted:
        return STATUS_REORDER
    return STATUS_OK
