from aiohttp import web
from tortoise import Tortoise
from tortoise import exceptions
from data_model import *
import aiohttp_jinja2
import jinja2
from html import escape

async def init():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["__main__"]}
    )
    await Tortoise.generate_schemas()

# This function renders the web page with data_model's objects
@aiohttp_jinja2.template('web_page.html')
async def web_page(request):
    building_options = "" # Will hold the building options for a dropdown
    data_list = "" # Will hold the html for the list of data_model's objects

    buildings = await Building.all()
    for building in buildings:
        # Always use html.escape funciton on user input for sanitizing
        building_options += f"<option value='{escape(building.name)}'></option>"

        floors = await building.get_all_floors()
        # if any floors exist then the building can be collapsed
        collapsable = "collapsable" if (len(floors) != 0) else ""
        data_list += f"""
        <div class='list b'><li>
        <button class='list_elem {collapsable}' data-item-type='building' data-item-id='{building.id}'>
        {escape(building.name)}</button>
        <div class='content'><ul>
        """

        for floor in floors:
            rooms = await floor.get_all_rooms()
            collapsable = "collapsable" if (len(rooms) != 0) else ""
            data_list += f"""
            <div class='list f'><li>
            <button class='list_elem {collapsable}' data-item-type='floor' data-item-id='{floor.id}'>
            {escape(floor.name)}</button>
            <div class='content'><ul>
            """

            for room in rooms:
                if (room.room_type == "industrial"):
                    equipments = await room.get_all_equipment()
                    collapsable = "collapsable" if (len(equipments) != 0) else ""
                    data_list += f"""
                    <div class='list r'><li>
                    <button class='list_elem {collapsable}' data-item-type='{room.room_type}' data-item-id='{room.id}'>
                    {escape(room.name)} ({room.room_type})</button>
                    <div class='content'><ul>
                    """

                    for equipment in equipments:
                        data_list += f"""
                        <div class='list e'><li>
                        <button class='list_elem' data-item-type='equipment' data-item-id='{equipment.id}'>
                        {escape(equipment.name)}</button>
                        </li></div>
                        """
                else:
                    data_list += f"""
                    <div class='list r'><li>
                    <button class='list_elem' data-item-type='{room.room_type}' data-item-id='{room.id}'>
                    {escape(room.name)} ({room.room_type})</button>
                    <div class='content'><ul>
                    """
                    
                data_list += "</ul></div></li></div>"

            data_list += "</ul></div></li></div>"

        data_list += "</ul></div></li></div>"


    return {'data_list': data_list, 'building_options': building_options}

async def add_item(request):
    data = await request.post() # Holds data from the inpit form

    try:
        building, _ = await Building.get_or_create(name=data.get("building"))

        if (data.get("floor")):
            floor, _ = await Floor.get_or_create(name=data.get("floor"),
                                                 building=building)
            if (data.get("room")):
                if (data.get("room_type") == "auxiliary"):
                    await AuxiliaryRoom.get_or_create(name=data.get("room"),
                                                      room_type=data.get("room_type"),
                                                      floor=floor)
                elif (data.get("room_type") == "other"):
                    await OtherRoom.get_or_create(name=data.get("room"),
                                                  room_type=data.get("room_type"),
                                                  floor=floor)
                else:
                    room, _ = await IndustrialRoom.get_or_create(name=data.get("room"),
                                                                 room_type=data.get("room_type"),
                                                                 floor=floor)
                    if (data.get("equipment")):
                        await Equipment.create(name=data.get("equipment"),
                                               room=room)

        return web.json_response({"status": "success"})

    except exceptions.DoesNotExist:
        return web.json_response({"status": "error", "message": "Item does not exist"})
    
    except exceptions.IntegrityError:
        return web.json_response({"status": "error", "message": "Integrity violation, possibly duplicate entry"})

async def rename_item(request):
    try:
        data = await request.json() # Holds json data from the renameItem request
        item_type = data.get("type")
        item_id = data.get("id")
        new_name = data.get("name")

        if (item_type == "building"):
            item = await Building.get(id=item_id)
        elif (item_type == "floor"):
            item = await Floor.get(id=item_id)
        elif (item_type == "industrial"):
            item = await IndustrialRoom.get(id=item_id)
        elif (item_type == "auxiliary"):
            item = await AuxiliaryRoom.get(id=item_id)
        elif (item_type == "other"):
            item = await OtherRoom.get(id=item_id)
        elif (item_type == "equipment"):
            item = await Equipment.get(id=item_id)

        item.name = new_name
        await item.save()

        return web.json_response({"status": "success"})
                                 
    except exceptions.DoesNotExist:
        return web.json_response({"status": "error", "message": "Item does not exist"})


async def delete_item(request):
    try:
        data = await request.json() # Holds json data from the deleteItem request
        item_type = data.get("type")
        item_id = data.get("id")

        if (item_type == "building"):
            item = await Building.get(id=item_id)
        elif (item_type == "floor"):
            item = await Floor.get(id=item_id)
        elif (item_type == "industrial"):
            item = await IndustrialRoom.get(id=item_id)
        elif (item_type == "auxiliary"):
            item = await AuxiliaryRoom.get(id=item_id)
        elif (item_type == "other"):
            item = await OtherRoom.get(id=item_id)
        elif (item_type == "equipment"):
            item = await Equipment.get(id=item_id)

        await item.delete()

        return web.json_response({"status": "success"})
    
    except exceptions.DoesNotExist:
        return web.json_response({"status": "error", "message": "Item does not exist"})

# Returns the list of floors for a specific building
async def get_floors(request):
    building_name = request.query.get("building_name")

    building = await Building.filter(name=building_name).first()
    if not building:
        return web.json_response({"error": "Building not found"})

    floors = await building.get_all_floors()

    return web.json_response([{"name": floor.name} for floor in floors])

# Returns the list of rooms for a specific floor
async def get_rooms(request):
    floor_name = request.query.get("floor_name")

    floor = await Floor.filter(name=floor_name).first()

    if not floor:
        return web.json_response({"error": "Floor not found"})
    
    rooms = await floor.get_all_rooms()

    return web.json_response([{"name": room.name} for room in rooms])

async def cleanup(app):
    print("Shutting down the server...")
    await Tortoise.close_connections()

async def start_server():
    app = web.Application()

    # Set up the jinja2 engine to fetch html forms from the templates folder
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

    app.add_routes([
        web.get("/", web_page),
        web.post("/add_item", add_item),
        web.post("/rename_item", rename_item),
        web.post("/delete_item", delete_item),
        web.get("/get_floors", get_floors),
        web.get("/get_rooms", get_rooms),
    ])
    app.on_cleanup.append(cleanup) # Call the cleanup function on shutdown

    await init()

    return app

if __name__ == "__main__":
    try:
        app = start_server()
        web.run_app(app)

    except Exception as e:
        print(f"Error occurred: {e}")
