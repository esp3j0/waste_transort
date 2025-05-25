from app.crud.base import CRUDBase
from app.crud.crud_user import user
from app.crud.crud_property_company import property_company
from app.crud.crud_property_manager import property_manager
from app.crud.crud_community import community
from app.crud.crud_address import address
from app.crud.crud_order import order

# Old transport and recycling (commented out or removed if already done)
# from app.crud.crud_transport import transport # Assuming this was deleted
# from app.crud.crud_recycling_company import recycling_company # Renamed from crud_recycling

# New Transport CRUDs
from .crud_transport_company import transport_company
from .crud_transport_manager import transport_manager
from .crud_vehicle import vehicle

# New Recycling CRUDs (if not already adjusted from previous step)
from .crud_recycling_company import recycling_company # This was likely already renamed in a previous step
from .crud_recycling_manager import recycling_manager

# New Waste Record CRUD
from .crud_waste_record import waste_record
from .crud_payment import payment

# Make sure all CRUDBase instances are exported if needed or just imported for use in APIs
__all__ = [
    "user", 
    "property_company",
    "property_manager", 
    "community", 
    "address", 
    "order", 
    "transport_company", 
    "transport_manager", 
    "vehicle",
    "recycling_company",
    "recycling_manager",
    "waste_record",
    "payment"
]
