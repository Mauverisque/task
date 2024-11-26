from tortoise import fields, models

class Equipment(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32)
    room = fields.ForeignKeyField('models.IndustrialRoom', related_name='equipment')

class Room(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32)
    room_type = fields.CharField(max_length=10)

    class Meta:
        abstract = True

class IndustrialRoom(Room):
    equipment: fields.ReverseRelation[Equipment]
    floor = fields.ForeignKeyField('models.Floor', related_name='industrial_rooms', on_delete=fields.CASCADE)

    async def get_all_equipment(self):
        return await self.equipment.all()

class AuxiliaryRoom(Room):
    floor = fields.ForeignKeyField('models.Floor', related_name='auxiliary_rooms', on_delete=fields.CASCADE)

class OtherRoom(Room):
    floor = fields.ForeignKeyField('models.Floor', related_name='other_rooms')

class Floor(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32)
    building = fields.ForeignKeyField('models.Building', related_name='floors')

    industrial_rooms: fields.ReverseRelation[Room]
    auxiliary_rooms: fields.ReverseRelation[Room]
    other_rooms: fields.ReverseRelation[Room]

    async def get_all_rooms(self):
        return await self.industrial_rooms.all() + await self.auxiliary_rooms.all() + await self.other_rooms.all()
     
class Building(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32)

    floors: fields.ReverseRelation[Floor]
    
    async def get_all_floors(self):
        return await self.floors.all()
        