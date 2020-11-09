from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from database.base import Base


class Guild(Base):
    id = Column('id', Integer, primary_key=True)
    discord_id = Column('discord_id', BigInteger)
    category = relationship('Category', uselist=False, back_populates='guild')
    name = Column('name', String(length=100))
    auto = Column('auto', Boolean)
    time = Column('time', Integer)


class Category(Base):
    id = Column('id', Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey('guild.id'))
    discord_id = Column('discord_id', BigInteger)
    name = Column('name', String(length=100))
    guild = relationship("Guild", back_populates='category')
    channels = relationship('Channel')


class Channel(Base):
    id = Column('id', Integer, primary_key=True)
    discord_id = Column('discord_id', BigInteger)
    category_id = Column(Integer, ForeignKey('category.id'))
    name = Column('name', String(length=100))
