from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# We'll import db from a separate file to avoid circular imports
from extensions import db

# --- Multi-Tenancy: Company Model ---
class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    users = db.relationship('User', backref='company', lazy=True)
    equipment = db.relationship('Equipment', backref='company', lazy=True)
    work_orders = db.relationship('WorkOrder', backref='company', lazy=True)
    locations = db.relationship('Location', backref='company', lazy=True)
    teams = db.relationship('Team', backref='company', lazy=True)
    roles = db.relationship('Role', backref='company', lazy=True)
    categories = db.relationship('Category', backref='company', lazy=True)
    # inventory_items relationship removed to avoid backref conflict
    # Add more as needed

# --- Category Management Model ---
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'equipment' or 'inventory'
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#007bff')  # Hex color code
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add unique constraint for name and type within company
    __table_args__ = (db.UniqueConstraint('company_id', 'name', 'type', name='uq_category_company_name_type'),)
    
    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'color': self.color,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# --- Role Management Model ---
class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.Text)  # JSON string for permissions
    is_system_role = db.Column(db.Boolean, default=False)  # System roles cannot be deleted
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='role_info', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'permissions': self.permissions,
            'is_system_role': self.is_system_role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='technician')  # Keep for backward compatibility
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # New role relationship
    phone = db.Column(db.String(20))
    department = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    password_reset_required = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    google_id = db.Column(db.String(255), unique=True, nullable=True)  # For Google OAuth
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))  # New location relationship
    
    # Relationships - specify foreign_keys to avoid ambiguity
    assigned_work_orders = db.relationship('WorkOrder', 
                                         backref='assigned_technician', 
                                         lazy=True,
                                         foreign_keys='WorkOrder.assigned_technician_id')
    created_work_orders = db.relationship('WorkOrder', 
                                        backref='created_by', 
                                        lazy=True, 
                                        foreign_keys='WorkOrder.created_by_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def generate_random_password(length=12):
        import random
        import string
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(length))
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'phone': self.phone,
            'department': self.department,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'password_reset_required': self.password_reset_required,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    equipment_id = db.Column(db.String(50), unique=True, nullable=False)  # Asset tag/ID
    category = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # Equipment type for admin filtering
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    location = db.Column(db.String(200))  # Keep for backward compatibility
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))  # New location relationship
    department = db.Column(db.String(100))  # Keep for backward compatibility
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))  # New department relationship
    tags = db.Column(db.Text)  # Comma-separated tags for filtering
    purchase_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    status = db.Column(db.String(20), default='operational')  # operational, maintenance, offline, out_of_service
    criticality = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    description = db.Column(db.Text)
    specifications = db.Column(db.Text)
    last_maintenance_date = db.Column(db.DateTime)  # Last maintenance performed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by = db.relationship('User', backref=db.backref('created_equipment', lazy=True))
    
    # Relationships
    work_orders = db.relationship('WorkOrder', backref='equipment', lazy=True)
    maintenance_schedules = db.relationship('MaintenanceSchedule', backref='equipment', lazy=True)
    
    def __repr__(self):
        return f'<Equipment {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'equipment_id': self.equipment_id,
            'category': self.category,
            'type': self.type,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'serial_number': self.serial_number,
            'location': self.location,
            'location_name': self.location_info.name if self.location_info else None,
            'department': self.department,
            'tags': self.tags,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'warranty_expiry': self.warranty_expiry.isoformat() if self.warranty_expiry else None,
            'status': self.status,
            'criticality': self.criticality,
            'description': self.description,
            'specifications': self.specifications,
            'last_maintenance_date': self.last_maintenance_date.isoformat() if self.last_maintenance_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by_id': self.created_by_id,
            'created_by_name': f"{self.created_by.first_name} {self.created_by.last_name}" if self.created_by else None
        }

class WorkOrder(db.Model):
    __tablename__ = 'work_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    work_order_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='open')  # open, in_progress, completed, cancelled
    type = db.Column(db.String(20), default='corrective')  # corrective, preventive, emergency
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))  # New: Direct location assignment
    assigned_technician_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))  # New: Team assignment
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scheduled_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)  # New: Due date field
    estimated_duration = db.Column(db.Integer)  # in minutes
    actual_duration = db.Column(db.Integer)  # in minutes
    actual_start_time = db.Column(db.DateTime)
    actual_end_time = db.Column(db.DateTime)
    completion_notes = db.Column(db.Text)
    images = db.Column(db.Text)  # Store image file paths as JSON
    videos = db.Column(db.Text)  # Store video file paths as JSON
    voice_notes = db.Column(db.Text)  # Store voice note file paths as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    location = db.relationship('Location', backref='work_orders')
    assigned_team = db.relationship('Team', backref='assigned_work_orders')
    comments = db.relationship('WorkOrderComment', backref='work_order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<WorkOrder {self.work_order_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'work_order_number': self.work_order_number,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'type': self.type,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment.name if self.equipment else None,
            'location_id': self.location_id,
            'location_name': self.location.name if self.location else None,
            'assigned_technician_id': self.assigned_technician_id,
            'assigned_technician_name': f"{self.assigned_technician.first_name} {self.assigned_technician.last_name}" if self.assigned_technician else None,
            'assigned_team_id': self.assigned_team_id,
            'assigned_team_name': self.assigned_team.name if self.assigned_team else None,
            'created_by_id': self.created_by_id,
            'created_by_name': f"{self.created_by.first_name} {self.created_by.last_name}" if self.created_by else None,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'actual_start_time': self.actual_start_time.isoformat() if self.actual_start_time else None,
            'actual_end_time': self.actual_end_time.isoformat() if self.actual_end_time else None,
            'completion_notes': self.completion_notes,
            'images': self.images,
            'videos': self.videos,
            'voice_notes': self.voice_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class MaintenanceSchedule(db.Model):
    __tablename__ = 'maintenance_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    schedule_type = db.Column(db.String(20), default='calendar')  # calendar, runtime, condition
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, yearly
    frequency_value = db.Column(db.Integer, default=1)  # every X days/weeks/months/years
    description = db.Column(db.Text, nullable=False)
    estimated_duration = db.Column(db.Integer)  # in minutes
    is_active = db.Column(db.Boolean, default=True)
    last_performed = db.Column(db.DateTime)
    next_due = db.Column(db.DateTime)
    sop_id = db.Column(db.Integer, db.ForeignKey('sops.id'))  # Link to SOP
    assigned_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))  # Assign to team
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sop = db.relationship('SOP', backref='maintenance_schedules')
    assigned_team = db.relationship('Team', backref='assigned_maintenance_schedules')
    
    def __repr__(self):
        return f'<MaintenanceSchedule {self.equipment.name if self.equipment else "Unknown"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment.name if self.equipment else None,
            'schedule_type': self.schedule_type,
            'frequency': self.frequency,
            'frequency_value': self.frequency_value,
            'description': self.description,
            'estimated_duration': self.estimated_duration,
            'is_active': self.is_active,
            'last_performed': self.last_performed.isoformat() if self.last_performed else None,
            'next_due': self.next_due.isoformat() if self.next_due else None,
            'sop_id': self.sop_id,
            'sop_name': self.sop.name if self.sop else None,
            'assigned_team_id': self.assigned_team_id,
            'assigned_team_name': self.assigned_team.name if self.assigned_team else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SOP(db.Model):
    __tablename__ = 'sops'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))  # PM, Safety, Operation, etc.
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    estimated_duration = db.Column(db.Integer)  # in minutes
    safety_notes = db.Column(db.Text)
    required_tools = db.Column(db.Text)
    required_parts = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    equipment = db.relationship('Equipment', backref='sops')
    created_by = db.relationship('User', backref='created_sops')
    checklist_items = db.relationship('SOPChecklistItem', backref='sop', cascade='all, delete-orphan', order_by='SOPChecklistItem.order', lazy='select')
    
    def __repr__(self):
        return f'<SOP {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment.name if self.equipment else None,
            'estimated_duration': self.estimated_duration,
            'safety_notes': self.safety_notes,
            'required_tools': self.required_tools,
            'required_parts': self.required_parts,
            'is_active': self.is_active,
            'created_by_id': self.created_by_id,
            'created_by_name': f"{self.created_by.first_name} {self.created_by.last_name}" if self.created_by else None,
            'checklist_items': [item.to_dict() for item in self.checklist_items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SOPChecklistItem(db.Model):
    __tablename__ = 'sop_checklist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sop_id = db.Column(db.Integer, db.ForeignKey('sops.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    is_required = db.Column(db.Boolean, default=True)
    expected_result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    company = db.relationship('Company', backref='sop_checklist_items')
    
    def __repr__(self):
        return f'<SOPChecklistItem {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sop_id': self.sop_id,
            'company_id': self.company_id,
            'description': self.description,
            'order': self.order,
            'is_required': self.is_required,
            'expected_result': self.expected_result,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WorkOrderChecklist(db.Model):
    __tablename__ = 'work_order_checklists'
    
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    sop_checklist_item_id = db.Column(db.Integer, db.ForeignKey('sop_checklist_items.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    work_order = db.relationship('WorkOrder', backref='checklist_items')
    sop_checklist_item = db.relationship('SOPChecklistItem', backref='work_order_checklists')
    completed_by = db.relationship('User', backref='completed_checklist_items')
    company = db.relationship('Company', backref='work_order_checklists')
    
    def __repr__(self):
        return f'<WorkOrderChecklist {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'work_order_id': self.work_order_id,
            'sop_checklist_item_id': self.sop_checklist_item_id,
            'company_id': self.company_id,
            'is_completed': self.is_completed,
            'completed_by_id': self.completed_by_id,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    part_number = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    unit_cost = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='USD')  # ISO 4217 currency code
    current_stock = db.Column(db.Integer, default=0)
    minimum_stock = db.Column(db.Integer, default=0)
    maximum_stock = db.Column(db.Integer)
    unit_of_measure = db.Column(db.String(20), default='pieces')
    location = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref=db.backref('inventory_items', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Inventory {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'part_number': self.part_number,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'manufacturer': self.manufacturer,
            'supplier': self.supplier,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'currency': self.currency,
            'current_stock': self.current_stock,
            'minimum_stock': self.minimum_stock,
            'maximum_stock': self.maximum_stock,
            'unit_of_measure': self.unit_of_measure,
            'location': self.location,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class WorkOrderComment(db.Model):
    __tablename__ = 'work_order_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text)  # Store image file paths as JSON
    videos = db.Column(db.Text)  # Store video file paths as JSON
    voice_notes = db.Column(db.Text)  # Store voice note file paths as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='work_order_comments')
    company = db.relationship('Company', backref='work_order_comments')
    
    def __repr__(self):
        return f'<WorkOrderComment {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'work_order_id': self.work_order_id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'comment': self.comment,
            'images': self.images,
            'videos': self.videos,
            'voice_notes': self.voice_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WorkOrderPart(db.Model):
    __tablename__ = 'work_order_parts'
    
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    quantity_used = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    work_order = db.relationship('WorkOrder', backref='parts_used')
    inventory_item = db.relationship('Inventory', backref='work_orders')
    company = db.relationship('Company', backref='work_order_parts')
    
    def __repr__(self):
        return f'<WorkOrderPart {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'work_order_id': self.work_order_id,
            'inventory_id': self.inventory_id,
            'company_id': self.company_id,
            'quantity_used': self.quantity_used,
            'unit_cost': str(self.unit_cost) if self.unit_cost else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False, unique=True)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100), default='USA')
    latitude = db.Column(db.Float)  # For map coordinates
    longitude = db.Column(db.Float)  # For map coordinates
    description = db.Column(db.Text)
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    equipment = db.relationship('Equipment', backref='location_info', lazy=True)
    users = db.relationship('User', backref='location_info', lazy=True)
    
    def __repr__(self):
        return f'<Location {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'description': self.description,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Association table for many-to-many relationship between users and teams
user_teams = db.Table('user_teams',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('teams.id'), primary_key=True)
)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    members = db.relationship('User', secondary=user_teams, backref=db.backref('teams', lazy='select'))
    
    # Add unique constraint for name within company
    __table_args__ = (db.UniqueConstraint('company_id', 'name', name='uq_team_company_name'),)

    def __repr__(self):
        return f'<Team {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'members': [user.id for user in self.members]
        }

# WhatsApp Integration Models
class WhatsAppUser(db.Model):
    __tablename__ = 'whatsapp_users'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    whatsapp_number = db.Column(db.String(20), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    verification_expires = db.Column(db.DateTime)
    preferred_language = db.Column(db.String(10), default='en')  # en, es, hi, ar, etc.
    notification_preferences = db.Column(db.Text)  # JSON string for notification settings
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='whatsapp_users')
    user = db.relationship('User', backref='whatsapp_profile')
    messages = db.relationship('WhatsAppMessage', backref='whatsapp_user', lazy=True)
    
    def __repr__(self):
        return f'<WhatsAppUser {self.whatsapp_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'user_id': self.user_id,
            'whatsapp_number': self.whatsapp_number,
            'is_verified': self.is_verified,
            'preferred_language': self.preferred_language,
            'notification_preferences': self.notification_preferences,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class WhatsAppMessage(db.Model):
    __tablename__ = 'whatsapp_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    whatsapp_user_id = db.Column(db.Integer, db.ForeignKey('whatsapp_users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # text, image, video, audio, document, button
    direction = db.Column(db.String(10), nullable=False)  # inbound, outbound
    content = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(500))  # For media messages
    media_type = db.Column(db.String(20))  # image, video, audio, document
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))  # Link to work order
    maintenance_schedule_id = db.Column(db.Integer, db.ForeignKey('maintenance_schedules.id'))  # Link to maintenance schedule
    template_id = db.Column(db.String(100))  # WhatsApp template ID
    status = db.Column(db.String(20), default='sent')  # sent, delivered, read, failed
    whatsapp_message_id = db.Column(db.String(100))  # WhatsApp's message ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    work_order = db.relationship('WorkOrder', backref='whatsapp_messages')
    maintenance_schedule = db.relationship('MaintenanceSchedule', backref='whatsapp_messages')
    company = db.relationship('Company', backref='whatsapp_messages')
    
    def __repr__(self):
        return f'<WhatsAppMessage {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'whatsapp_user_id': self.whatsapp_user_id,
            'company_id': self.company_id,
            'message_type': self.message_type,
            'direction': self.direction,
            'content': self.content,
            'media_url': self.media_url,
            'media_type': self.media_type,
            'work_order_id': self.work_order_id,
            'maintenance_schedule_id': self.maintenance_schedule_id,
            'template_id': self.template_id,
            'status': self.status,
            'whatsapp_message_id': self.whatsapp_message_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WhatsAppTemplate(db.Model):
    __tablename__ = 'whatsapp_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)  # work_order, maintenance, emergency, general
    template_id = db.Column(db.String(100), nullable=False, unique=True)  # WhatsApp template ID
    language = db.Column(db.String(10), default='en')
    content = db.Column(db.Text, nullable=False)  # Template content with variables
    variables = db.Column(db.Text)  # JSON string of required variables
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='whatsapp_templates')
    
    def __repr__(self):
        return f'<WhatsAppTemplate {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'template_id': self.template_id,
            'language': self.language,
            'content': self.content,
            'variables': self.variables,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class NotificationLog(db.Model):
    __tablename__ = 'notification_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # whatsapp, email, sms
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_whatsapp_id = db.Column(db.Integer, db.ForeignKey('whatsapp_users.id'))
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, sent, delivered, failed
    error_message = db.Column(db.Text)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))
    maintenance_schedule_id = db.Column(db.Integer, db.ForeignKey('maintenance_schedules.id'))
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='notification_logs')
    recipient = db.relationship('User', backref='notifications')
    recipient_whatsapp = db.relationship('WhatsAppUser', backref='notifications')
    work_order = db.relationship('WorkOrder', backref='notifications')
    maintenance_schedule = db.relationship('MaintenanceSchedule', backref='notifications')
    
    def __repr__(self):
        return f'<NotificationLog {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'notification_type': self.notification_type,
            'recipient_id': self.recipient_id,
            'recipient_whatsapp_id': self.recipient_whatsapp_id,
            'subject': self.subject,
            'content': self.content,
            'status': self.status,
            'error_message': self.error_message,
            'work_order_id': self.work_order_id,
            'maintenance_schedule_id': self.maintenance_schedule_id,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'created_at': self.created_at.isoformat()
        }

class EmergencyBroadcast(db.Model):
    __tablename__ = 'emergency_broadcasts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='high')  # low, medium, high, critical
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    sent_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipients = db.Column(db.Text)  # JSON string of recipient IDs or 'all'
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='emergency_broadcasts')
    equipment = db.relationship('Equipment', backref='emergency_broadcasts')
    location = db.relationship('Location', backref='emergency_broadcasts')
    sent_by = db.relationship('User', backref='sent_emergency_broadcasts')
    
    def __repr__(self):
        return f'<EmergencyBroadcast {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'equipment_id': self.equipment_id,
            'location_id': self.location_id,
            'sent_by_id': self.sent_by_id,
            'recipients': self.recipients,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat()
        }

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('company_id', 'name', name='uq_department_company_name'),)

    company = db.relationship('Company', backref='departments')
    equipment = db.relationship('Equipment', backref='department_info', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# --- Vendor Management Models ---
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    location = db.relationship('Location', backref='vendors')  # type: ignore
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contacts = db.relationship('VendorContact', backref='vendor', cascade='all, delete-orphan', lazy=True)  # type: ignore
    files = db.relationship('VendorFile', backref='vendor', cascade='all, delete-orphan', lazy=True)  # type: ignore
    equipment = db.relationship('Equipment', secondary='vendor_equipment', backref='vendors', lazy='dynamic')  # type: ignore
    inventory = db.relationship('Inventory', secondary='vendor_inventory', backref='vendors', lazy='dynamic')  # type: ignore

    def __repr__(self):
        return f'<Vendor {self.name}>'

class VendorContact(db.Model):
    __tablename__ = 'vendor_contacts'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    position = db.Column(db.String(100))
    company = db.relationship('Company', backref='vendor_contacts')
    def __repr__(self):
        return f'<VendorContact {self.id}>'
    def to_dict(self):
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'company_id': self.company_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'position': self.position
        }

class VendorFile(db.Model):
    __tablename__ = 'vendor_files'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    company = db.relationship('Company', backref='vendor_files')
    def __repr__(self):
        return f'<VendorFile {self.id}>'
    def to_dict(self):
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'company_id': self.company_id,
            'filename': self.filename,
            'filepath': self.filepath,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

# Association tables for many-to-many relationships
vendor_equipment = db.Table('vendor_equipment',
    db.Column('vendor_id', db.Integer, db.ForeignKey('vendors.id'), primary_key=True),
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
)
vendor_inventory = db.Table('vendor_inventory',
    db.Column('vendor_id', db.Integer, db.ForeignKey('vendors.id'), primary_key=True),
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'), primary_key=True)
) 