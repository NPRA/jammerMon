from sqlalchemy import Column, Integer, \
    Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JamTimeseries(Base):
    """
    ORM model that describes and maps the columns in the 'jam_timeseries'
    table with the attributes of this class.

    Used in SQLAlchemy.
    """
    __tablename__ = 'jam_timeseries'

    id = Column(Integer, primary_key=True)
    utc = Column(DateTime, nullable=False)
    indicator = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    gps_ts = Column(DateTime, nullable=False)

    def __init__(self, timestamp_id, jam_ind, utc, lat, lon, gps_ts):
        self.id = timestamp_id
        self.indicator = jam_ind
        self.utc = utc
        self.latitude = lat
        self.longitude = lon
        self.gps_ts = gps_ts

    def __str__(self):
        return "{}(id={}, utc={}, indicator={}, latitude={}, longitude={}, gps_ts={})".format(
            self.__class__, self.utc, self.indicator, self.latitude, self.longitude, self.gps_ts)
