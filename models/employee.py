# Model untuk tabel Employee
from database import get_db_connection
from . import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employee'
    id_karyawan = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    face_encoding = db.Column(db.LargeBinary)  # Menggunakan LargeBinary untuk BYTEA
    photo = db.Column(db.ARRAY(db.Text))  # Menggunakan ARRAY untuk tekstual array
    status = db.Column(db.CHAR(1), default='A', nullable=False)
    tgl_create = db.Column(db.DateTime, default=datetime.utcnow)
    create_by = db.Column(db.String)
    tgl_update = db.Column(db.DateTime)
    update_by = db.Column(db.String)
    tgl_delete = db.Column(db.DateTime)
    delete_by = db.Column(db.String)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
